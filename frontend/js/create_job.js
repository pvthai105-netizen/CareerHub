/* ---------- BƯỚC 1: LẤY CÁC PHẦN TỬ HTML ---------- */
const form = document.getElementById("job-form");
const steps = document.querySelectorAll("#steps li");
const toast = document.getElementById("toast");
const dialog = document.getElementById("preview-dialog");
const previewList = document.getElementById("preview-list");

const saveDraftBtn = document.getElementById("save-draft-btn");
const editBtn = document.getElementById("edit-btn");
const submitBtn = document.getElementById("submit-btn");

const DRAFT_KEY = "job-post-draft";

// Lấy ID tin tuyển dụng từ URL.
// Nếu có ID thì đang ở chế độ sửa tin.
const urlParams = new URLSearchParams(window.location.search);
const editJobId = urlParams.get("edit_id");

// Danh sách các trường trong form
const fields = [
  { id: "title", label: "Tên vị trí tuyển dụng" },
  { id: "category", label: "Ngành nghề" },
  { id: "location", label: "Địa điểm làm việc" },
  { id: "salaryMin", label: "Mức lương tối thiểu" },
  { id: "salaryMax", label: "Mức lương tối đa" },
  { id: "jobType", label: "Loại hình công việc" },
  { id: "quantity", label: "Số lượng tuyển dụng" },
  { id: "experience", label: "Kinh nghiệm" },
  { id: "description", label: "Mô tả công việc" },
  { id: "requirements", label: "Yêu cầu ứng viên" },
  { id: "deadline", label: "Hạn ứng tuyển" },
  { id: "benefits", label: "Quyền lợi" }
];


/* ---------- BƯỚC 2: CÁC HÀM HỖ TRỢ ---------- */

// Lấy giá trị của một ô nhập theo ID
function getValue(id) {
  const element = document.getElementById(id);

  return element ? element.value.trim() : "";
}


// Hiển thị thông báo nhỏ trên màn hình
function showToast(message) {
  if (!toast) return;

  toast.textContent = message;
  toast.classList.add("show");

  setTimeout(function () {
    toast.classList.remove("show");
  }, 2500);
}


// Đánh dấu tiến trình các bước
function setStep(number) {
  steps.forEach(function (step, index) {
    step.classList.toggle("active", index < number);
  });
}


// Hiển thị lỗi tại một ô nhập
function showError(id, message) {
  const input = document.getElementById(id);

  if (!input) return;

  const field = input.closest(".field");
  const errorText = document.getElementById(id + "-error");

  if (field) {
    field.classList.add("has-error");
  }

  if (errorText) {
    errorText.textContent = message;
  }
}


// Xóa các lỗi đang hiển thị
function clearErrors() {
  document.querySelectorAll(".field.has-error").forEach(function (field) {
    field.classList.remove("has-error");

    const errorText = field.querySelector("[id$='-error']");

    if (errorText) {
      errorText.textContent = "";
    }
  });
}


// Lấy ngày hiện tại theo định dạng YYYY-MM-DD
function todayIso() {
  const now = new Date();

  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");

  return now.getFullYear() + "-" + month + "-" + day;
}


// Chuyển ngày YYYY-MM-DD thành DD/MM/YYYY
function formatDate(isoDate) {
  if (!isoDate) return "";

  const parts = isoDate.split("-");

  return parts[2] + "/" + parts[1] + "/" + parts[0];
}


// Định dạng số tiền
function formatMoney(number) {
  return Number(number).toLocaleString("vi-VN");
}


/* ---------- BƯỚC 3: KIỂM TRA DỮ LIỆU ---------- */

function validateForm() {
  clearErrors();

  let isValid = true;

  // Các trường bắt buộc
  const requiredMessages = {
    title: "Vui lòng nhập tên vị trí.",
    category: "Vui lòng chọn ngành nghề.",
    location: "Vui lòng nhập địa điểm làm việc.",
    salaryMin: "Vui lòng nhập mức lương tối thiểu.",
    salaryMax: "Vui lòng nhập mức lương tối đa.",
    jobType: "Vui lòng chọn loại hình công việc.",
    quantity: "Vui lòng nhập số lượng tuyển.",
    experience: "Vui lòng chọn kinh nghiệm.",
    description: "Vui lòng nhập mô tả công việc.",
    requirements: "Vui lòng nhập yêu cầu ứng viên.",
    deadline: "Vui lòng chọn hạn ứng tuyển."
  };

  // Kiểm tra các trường bắt buộc
  for (const id in requiredMessages) {
    if (getValue(id) === "") {
      showError(id, requiredMessages[id]);
      isValid = false;
    }
  }

  // Kiểm tra mức lương
  const min = Number(getValue("salaryMin"));
  const max = Number(getValue("salaryMax"));

  if (
    getValue("salaryMin") !== "" &&
    getValue("salaryMax") !== "" &&
    (min < 0 || max < 0 || min > max)
  ) {
    showError(
      "salaryMax",
      "Mức lương tối đa phải lớn hơn hoặc bằng mức tối thiểu."
    );

    isValid = false;
  }

  // Kiểm tra số lượng tuyển dụng
  const quantity = Number(getValue("quantity"));

  if (
    getValue("quantity") !== "" &&
    (!Number.isInteger(quantity) || quantity < 1)
  ) {
    showError(
      "quantity",
      "Số lượng tuyển phải là số nguyên từ 1 trở lên."
    );

    isValid = false;
  }

  // Kiểm tra hạn ứng tuyển
  if (
    getValue("deadline") !== "" &&
    getValue("deadline") < todayIso()
  ) {
    showError(
      "deadline",
      "Hạn ứng tuyển phải từ hôm nay trở đi."
    );

    isValid = false;
  }

  // Đưa con trỏ đến ô lỗi đầu tiên
  if (!isValid) {
    const firstError = document.querySelector(
      ".field.has-error input, " +
      ".field.has-error select, " +
      ".field.has-error textarea"
    );

    if (firstError) {
      firstError.focus();
    }
  }

  return isValid;
}


/* ---------- BƯỚC 4: LƯU VÀ KHÔI PHỤC BẢN NHÁP ---------- */

// Thu thập dữ liệu từ form
function collectFormData() {
  const data = {};

  fields.forEach(function (field) {
    data[field.id] = getValue(field.id);
  });

  return data;
}


// Lưu bản nháp vào localStorage
function saveDraft() {
  const data = collectFormData();

  localStorage.setItem(DRAFT_KEY, JSON.stringify(data));

  showToast("Đã lưu bản nháp");
}


// Khôi phục bản nháp khi mở trang
function loadDraft() {
  const saved = localStorage.getItem(DRAFT_KEY);

  if (!saved) return;

  try {
    const data = JSON.parse(saved);

    fields.forEach(function (field) {
      const input = document.getElementById(field.id);

      if (input) {
        input.value = data[field.id] || "";
      }
    });

    showToast("Đã khôi phục bản nháp của bạn");

  } catch (error) {
    console.error("Không thể khôi phục bản nháp:", error);

    localStorage.removeItem(DRAFT_KEY);
  }
}

// Chuyển giá trị loại công việc từ Backend sang nội dung hiển thị
function getJobTypeLabel(jobType) {
  const typeMap = {
    FULL_TIME: "Toàn thời gian",
    PART_TIME: "Bán thời gian",
    INTERNSHIP: "Thực tập",
    REMOTE: "Làm việc từ xa",
    CONTRACT: "Hợp đồng"
  };

  return typeMap[String(jobType || "").toUpperCase()] || jobType;
}


// Lấy thông tin tin tuyển dụng để điền vào form
async function loadJobForEdit() {
  try {
    const response = await api.get(`/jobs/my-jobs/${editJobId}`);

    // Hỗ trợ trường hợp API trả dữ liệu trực tiếp hoặc nằm trong data
    const job = response.data ?? response;

    // Điền dữ liệu cũ vào form
    document.getElementById("title").value = job.title || "";
    document.getElementById("category").value = job.industry || "";
    document.getElementById("location").value = job.location || "";

    document.getElementById("salaryMin").value = job.salary_min ?? "";
    document.getElementById("salaryMax").value = job.salary_max ?? "";

    document.getElementById("jobType").value =
      getJobTypeLabel(job.job_type);

    document.getElementById("quantity").value = job.quantity ?? "";
    document.getElementById("experience").value = job.experience || "";

    document.getElementById("description").value = job.description || "";
    document.getElementById("requirements").value = job.requirements || "";

    // Chỉ lấy phần ngày YYYY-MM-DD để hiển thị trong input date
    document.getElementById("deadline").value = job.deadline ? String(job.deadline).slice(0, 10) : "";

    document.getElementById("benefits").value = job.benefits || "";

    showToast("Đã tải thông tin tin tuyển dụng");

  } catch (error) {
    showToast(error.message || "Không thể tải thông tin tin tuyển dụng");
  }
}


/* ---------- BƯỚC 5: XEM TRƯỚC TIN TUYỂN DỤNG ---------- */

// Thêm một dòng thông tin vào phần xem trước
function addPreviewRow(label, value) {
  const row = document.createElement("div");

  const dt = document.createElement("dt");
  const dd = document.createElement("dd");

  dt.textContent = label;
  dd.textContent = value;

  row.appendChild(dt);
  row.appendChild(dd);

  previewList.appendChild(row);
}


// Mở hộp thoại xem trước
function openPreview() {
  const data = collectFormData();

  previewList.innerHTML = "";

  addPreviewRow("Vị trí", data.title);
  addPreviewRow("Ngành nghề", data.category);
  addPreviewRow("Địa điểm", data.location);

  addPreviewRow(
    "Mức lương",
    formatMoney(data.salaryMin) +
    " – " +
    formatMoney(data.salaryMax) +
    " VNĐ"
  );

  addPreviewRow("Loại hình", data.jobType);
  addPreviewRow("Số lượng", data.quantity + " người");
  addPreviewRow("Kinh nghiệm", data.experience);
  addPreviewRow("Hạn ứng tuyển", formatDate(data.deadline));

  addPreviewRow("Mô tả công việc", data.description);
  addPreviewRow("Yêu cầu ứng viên", data.requirements);

  if (data.benefits !== "") {
    addPreviewRow("Quyền lợi", data.benefits);
  }

  setStep(3);

  dialog.showModal();
}


// Đóng hộp thoại xem trước
function closePreview() {
  if (dialog.open) {
    dialog.close();
  }
}


/* ---------- BƯỚC 6: CHUẨN BỊ DỮ LIỆU GỬI BACKEND ---------- */

// Chuyển loại công việc về đúng giá trị Enum của Backend
function getJobTypeValue() {
  const select = document.getElementById("jobType");

  const selectedOption = select.options[select.selectedIndex];

  // Ưu tiên lấy value của option
  let value = selectedOption.value.trim().toUpperCase();

  // Nếu value đang là tiếng Việt thì dựa vào nội dung hiển thị
  const text = selectedOption.textContent.trim().toLowerCase();

  const typeMap = {
    "toàn thời gian": "FULL_TIME",
    "bán thời gian": "PART_TIME",
    "thực tập": "INTERNSHIP",
    "làm từ xa": "REMOTE",
    "hợp đồng": "CONTRACT"
  };

  if (typeMap[text]) {
    return typeMap[text];
  }

  return value;
}


// Chuyển dữ liệu form sang cấu trúc Backend cần
function prepareJobPayload() {
  const data = collectFormData();

  return {
    title: data.title,
    industry: data.category,
    location: data.location,

    // Chuyển mức lương sang kiểu số
    salary_min: Number(data.salaryMin),
    salary_max: Number(data.salaryMax),

    // Giá trị Enum: FULL_TIME, PART_TIME, INTERNSHIP...
    job_type: getJobTypeValue(),

    deadline: data.deadline,

    // Bốn trường bổ sung
    quantity: Number(data.quantity),
    experience: data.experience,
    requirements: data.requirements,
    benefits: data.benefits,

    description: data.description
  };
}


/* ---------- BƯỚC 7: GỬI TIN TUYỂN DỤNG ---------- */

// Gửi dữ liệu lên Backend
async function submitJob() {

  // Tránh người dùng bấm gửi nhiều lần
  if (submitBtn.disabled) return;

  try {
    // Kiểm tra đăng nhập
    if (!localStorage.getItem("careerhub_token")) {
      throw new Error("Vui lòng đăng nhập bằng tài khoản nhà tuyển dụng.");
    }

    // Chuẩn bị dữ liệu gửi đi
    const payload = prepareJobPayload();

    // Khóa nút gửi trong lúc chờ Backend xử lý
    submitBtn.disabled = true;

    const oldButtonText = submitBtn.textContent;
    submitBtn.textContent = "Đang gửi...";

    // Gọi API tạo tin tuyển dụng
    // api.post tự thêm token và chuyển dữ liệu thành JSON
    // Gửi dữ liệu lên Backend
    let result;
    // Nếu có ID thì cập nhật tin tuyển dụng
    if (editJobId) {
      result = await api.put(`/jobs/my-jobs/${editJobId}`, payload);

    } else {
      // Nếu không có ID thì tạo tin tuyển dụng mới
      result = await api.post("/jobs", payload);
    }

    // Đóng modal sau khi Backend xác nhận đã lưu
    dialog.close();

    // Xóa dữ liệu form
    form.reset();

    // Xóa bản nháp cũ
    localStorage.removeItem(DRAFT_KEY);

    // Thông báo thành công
    showToast(editJobId ? "Cập nhật tin tuyển dụng thành công!" : "Đăng tin tuyển dụng thành công!");

    // Chuyển về trang quản lý tin tuyển dụng
    // Trang này sẽ tự tải lại danh sách từ Backend
    setTimeout(function () {
      window.location.href = "./job_post.html";
    }, 800);

  } catch (error) {
    showToast(error.message || "Không thể tạo tin tuyển dụng.");

  } finally {
    // Mở lại nút gửi sau khi xử lý xong
    submitBtn.disabled = false;

    if (submitBtn.textContent === "Đang gửi...") {
      submitBtn.textContent = "Gửi tin";
    }
  }
}


/* ---------- BƯỚC 8: GẮN SỰ KIỆN ---------- */

// Khi gửi form thì kiểm tra dữ liệu và mở xem trước
form.addEventListener("submit", function (event) {
  event.preventDefault();

  if (validateForm()) {
    openPreview();
  }
});


// Nút lưu bản nháp
saveDraftBtn.addEventListener("click", saveDraft);


// Nút chỉnh sửa
editBtn.addEventListener("click", closePreview);


// Nút gửi tin
submitBtn.addEventListener("click", submitJob);


// Khi đóng hộp thoại xem trước
dialog.addEventListener("close", function () {
  setStep(2);
});


// Khi người dùng sửa nội dung ô nhập thì xóa lỗi
form.addEventListener("input", function (event) {
  const field = event.target.closest(".field");

  if (field) {
    field.classList.remove("has-error");

    const errorText = field.querySelector("[id$='-error']");

    if (errorText) {
      errorText.textContent = "";
    }
  }
});

function editJob(jobId) {
  if (!jobId) {
    alert('Không tìm thấy ID tin tuyển dụng');
    return;
  }

  window.location.href = `create_job.html?edit_id=${jobId}`;
}

/* ---------- BƯỚC 9: KHỞI TẠO TRANG ---------- */

// Không cho chọn hạn ứng tuyển trong quá khứ
document.getElementById("deadline").min = todayIso();

// Đánh dấu bước nhập thông tin
setStep(2);

// Nếu có ID thì tải dữ liệu cũ để sửa
if (editJobId) {
  document.querySelector("h1").textContent = "Chỉnh sửa tin tuyển dụng";
  submitBtn.textContent = "Cập nhật tin";

  loadJobForEdit();

} else {
  // Nếu không có ID thì khôi phục bản nháp
  loadDraft();
}
