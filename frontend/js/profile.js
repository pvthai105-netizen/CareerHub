/**
 * profile.js - Xử lý Form Cập nhật thông tin cá nhân sinh viên
 * Mã task: T02D210
 * Tính năng:
 *  - Quản lý thông tin: cá nhân, trường/ngành, kỹ năng, mong muốn.
 *  - Validate hoàn toàn ở client trước khi lưu.
 *  - Lưu trữ vào localStorage (F5 vẫn giữ nguyên 100% dữ liệu).
 *  - Đồng bộ với backend API /api/students/me nếu đã đăng nhập.
 *  - Cập nhật live preview trực quan.
 */

document.addEventListener("DOMContentLoaded", () => {
  const STORAGE_KEY = "careerhub_student_profile";

  // Dữ liệu mẫu khởi tạo nếu người dùng mới vào lần đầu
  const defaultProfile = {
    full_name: "Nguyễn Văn An",
    phone: "0901112223",
    university: "Học viện Công nghệ Bưu chính Viễn thông",
    major: "Công nghệ thông tin",
    bio: "Sinh viên năm 3 đam mê lập trình, có tinh thần cầu tiến và khả năng tự nghiên cứu, mong muốn tìm kiếm cơ hội thực tập phát triển chuyên môn.",
    skills: "HTML/CSS, JavaScript, Python, FastAPI, MySQL, Git",
    desired_job_type: "INTERNSHIP",
    avatar_url: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150"
  };

  // Các trường trong Form
  const form = document.getElementById("profile-form");
  const inputFullName = document.getElementById("full_name");
  const inputPhone = document.getElementById("phone");
  const inputUniversity = document.getElementById("university");
  const inputMajor = document.getElementById("major");
  const inputBio = document.getElementById("bio");
  const inputAvatarUrl = document.getElementById("avatar_url");
  const skillTagInput = document.getElementById("skill-tag-input");
  const skillsContainer = document.getElementById("skills-tag-container");
  const btnReset = document.getElementById("btn-reset-form");
  const toast = document.getElementById("profile-toast");
  const lastSavedTimeEl = document.getElementById("last-saved-time");

  // Các phần tử Live Preview bên trái
  const previewAvatar = document.getElementById("preview-avatar");
  const previewName = document.getElementById("preview-name");
  const previewUniversity = document.getElementById("preview-university");
  const previewMajor = document.getElementById("preview-major");
  const previewPhone = document.getElementById("preview-phone");
  const previewJobType = document.getElementById("preview-job-type");
  const previewSkills = document.getElementById("preview-skills");

  // Danh sách kỹ năng dạng Array
  let skillsList = [];

  // Từ điển nhãn công việc mong muốn
  const jobTypeLabels = {
    INTERNSHIP: "Thực tập sinh (Internship)",
    PART_TIME: "Việc làm bán thời gian (Part-time)",
    BOTH: "Cả hai hình thức (Both)"
  };

  /**
   * 1. Hiển thị thông báo Toast
   */
  let toastTimer = null;
  function showToast(title, message, isError = false) {
    if (!toast) return;
    clearTimeout(toastTimer);
    toast.className = `toast-notice show ${isError ? "toast-error" : ""}`;
    toast.querySelector(".toast-icon").textContent = isError ? "⚠️" : "✓";
    toast.querySelector(".toast-title").textContent = title;
    toast.querySelector(".toast-message").textContent = message;

    toastTimer = setTimeout(() => {
      toast.classList.remove("show");
    }, 4000);
  }

  /**
   * 2. Quản lý Tag Kỹ Năng
   */
  function renderSkills() {
    // Xóa toàn bộ tag cũ nhưng giữ lại input nhập
    const existingTags = skillsContainer.querySelectorAll(".skill-tag");
    existingTags.forEach((tag) => tag.remove());

    // Render từng tag
    skillsList.forEach((skill, index) => {
      const tag = document.createElement("span");
      tag.className = "skill-tag";
      tag.innerHTML = `
        <span>${escapeHtml(skill)}</span>
        <button type="button" class="btn-remove-skill" data-index="${index}" title="Xóa kỹ năng">&times;</button>
      `;
      skillsContainer.insertBefore(tag, skillTagInput);
    });

    // Cập nhật preview kỹ năng bên cột tóm tắt
    renderSkillsPreview();
  }

  function addSkill(skillName) {
    const trimmed = skillName.trim();
    if (!trimmed) return;

    // Không thêm trùng lặp (không phân biệt hoa thường)
    const exists = skillsList.some(
      (s) => s.toLowerCase() === trimmed.toLowerCase()
    );
    if (!exists) {
      skillsList.push(trimmed);
      renderSkills();
      clearError("skills");
    }
    skillTagInput.value = "";
  }

  function removeSkill(index) {
    skillsList.splice(index, 1);
    renderSkills();
  }

  // Bắt sự kiện xóa tag khi click dấu x
  skillsContainer.addEventListener("click", (e) => {
    const removeBtn = e.target.closest(".btn-remove-skill");
    if (removeBtn) {
      const index = parseInt(removeBtn.getAttribute("data-index"), 10);
      removeSkill(index);
    }
  });

  // Bắt sự kiện gõ Enter hoặc dấu phẩy để thêm tag
  skillTagInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addSkill(skillTagInput.value);
    } else if (e.key === "Backspace" && !skillTagInput.value && skillsList.length > 0) {
      // Xóa tag cuối khi ô nhập trống và bấm backspace
      removeSkill(skillsList.length - 1);
    }
  });

  // Bắt sự kiện click vào các chip kỹ năng gợi ý
  document.querySelectorAll(".btn-suggested-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const skill = chip.getAttribute("data-skill");
      addSkill(skill);
    });
  });

  /**
   * 3. Lựa chọn Loại công việc mong muốn (Radio cards)
   */
  const jobCards = document.querySelectorAll(".desired-job-card");
  function setSelectedJobType(val) {
    jobCards.forEach((card) => {
      const radio = card.querySelector('input[type="radio"]');
      if (radio.value === val) {
        radio.checked = true;
        card.classList.add("active");
      } else {
        radio.checked = false;
        card.classList.remove("active");
      }
    });
    updateLivePreview();
  }

  function getSelectedJobType() {
    const checked = document.querySelector('input[name="desired_job_type"]:checked');
    return checked ? checked.value : null;
  }

  jobCards.forEach((card) => {
    card.addEventListener("click", () => {
      const radio = card.querySelector('input[type="radio"]');
      setSelectedJobType(radio.value);
      clearError("desired_job_type");
    });
  });

  /**
   * 4. Cập nhật xem trước (Live Preview)
   */
  function renderSkillsPreview() {
    if (!previewSkills) return;
    previewSkills.innerHTML = "";
    if (skillsList.length === 0) {
      previewSkills.innerHTML = '<span style="color: var(--muted); font-size: 12px">Chưa có kỹ năng</span>';
      return;
    }
    skillsList.forEach((skill) => {
      const pill = document.createElement("span");
      pill.className = "skill-tag-pill";
      pill.textContent = skill;
      previewSkills.appendChild(pill);
    });
  }

  function updateLivePreview() {
    if (previewName) {
      previewName.textContent = inputFullName.value.trim() || "Chưa đặt tên";
    }
    if (previewUniversity) {
      previewUniversity.textContent = inputUniversity.value.trim() || "Chưa cập nhật";
    }
    if (previewMajor) {
      previewMajor.textContent = inputMajor.value.trim() || "Chưa cập nhật";
    }
    if (previewPhone) {
      previewPhone.textContent = inputPhone.value.trim() || "Chưa cập nhật";
    }
    if (previewAvatar) {
      const url = inputAvatarUrl.value.trim();
      if (url) {
        previewAvatar.src = url;
      }
    }
    if (previewJobType) {
      const selected = getSelectedJobType();
      previewJobType.textContent = jobTypeLabels[selected] || "Chưa chọn";
    }
  }

  // Lắng nghe sự kiện input để live update
  [inputFullName, inputPhone, inputUniversity, inputMajor, inputAvatarUrl].forEach((input) => {
    if (input) {
      input.addEventListener("input", updateLivePreview);
    }
  });

  // Xử lý lỗi load ảnh đại diện
  if (previewAvatar) {
    previewAvatar.addEventListener("error", () => {
      previewAvatar.src = "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150";
    });
  }

  /**
   * 5. VALIDATE DỮ LIỆU Ở CLIENT
   */
  function showError(fieldId, message) {
    const errorEl = document.getElementById(`err-${fieldId}`);
    const inputEl = document.getElementById(fieldId);
    if (errorEl) {
      errorEl.textContent = message;
      errorEl.style.display = "block";
    }
    if (inputEl) {
      inputEl.classList.add("input-error");
    }
  }

  function clearError(fieldId) {
    const errorEl = document.getElementById(`err-${fieldId}`);
    const inputEl = document.getElementById(fieldId);
    if (errorEl) {
      errorEl.style.display = "none";
      errorEl.textContent = "";
    }
    if (inputEl) {
      inputEl.classList.remove("input-error");
    }
  }

  // Clear lỗi khi người dùng nhập lại
  [inputFullName, inputPhone, inputUniversity, inputMajor].forEach((input) => {
    if (input) {
      input.addEventListener("input", () => clearError(input.id));
    }
  });

  function validateClient() {
    let isValid = true;
    let firstInvalidField = null;

    // 1. Validate Họ và tên (Bắt buộc, 2 - 100 ký tự)
    const fullNameVal = inputFullName.value.trim();
    if (!fullNameVal) {
      showError("full_name", "Họ và tên không được để trống.");
      isValid = false;
      firstInvalidField = firstInvalidField || inputFullName;
    } else if (fullNameVal.length > 100) {
      showError("full_name", "Họ và tên không được vượt quá 100 ký tự.");
      isValid = false;
      firstInvalidField = firstInvalidField || inputFullName;
    } else {
      clearError("full_name");
    }

    // 2. Validate Số điện thoại (Nếu nhập thì phải đúng định dạng VN 10 số: 0x hoặc +84x)
    const phoneVal = inputPhone.value.trim();
    const phoneRegex = /^(0|\+84)[0-9]{9}$/;
    if (phoneVal && !phoneRegex.test(phoneVal)) {
      showError("phone", "Số điện thoại không hợp lệ (cần 10 chữ số, ví dụ: 0901234567 hoặc +84901234567).");
      isValid = false;
      firstInvalidField = firstInvalidField || inputPhone;
    } else {
      clearError("phone");
    }

    // 3. Validate Trường học (Bắt buộc, tối đa 150 ký tự)
    const universityVal = inputUniversity.value.trim();
    if (!universityVal) {
      showError("university", "Vui lòng nhập trường đại học / cao đẳng đang theo học.");
      isValid = false;
      firstInvalidField = firstInvalidField || inputUniversity;
    } else if (universityVal.length > 150) {
      showError("university", "Tên trường không được vượt quá 150 ký tự.");
      isValid = false;
      firstInvalidField = firstInvalidField || inputUniversity;
    } else {
      clearError("university");
    }

    // 4. Validate Chuyên ngành (Bắt buộc, tối đa 100 ký tự)
    const majorVal = inputMajor.value.trim();
    if (!majorVal) {
      showError("major", "Vui lòng nhập chuyên ngành học.");
      isValid = false;
      firstInvalidField = firstInvalidField || inputMajor;
    } else if (majorVal.length > 100) {
      showError("major", "Chuyên ngành không được vượt quá 100 ký tự.");
      isValid = false;
      firstInvalidField = firstInvalidField || inputMajor;
    } else {
      clearError("major");
    }

    // 5. Validate Kỹ năng (Tối thiểu 1 kỹ năng)
    if (skillsList.length === 0) {
      showError("skills", "Vui lòng thêm ít nhất 1 kỹ năng chuyên môn.");
      isValid = false;
      firstInvalidField = firstInvalidField || skillTagInput;
    } else {
      clearError("skills");
    }

    // 6. Validate Mong muốn công việc (Phải chọn 1 trong các mục)
    const desiredJob = getSelectedJobType();
    if (!desiredJob) {
      showError("desired_job_type", "Vui lòng chọn loại công việc mong muốn.");
      isValid = false;
    } else {
      clearError("desired_job_type");
    }

    if (!isValid && firstInvalidField) {
      firstInvalidField.focus();
    }

    return isValid;
  }

  /**
   * 6. LƯU VÀ KHÔI PHỤC DỮ LIỆU (F5 VẪN CÒN NGUYÊN)
   */
  function populateForm(data) {
    if (!data) return;

    if (inputFullName) inputFullName.value = data.full_name || "";
    if (inputPhone) inputPhone.value = data.phone || "";
    if (inputUniversity) inputUniversity.value = data.university || "";
    if (inputMajor) inputMajor.value = data.major || "";
    if (inputBio) inputBio.value = data.bio || "";
    if (inputAvatarUrl) inputAvatarUrl.value = data.avatar_url || "";

    // Kỹ năng
    if (data.skills) {
      if (Array.isArray(data.skills)) {
        skillsList = [...data.skills];
      } else if (typeof data.skills === "string") {
        skillsList = data.skills
          .split(",")
          .map((s) => s.trim())
          .filter((s) => s.length > 0);
      }
    } else {
      skillsList = [];
    }
    renderSkills();

    // Mong muốn
    if (data.desired_job_type) {
      setSelectedJobType(data.desired_job_type);
    } else {
      setSelectedJobType("BOTH");
    }

    // Cập nhật live preview
    updateLivePreview();

    // Hiển thị thời gian lưu gần nhất nếu có
    if (lastSavedTimeEl && data.updated_at) {
      try {
        const dateObj = new Date(data.updated_at);
        lastSavedTimeEl.textContent = `Đã lưu: ${dateObj.toLocaleTimeString("vi-VN")} ${dateObj.toLocaleDateString("vi-VN")}`;
      } catch (e) {
        lastSavedTimeEl.textContent = "Đã lưu vào bộ nhớ trình duyệt";
      }
    }
  }

  /**
   * Khởi tạo tải dữ liệu:
   * 1. Ưu tiên đọc từ localStorage.
   * 2. Nếu localStorage chưa có, dùng defaultProfile.
   * 3. Nếu người dùng đã đăng nhập (có token), gọi API /api/students/me để cập nhật đồng bộ.
   */
  async function loadInitialData() {
    let localData = null;
    const rawLocal = localStorage.getItem(STORAGE_KEY);
    if (rawLocal) {
      try {
        localData = JSON.parse(rawLocal);
      } catch (err) {
        console.error("Lỗi parse localStorage:", err);
      }
    }

    if (localData) {
      populateForm(localData);
    } else {
      // Thiết lập dữ liệu khởi tạo mẫu
      populateForm(defaultProfile);
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        ...defaultProfile,
        updated_at: new Date().toISOString()
      }));
    }

    // Nếu người dùng có đăng nhập bằng tài khoản sinh viên và backend đang chạy, đồng bộ từ API
    if (typeof Auth !== "undefined" && Auth.getToken() && typeof api !== "undefined") {
      try {
        const apiData = await api.get("/students/me");
        if (apiData) {
          // Lưu vào localStorage và điền form
          const mergedData = {
            ...apiData,
            updated_at: new Date().toISOString()
          };
          localStorage.setItem(STORAGE_KEY, JSON.stringify(mergedData));
          populateForm(mergedData);
        }
      } catch (apiErr) {
        // Backend có thể chưa chạy hoặc token hết hạn, không làm gián đoạn trải nghiệm người dùng
        console.warn("Không thể đồng bộ API, sử dụng dữ liệu offline từ localStorage:", apiErr.message);
      }
    }
  }

  // Thực hiện nạp dữ liệu ngay khi tải trang
  loadInitialData();

  /**
   * 7. Xử lý SUBMIT FORM CẬP NHẬT
   */
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // 1. Validate phía client
    const isValid = validateClient();
    if (!isValid) {
      showToast("Lỗi kiểm tra dữ liệu", "Vui lòng kiểm tra và sửa các thông tin chưa hợp lệ.", true);
      return;
    }

    // 2. Thu thập dữ liệu
    const formData = {
      full_name: inputFullName.value.trim(),
      phone: inputPhone.value.trim() || null,
      university: inputUniversity.value.trim() || null,
      major: inputMajor.value.trim() || null,
      bio: inputBio.value.trim() || null,
      skills: skillsList.join(", "),
      desired_job_type: getSelectedJobType(),
      avatar_url: inputAvatarUrl.value.trim() || null,
      updated_at: new Date().toISOString()
    };

    const submitBtn = document.getElementById("btn-submit-profile");
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = "<span>Đang lưu...</span>";
    }

    try {
      // 3. LƯU VÀO LOCALSTORAGE (Đảm bảo F5 luôn còn dữ liệu)
      localStorage.setItem(STORAGE_KEY, JSON.stringify(formData));

      // 4. Nếu có token thì đồng thời gửi cập nhật lên API Backend
      let apiSynced = false;
      if (typeof Auth !== "undefined" && Auth.getToken() && typeof api !== "undefined") {
        try {
          await api.put("/students/me", {
            full_name: formData.full_name,
            phone: formData.phone,
            university: formData.university,
            major: formData.major,
            bio: formData.bio,
            skills: formData.skills,
            desired_job_type: formData.desired_job_type,
            avatar_url: formData.avatar_url
          });
          apiSynced = true;
        } catch (apiErr) {
          console.warn("Lưu cục bộ thành công, chưa đồng bộ được API:", apiErr.message);
        }
      }

      // Cập nhật nhãn thời gian lưu
      if (lastSavedTimeEl) {
        const now = new Date();
        lastSavedTimeEl.textContent = `Đã lưu: ${now.toLocaleTimeString("vi-VN")} ${now.toLocaleDateString("vi-VN")}`;
      }

      // Thông báo thành công
      const successMsg = apiSynced
        ? "Thông tin đã được lưu vào hệ thống và trình duyệt thành công!"
        : "Đã lưu thông tin vào trình duyệt (F5 vẫn giữ nguyên dữ liệu)!";
      showToast("Cập nhật thành công", successMsg, false);

      // Cập nhật lại live preview
      updateLivePreview();
    } catch (err) {
      showToast("Lỗi lưu dữ liệu", err.message || "Không thể lưu dữ liệu.", true);
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = "<span>Lưu thay đổi</span>";
      }
    }
  });

  /**
   * 8. Nút Khôi phục dữ liệu ban đầu
   */
  if (btnReset) {
    btnReset.addEventListener("click", () => {
      if (confirm("Bạn có chắc muốn khôi phục lại dữ liệu ban đầu không?")) {
        populateForm(defaultProfile);
        localStorage.setItem(STORAGE_KEY, JSON.stringify({
          ...defaultProfile,
          updated_at: new Date().toISOString()
        }));
        showToast("Đã khôi phục", "Đã đặt lại dữ liệu về trạng thái ban đầu.");
      }
    });
  }

  // Tiện ích escape html
  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
