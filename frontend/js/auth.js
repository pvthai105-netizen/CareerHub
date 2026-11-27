document.addEventListener("DOMContentLoaded", () => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  // Xử lý nút Hiện/Ẩn mật khẩu (Toggle Password)
  const btnTogglePwd = document.getElementById("btn-toggle-pwd");
  const loginPasswordInput = document.getElementById("login-password");
  if (btnTogglePwd && loginPasswordInput) {
    btnTogglePwd.addEventListener("click", () => {
      const isPassword = loginPasswordInput.type === "password";
      loginPasswordInput.type = isPassword ? "text" : "password";
      btnTogglePwd.textContent = isPassword ? "Ẩn" : "Hiện";
    });
  }

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

    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("expired") === "1" || urlParams.get("logout") === "1") {
      Auth.clear();
      if (alertBox) {
        alertBox.className = "alert-box info";
        alertBox.textContent =
          urlParams.get("logout") === "1"
            ? "Đã đăng xuất thành công."
            : "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.";
      }
    }

    const currentUser = AuthGuard.getUser();
    if (currentUser && !urlParams.has("force")) {
      AuthGuard.redirectByRole(currentUser.role);
      return;
    }

    formLogin.addEventListener("submit", async (e) => {
      e.preventDefault();
      alertBox.className = "alert-box";
      alertBox.textContent = "";

      let isValid = true;
      const email = emailInput.value.trim();
      const password = passwordInput.value;

      if (!email || !emailRegex.test(email)) {
        errEmail.style.display = "block";
        isValid = false;
      } else {
        errEmail.style.display = "none";
      }

      if (!password) {
        errPassword.style.display = "block";
        isValid = false;
      } else {
        errPassword.style.display = "none";
      }

      if (!isValid) return;

      try {
        btnSubmit.disabled = true;
        btnSubmit.textContent = "Đang đăng nhập...";

        const data = await api.post("/api/auth/login", { email, password });
        Auth.setToken(data.access_token);

        const user = AuthGuard.getUser();
        if (user) {
          AuthGuard.redirectByRole(user.role);
        } else {
          window.location.href = "home.html";
        }
      } catch (err) {
        alertBox.className = "alert-box error";
        alertBox.textContent = err.message || "Email hoặc mật khẩu không đúng.";
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
    const fullNameInput = document.getElementById("reg-fullname");
    const emailInput = document.getElementById("reg-email");
    const passwordInput = document.getElementById("reg-password");
    const repasswordInput = document.getElementById("reg-repassword");
    const errEmail = document.getElementById("err-reg-email");
    const errPassword = document.getElementById("err-reg-password");
    const errRepassword = document.getElementById("err-reg-repassword");
    const alertBox = document.getElementById("register-alert");
    const btnSubmit = document.getElementById("btn-submit-reg");

    // Tự động tích chọn role nếu URL có ?role=employer
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("role") === "employer") {
      const empRadio = document.querySelector('input[name="role"][value="employer"]');
      if (empRadio) {
        empRadio.checked = true;
        document.querySelectorAll(".role-pill").forEach((p) => p.classList.remove("active"));
        document.getElementById("label-role-employer")?.classList.add("active");
      }
    }

    // Hiệu ứng click chọn vai trò
    const rolePills = document.querySelectorAll(".role-pill");
    rolePills.forEach((pill) => {
      pill.addEventListener("click", () => {
        rolePills.forEach((p) => p.classList.remove("active"));
        pill.classList.add("active");
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
      const fullName = fullNameInput ? fullNameInput.value.trim() : "";
      const selectedRole = document.querySelector('input[name="role"]:checked')?.value || "student";

      if (!email || !emailRegex.test(email)) {
        errEmail.style.display = "block";
        isValid = false;
      } else {
        errEmail.style.display = "none";
      }

      if (!password || password.length < 8) {
        errPassword.style.display = "block";
        isValid = false;
      } else {
        errPassword.style.display = "none";
      }

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

        // Lưu họ tên vào localStorage để sang trang hồ sơ tự điền
        if (fullName) {
          localStorage.setItem("temp_registered_name", fullName);
        }

        await api.post("/api/auth/register", {
          email: email,
          password: password,
          role: selectedRole,
        });

        // Tự động đăng nhập
        let autoLoggedIn = false;
        try {
          const loginData = await api.post("/api/auth/login", { email, password });
          if (loginData && loginData.access_token) {
            Auth.setToken(loginData.access_token);
            autoLoggedIn = true;
          }
        } catch (_) {}

        alertBox.className = "alert-box success";
        alertBox.textContent = "Đăng ký thành công! Đang chuyển hướng...";

        setTimeout(() => {
          if (autoLoggedIn) {
            if (selectedRole === "student") {
              window.location.href = "profile.html";
            } else if (selectedRole === "employer") {
              window.location.href = "employer_profile.html";
            } else {
              window.location.href = "home.html";
            }
          } else {
            window.location.href = "login.html";
          }
        }, 1200);
      } catch (err) {
        alertBox.className = "alert-box error";
        alertBox.textContent = err.message || "Đăng ký không thành công.";
      } finally {
        btnSubmit.disabled = false;
        btnSubmit.textContent = "Tạo tài khoản";
      }
    });
  }
});