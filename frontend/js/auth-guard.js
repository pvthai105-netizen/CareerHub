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
        window.location.href = "/profile.html"; // Trang sinh viên (hồ sơ sinh viên)
        break;
      case "employer":
        window.location.href = "/job_post.html"; // Trang nhà tuyển dụng (quản lý tin)
        break;
      case "admin":
        window.location.href = "/index.html"; // Hoặc admin.html
        break;
      default:
        window.location.href = "/index.html";
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
      window.location.href = `/login.html?expired=1&redirect=${currentUrl}`;
      return null;
    }

    if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
      alert("Bạn không có quyền truy cập vào trang này!");
      window.location.href = "/index.html";
      return null;
    }

    return user;
  },

  // Tự động đồng bộ giao diện Navbar với trạng thái đăng nhập
  renderNavbar() {
    const navActions = document.querySelector(".nav-actions");
    if (!navActions) return;

    const user = this.getUser();
    if (user) {
      const roleLabel =
        user.role === "student"
          ? "🎓 Sinh viên"
          : user.role === "employer"
          ? "🏢 Nhà tuyển dụng"
          : "Quản trị";

      navActions.innerHTML = `
        <span style="font-size: 13px; font-weight: 600; color: var(--indigo); display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; background: var(--info-bg); border-radius: var(--radius-sm);">
          <span style="width: 8px; height: 8px; border-radius: 50%; background-color: var(--success); display: inline-block;"></span>
          <span>${roleLabel}</span>
        </span>
        <button type="button" id="btn-navbar-logout" class="btn btn-outline" style="padding: 7px 16px; font-size: 13px;">
          Đăng xuất
        </button>
      `;

      const btnLogout = document.getElementById("btn-navbar-logout");
      if (btnLogout) {
        btnLogout.addEventListener("click", () => {
          Auth.clear();
          window.location.href = "login.html";
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