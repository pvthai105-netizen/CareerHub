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
};

// Tự động kiểm tra và cập nhật Navbar khi trang tải xong
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => AuthGuard.renderNavbar());
} else {
  AuthGuard.renderNavbar();
}
