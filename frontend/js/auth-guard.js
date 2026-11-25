/**
 * Module quản lý phiên đăng nhập và phân quyền trên trình duyệt (Auth Guard)
 */
const AuthGuard = {
  // Giải mã payload của JWT không cần thư viện ngoài
  parseJwt(token) {
    if (!token) return null;
    try {
      const base64Url = token.split(".")[1];
      const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split("")
          .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
          .join("")
      );
      return JSON.parse(jsonPayload);
    } catch (e) {
      return null;
    }
  },

  // Lấy thông tin user hiện tại từ token
  getUser() {
    const token = Auth.getToken();
    if (!token) return null;
    const payload = this.parseJwt(token);
    if (!payload) return null;

    // Kiểm tra thời hạn hết hạn token (exp)
    const now = Math.floor(Date.now() / 1000);
    if (payload.exp && payload.exp < now) {
      Auth.clear();
      return null;
    }

    return {
      id: payload.sub,
      role: payload.role,
      exp: payload.exp,
    };
  },

  // Điều hướng người dùng về trang tương ứng theo vai trò
  redirectByRole(role) {
    switch (role) {
      case "student":
        window.location.href = "home.html"; // Dẫn về trang tìm việc làm (sinh viên đăng nhập)
        break;
      case "employer":
        window.location.href = "employer_dashboard.html"; // Dashboard doanh nghiệp
        break;
      case "admin":
        window.location.href = "admin_dashboard.html"; // Dashboard quản trị viên
        break;
      default:
        window.location.href = "home.html";
    }
  },

  // Hàm chặn truy cập trái quyền (Dùng ở đầu các trang cần bảo vệ)
  // Ví dụ ở trang nhà tuyển dụng: AuthGuard.requireRoles(['employer'])
  requireRoles(allowedRoles = []) {
    const user = this.getUser();

    if (!user) {
      // Chưa đăng nhập hoặc token đã hết hạn
      Auth.clear();
      const currentUrl = encodeURIComponent(window.location.pathname);
      window.location.href = `login.html?expired=1&redirect=${currentUrl}`;
      return null;
    }

    if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
      alert("Bạn không có quyền truy cập vào trang này!");
      window.location.href = "home.html";
      return null;
    }

    return user;
  },

  // Tự động đồng bộ giao diện Navbar với trạng thái đăng nhập (Phương án A)
  renderNavbar() {
    const navActions = document.querySelector(".nav-actions") || document.querySelector(".header-buttons");
    if (!navActions) return;

    const user = this.getUser();
    if (user) {
      let displayName = user.role === "student" ? "Sinh viên" : user.role === "employer" ? "Nhà tuyển dụng" : "Quản trị";
      let initials = user.role === "student" ? "SV" : user.role === "employer" ? "NTD" : "AD";

      // Nếu là sinh viên, lấy tên từ thông tin profile đã lưu nếu có
      if (user.role === "student") {
        try {
          const profile = JSON.parse(localStorage.getItem("careerhub_student_profile") || "{}");
          if (profile.full_name) {
            displayName = profile.full_name;
            const parts = profile.full_name.trim().split(/\s+/);
            if (parts.length >= 2) {
              initials = (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
            } else if (parts.length === 1 && parts[0]) {
              initials = parts[0].slice(0, 2).toUpperCase();
            }
          }
        } catch (_) {}
      }

      const profileUrl = user.role === "student" ? "profile.html" : user.role === "employer" ? "employer_profile.html" : "admin_dashboard.html";

      navActions.innerHTML = `
        <div style="display: inline-flex; align-items: center; gap: 10px;">
          <a href="${profileUrl}" title="Xem hồ sơ cá nhân" style="display: inline-flex; align-items: center; gap: 8px; text-decoration: none; padding: 4px 12px; background: #F2EFF9; border-radius: 9999px; transition: all 0.2s; border: 1px solid #E8E5F0;">
            <span style="width: 26px; height: 26px; border-radius: 50%; background-color: #8176B5; color: #FFFFFF; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700;">
              ${initials}
            </span>
            <span style="font-size: 13px; font-weight: 600; color: #292642; max-width: 140px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
              ${displayName}
            </span>
          </a>
          <button type="button" id="btn-navbar-logout" class="btn btn-outline" style="padding: 7px 16px; font-size: 13px; cursor: pointer;">
            Đăng xuất
          </button>
        </div>
      `;

      const btnLogout = document.getElementById("btn-navbar-logout");
      if (btnLogout) {
        btnLogout.addEventListener("click", () => {
          Auth.clear();
          window.location.href = "login.html?logout=1";
        });
      }
    }
  },

  renderNotificationCenter() {
    if (!this.getUser() || typeof api === "undefined") return;

    const styleId = "notification-center-styles";
    if (!document.getElementById(styleId)) {
      const style = document.createElement("style");
      style.id = styleId;
      style.textContent = `
        .notification-center { position: relative; display: inline-flex; align-items: center; flex: 0 0 auto; }
        .notification-trigger { position: relative; display: inline-flex; align-items: center; justify-content: center; gap: 8px; min-width: 40px; height: 40px; padding: 0 10px; color: #4a4760; background: #fff; border: 1px solid #e8e5f0; border-radius: 9px; cursor: pointer; font: 500 13px Inter, system-ui, sans-serif; }
        .notification-trigger:hover, .notification-trigger[aria-expanded="true"] { background: #f5f2fb; border-color: #b9aedb; }
        .notification-trigger svg { width: 19px; height: 19px; flex: 0 0 auto; }
        .notification-count { position: absolute; top: -7px; right: -7px; min-width: 19px; height: 19px; padding: 0 5px; display: inline-flex; align-items: center; justify-content: center; color: #fff; background: #d94b63; border: 2px solid #fff; border-radius: 999px; font: 700 10px/1 Inter, system-ui, sans-serif; }
        .notification-count[hidden] { display: none; }
        .notification-panel { position: absolute; z-index: 1200; top: calc(100% + 10px); right: 0; width: min(360px, calc(100vw - 32px)); max-height: min(440px, calc(100vh - 100px)); overflow: auto; color: #292642; background: #fff; border: 1px solid #e8e5f0; border-radius: 14px; box-shadow: 0 12px 36px rgba(41, 38, 66, .18); }
        .notification-panel[hidden] { display: none; }
        .notification-panel-header { position: sticky; top: 0; z-index: 1; display: flex; align-items: center; justify-content: space-between; padding: 14px 16px; background: #fff; border-bottom: 1px solid #eeeaf5; }
        .notification-panel-header strong { font-size: 14px; }
        .notification-close { width: 30px; height: 30px; color: #77738b; background: transparent; border: 0; border-radius: 7px; font-size: 21px; cursor: pointer; }
        .notification-close:hover { color: #292642; background: #f5f2fb; }
        .notification-list { padding: 6px; }
        .notification-item { width: 100%; display: block; padding: 11px 12px; color: #292642; text-align: left; background: transparent; border: 0; border-radius: 9px; cursor: pointer; }
        .notification-item:hover { background: #f8f7fc; }
        .notification-item.is-unread { background: #f3f0fb; }
        .notification-item-title { display: block; margin-bottom: 3px; font-size: 13px; font-weight: 650; }
        .notification-item-message { display: block; font-size: 12px; line-height: 1.5; color: #5e5a70; }
        .notification-item-date { display: block; margin-top: 6px; color: #858197; font-size: 11px; }
        .notification-empty, .notification-error { margin: 0; padding: 22px 16px; color: #77738b; text-align: center; font-size: 13px; }
        .notification-error { color: #b54755; }
        @media (max-width: 560px) { .notification-panel { right: -54px; } .notification-trigger .notification-trigger-label { display: none; } }
      `;
      document.head.append(style);
    }

    const bell = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M10 21h4"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/></svg>`;
    const container = document.createElement("div");
    container.className = "notification-center";
    container.innerHTML = `
      <button type="button" class="notification-trigger" aria-label="Thông báo" aria-haspopup="dialog" aria-expanded="false">
        ${bell}<span class="notification-trigger-label">Thông báo</span>
        <span class="notification-count" aria-live="polite" hidden></span>
      </button>
      <section class="notification-panel" role="dialog" aria-label="Thông báo của bạn" hidden>
        <div class="notification-panel-header"><strong>Thông báo</strong><button type="button" class="notification-close" aria-label="Đóng">×</button></div>
        <div class="notification-list" aria-live="polite"><p class="notification-empty">Đang tải thông báo…</p></div>
      </section>`;

    const navActions = document.querySelector(".nav-actions, .header-buttons");
    const dashboardActions = document.querySelector(".dash-topbar-actions");
    const jobPostNotification = document.querySelector(".header-notif");
    const profileActions = document.querySelector(".topbar-right");
    if (navActions) navActions.prepend(container);
    else if (dashboardActions) {
      dashboardActions.querySelector(".dash-icon-btn")?.remove();
      dashboardActions.prepend(container);
    } else if (jobPostNotification) jobPostNotification.replaceWith(container);
    else if (profileActions) profileActions.prepend(container);
    else return;

    const trigger = container.querySelector(".notification-trigger");
    const panel = container.querySelector(".notification-panel");
    const list = container.querySelector(".notification-list");
    const badge = container.querySelector(".notification-count");
    let notifications = [];

    const showMessage = (message, className) => {
      list.replaceChildren();
      const paragraph = document.createElement("p");
      paragraph.className = className;
      paragraph.textContent = message;
      list.append(paragraph);
    };

    const refreshCount = async () => {
      try {
        const result = await api.get("/notifications/unread-count");
        const count = Number(result?.unread_count) || 0;
        badge.textContent = count > 99 ? "99+" : String(count);
        badge.hidden = count === 0;
        trigger.setAttribute("aria-label", count ? `Thông báo, ${count} chưa đọc` : "Thông báo");
      } catch (_) {
        // Lỗi tạm thời không làm gián đoạn phần còn lại của trang.
      }
    };

    const renderList = () => {
      list.replaceChildren();
      if (!notifications.length) {
        showMessage("Bạn chưa có thông báo nào.", "notification-empty");
        return;
      }

      notifications.forEach((notification) => {
        const item = document.createElement("button");
        item.type = "button";
        item.className = `notification-item${notification.is_read ? "" : " is-unread"}`;
        const title = document.createElement("span");
        title.className = "notification-item-title";
        title.textContent = notification.title;
        const message = document.createElement("span");
        message.className = "notification-item-message";
        message.textContent = notification.message;
        const date = document.createElement("span");
        date.className = "notification-item-date";
        const createdAt = new Date(notification.created_at);
        date.textContent = Number.isNaN(createdAt.getTime()) ? "" : createdAt.toLocaleString("vi-VN", { dateStyle: "short", timeStyle: "short" });
        item.append(title, message, date);
        item.setAttribute("aria-label", `${notification.is_read ? "Đã đọc" : "Chưa đọc"}: ${notification.title}. ${notification.message}`);
        item.addEventListener("click", async () => {
          if (!notification.is_read) {
            item.disabled = true;
            try {
              await api.patch(`/notifications/${notification.id}/read`);
              notification.is_read = true;
              await refreshCount();
              renderList();
            } catch (error) {
              showMessage(error.message || "Không thể đánh dấu đã đọc. Vui lòng thử lại.", "notification-error");
            }
          }
        });
        list.append(item);
      });
    };

    const refreshList = async () => {
      showMessage("Đang tải thông báo…", "notification-empty");
      try {
        notifications = await api.get("/notifications?limit=30&offset=0");
        renderList();
      } catch (error) {
        showMessage(error.message || "Không thể tải thông báo. Vui lòng thử lại.", "notification-error");
      }
    };

    trigger.addEventListener("click", async () => {
      const isOpen = !panel.hidden;
      panel.hidden = isOpen;
      trigger.setAttribute("aria-expanded", String(!isOpen));
      if (!isOpen) await refreshList();
    });
    container.querySelector(".notification-close").addEventListener("click", () => {
      panel.hidden = true;
      trigger.setAttribute("aria-expanded", "false");
      trigger.focus();
    });
    document.addEventListener("click", (event) => {
      if (!container.contains(event.target)) {
        panel.hidden = true;
        trigger.setAttribute("aria-expanded", "false");
      }
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !panel.hidden) {
        panel.hidden = true;
        trigger.setAttribute("aria-expanded", "false");
        trigger.focus();
      }
    });

    refreshCount();
    window.setInterval(() => {
      if (document.visibilityState === "visible") {
        refreshCount();
        if (!panel.hidden) refreshList();
      }
    }, 30000);
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible") {
        refreshCount();
        if (!panel.hidden) refreshList();
      }
    });
  },
};

// Tự động kiểm tra và cập nhật Navbar khi trang tải xong
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    AuthGuard.renderNavbar();
    AuthGuard.renderNotificationCenter();
  });
} else {
  AuthGuard.renderNavbar();
  AuthGuard.renderNotificationCenter();
}
