document.addEventListener("DOMContentLoaded", () => {
  // Regex kiểm tra định dạng email chuẩn
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  // ==========================================
  // 1. XỬ LÝ TRANG ĐĂNG NHẬP (LOGIN)
  // ==========================================
  const formLogin = document.getElementById("form-login");
  if (formLogin) {
    const emailInput = document.getElementById("login-email");
    const passwordInput = document.getElementById("login-password");
    const errEmail = document.getElementById("err-login-email");
    const errPassword = document.getElementById("err-login-password");
    const alertBox = document.getElementById("login-alert");
    const btnSubmit = document.getElementById("btn-submit-login");

    // Nếu đã đăng nhập và token còn hạn, tự chuyển trang luôn
    const currentUser = AuthGuard.getUser();
    if (currentUser) {
      AuthGuard.redirectByRole(currentUser.role);
      return;
    }

    // Kiểm tra thông báo token hết hạn trên URL query (?expired=1)
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("expired") === "1") {
      alertBox.className = "alert-box info";
      alertBox.textContent = "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.";
    }

    formLogin.addEventListener("submit", async (e) => {
      e.preventDefault();
      alertBox.className = "alert-box";
      alertBox.textContent = "";

      let isValid = true;
      const email = emailInput.value.trim();
      const password = passwordInput.value;

      // Validate email
      if (!email || !emailRegex.test(email)) {
        errEmail.style.display = "block";
        isValid = false;
      } else {
        errEmail.style.display = "none";
      }

      // Validate password
      if (!password) {
        errPassword.style.display = "block";
        isValid = false;
      } else {
        errPassword.style.display = "none";
      }

      if (!isValid) return;

      // Gửi API đăng nhập
      try {
        btnSubmit.disabled = true;
        btnSubmit.textContent = "Đang đăng nhập...";

        const data = await api.post("/auth/login", { email, password });
        
        // Lưu access_token vào localStorage
        Auth.setToken(data.access_token);

        // Lấy thông tin user vừa giải mã từ token và chuyển trang
        const user = AuthGuard.getUser();
        if (user) {
          AuthGuard.redirectByRole(user.role);
        } else {
          window.location.href = "/index.html";
        }
      } catch (err) {
        alertBox.className = "alert-box error";
        alertBox.textContent = err.message || "Đăng nhập thất bại. Vui lòng thử lại.";
      } finally {
        btnSubmit.disabled = false;
        btnSubmit.textContent = "Đăng nhập";
      }
    });
  }

  // ==========================================
  // 2. XỬ LÝ TRANG ĐĂNG KÝ (REGISTER)
  // ==========================================
  const formRegister = document.getElementById("form-register");
  if (formRegister) {
    const emailInput = document.getElementById("reg-email");
    const passwordInput = document.getElementById("reg-password");
    const repasswordInput = document.getElementById("reg-repassword");
    const errEmail = document.getElementById("err-reg-email");
    const errPassword = document.getElementById("err-reg-password");
    const errRepassword = document.getElementById("err-reg-repassword");
    const alertBox = document.getElementById("register-alert");
    const btnSubmit = document.getElementById("btn-submit-reg");

    // Xử lý hiệu ứng chọn vai trò (Student / Employer)
    const roleRadios = document.querySelectorAll('input[name="role"]');
    roleRadios.forEach((radio) => {
      radio.addEventListener("change", (e) => {
        document.querySelectorAll(".role-box").forEach((b) => b.classList.remove("active"));
        e.target.closest(".role-box").classList.add("active");
      });
    });

    formRegister.addEventListener("submit", async (e) => {
      e.preventDefault();
      alertBox.className = "alert-box";
      alertBox.textContent = "";

      let isValid = true;
      const email = emailInput.value.trim();
      const password = passwordInput.value;
      const repassword = repasswordInput.value;
      const selectedRole = document.querySelector('input[name="role"]:checked')?.value;

      // Validate Email
      if (!email || !emailRegex.test(email)) {
        errEmail.style.display = "block";
        isValid = false;
      } else {
        errEmail.style.display = "none";
      }

      // Validate Mật khẩu (Pydantic yêu cầu tối thiểu 8 ký tự)
      if (!password || password.length < 8) {
        errPassword.style.display = "block";
        isValid = false;
      } else {
        errPassword.style.display = "none";
      }

      // Validate Mật khẩu xác nhận
      if (password !== repassword) {
        errRepassword.style.display = "block";
        isValid = false;
      } else {
        errRepassword.style.display = "none";
      }

      if (!isValid) return;

      try {
        btnSubmit.disabled = true;
        btnSubmit.textContent = "Đang tạo tài khoản...";

        await api.post("/auth/register", {
          email: email,
          password: password,
          role: selectedRole,
        });

        alertBox.className = "alert-box success";
        alertBox.textContent = "Đăng ký thành công! Đang chuyển hướng sang trang đăng nhập...";

        // Chờ 1.5 giây để người dùng thấy thông báo rồi chuyển trang
        setTimeout(() => {
          window.location.href = "/login.html";
        }, 1500);
      } catch (err) {
        alertBox.className = "alert-box error";
        alertBox.textContent = err.message || "Đăng ký không thành công.";
      } finally {
        btnSubmit.disabled = false;
        btnSubmit.textContent = "Đăng ký tài khoản";
      }
    });
  }
});