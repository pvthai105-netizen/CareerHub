/**
 * employer_profile.js - Quản lý Form Hồ sơ Doanh nghiệp
 */

document.addEventListener("DOMContentLoaded", async () => {
  // 1. Kiểm tra quyền truy cập (Bắt buộc vai trò Employer)
  const currentUser = AuthGuard.requireRoles(["employer"]);
  if (!currentUser) return;

  // 2. Tham chiếu các phần tử DOM
  const form = document.getElementById("employer-form");
  const inputCompanyName = document.getElementById("company_name");
  const inputWebsite = document.getElementById("company_website");
  const inputTaxCode = document.getElementById("tax_code");
  const inputAddress = document.getElementById("address");
  const inputDescription = document.getElementById("description");
  const inputContactName = document.getElementById("contact_name");
  const inputEmail = document.getElementById("company_email");
  const inputPhone = document.getElementById("phone");
  const logoFileInput = document.getElementById("logo-file-input");
  const logoPreview = document.getElementById("logo-preview");
  const previewCompanyName = document.getElementById("preview-company-name");
  const sidebarCompanyName = document.getElementById("sidebar-company-name");
  const userDisplayEmail = document.getElementById("user-display-email");
  const btnViewPublic = document.getElementById("btn-view-public");
  const btnSave = document.getElementById("btn-save-profile");
  const logoUploadStatus = document.getElementById("logo-upload-status");
  const toast = document.getElementById("toast-message");

  let currentProfileId = null;

  // Hiển thị Toast
  function showToast(title, message, isError = false) {
    if (!toast) return;
    toast.className = `toast-notice show ${isError ? "toast-error" : ""}`;
    toast.querySelector(".toast-icon").textContent = isError ? "⚠️" : "✓";
    toast.querySelector(".toast-title").textContent = title;
    toast.querySelector(".toast-desc").textContent = message;
    setTimeout(() => toast.classList.remove("show"), 4000);
  }

  // Tính toán thanh tiến độ hoàn thiện hồ sơ
  function calculateProgress() {
    let fields = [
      inputCompanyName.value.trim(),
      inputAddress.value.trim(),
      inputContactName.value.trim(),
      inputPhone.value.trim(),
      inputWebsite.value.trim(),
      inputTaxCode.value.trim(),
      inputDescription.value.trim(),
    ];
    let filledCount = fields.filter((val) => val.length > 0).length;
    let percent = Math.round((filledCount / fields.length) * 100);

    const percentEl = document.getElementById("progress-percent");
    const fillEl = document.getElementById("progress-bar-fill");
    if (percentEl) percentEl.textContent = `${percent}%`;
    if (fillEl) fillEl.style.width = `${percent}%`;
  }

  // 3. Tải dữ liệu hồ sơ công ty từ API
  async function loadProfile() {
    try {
      const data = await api.get("/employers/me");
      if (!data) return;

      currentProfileId = data.id;

      // Đổ dữ liệu vào Form
      inputCompanyName.value = data.company_name || "";
      inputWebsite.value = data.company_website || "";
      inputTaxCode.value = data.tax_code || "";
      inputAddress.value = data.address || "";
      inputDescription.value = data.description || "";
      inputContactName.value = data.contact_name || "";
      inputPhone.value = data.phone || "";
      inputEmail.value = data.email || "";

      // Hiển thị logo nếu có
      if (data.logo_url) {
        logoPreview.src = data.logo_url;
      }

      // Tên hiển thị trên Preview & Sidebar
      const name = data.company_name || "LUMINA STUDIO";
      previewCompanyName.textContent = name;
      sidebarCompanyName.textContent = name;
      userDisplayEmail.textContent = data.email || "";

      // Gắn link nút xem trang công khai
      btnViewPublic.href = `company_detail.html?id=${data.id}`;

      calculateProgress();
    } catch (err) {
      showToast("Lỗi tải hồ sơ", err.message, true);
    }
  }

  // 4. Xử lý Upload Logo
  logoFileInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Kiểm tra định dạng
    const validTypes = ["image/png", "image/jpeg", "image/jpg", "image/webp"];
    if (!validTypes.includes(file.type)) {
      showToast("Tệp không hợp lệ", "Chỉ nhận định dạng ảnh PNG, JPG hoặc WEBP.", true);
      return;
    }

    // Kiểm tra dung lượng (tối đa 2MB)
    if (file.size > 2 * 1024 * 1024) {
      showToast("Ảnh quá lớn", "Dung lượng ảnh tối đa 2MB.", true);
      return;
    }

    // Hiển thị preview ngay lập tức
    const reader = new FileReader();
    reader.onload = (ev) => {
      logoPreview.src = ev.target.result;
    };
    reader.readAsDataURL(file);

    // Gửi lên backend
    logoUploadStatus.textContent = "Đang tải lên...";
    logoUploadStatus.className = "status-msg";

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await apiFetch("/employers/logo", {
        method: "POST",
        body: formData,
      });
      logoUploadStatus.textContent = "Đã lưu logo!";
      logoUploadStatus.className = "status-msg success";
      showToast("Thành công", "Logo công ty đã được cập nhật.");
    } catch (err) {
      logoUploadStatus.textContent = "Lỗi upload!";
      logoUploadStatus.className = "status-msg error";
      showToast("Lỗi upload logo", err.message, true);
    }
  });

  // 5. Lưu thông tin form (Cập nhật hồ sơ công ty)
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Reset thông báo lỗi
    document.getElementById("err-company-name").textContent = "";
    document.getElementById("err-address").textContent = "";
    document.getElementById("err-phone").textContent = "";

    const companyName = inputCompanyName.value.trim();
    const address = inputAddress.value.trim();
    const phone = inputPhone.value.trim();

    // Validate client-side
    let hasError = false;
    if (!companyName) {
      document.getElementById("err-company-name").textContent = "Vui lòng nhập tên công ty.";
      hasError = true;
    }
    if (!address) {
      document.getElementById("err-address").textContent = "Vui lòng nhập địa chỉ trụ sở.";
      hasError = true;
    }
    if (phone && !/^(0|\+84)[0-9]{9}$/.test(phone)) {
      document.getElementById("err-phone").textContent = "Số điện thoại cần 10 chữ số (vd: 0901234567).";
      hasError = true;
    }

    if (hasError) return;

    btnSave.disabled = true;
    btnSave.textContent = "Đang lưu...";

    const payload = {
      company_name: companyName,
      company_website: inputWebsite.value.trim() || null,
      tax_code: inputTaxCode.value.trim() || null,
      address: address,
      description: inputDescription.value.trim() || null,
      contact_name: inputContactName.value.trim() || null,
      phone: phone || null,
    };

    try {
      const updated = await api.put("/employers/me", payload);
      showToast("Thành công", "Đã lưu thông tin hồ sơ doanh nghiệp!");
      previewCompanyName.textContent = updated.company_name;
      sidebarCompanyName.textContent = updated.company_name;
      calculateProgress();
    } catch (err) {
      showToast("Lỗi lưu hồ sơ", err.message, true);
    } finally {
      btnSave.disabled = false;
      btnSave.textContent = "Lưu thay đổi";
    }
  });

  // Tự động tính lại tiến độ khi người dùng gõ phím
  form.addEventListener("input", calculateProgress);

  // Nút đăng xuất ở sidebar
  const btnLogout = document.getElementById("btn-sidebar-logout");
  if (btnLogout) {
    btnLogout.addEventListener("click", (e) => {
      e.preventDefault();
      Auth.clear();
      window.location.href = "login.html";
    });
  }

  // Khởi động
  await loadProfile();
});