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
        window.location.href = "/index.html"; // Trang sinh viên (tìm việc, hồ sơ)
        break;
      case "employer":
        window.location.href = "/index.html"; // Hoặc trang quản lý tin tuyển dụng khi hoàn thành
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
};