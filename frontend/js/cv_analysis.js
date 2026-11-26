const CV_ANALYSIS_URL = "http://127.0.0.1:8000/api/students/me/cv-analyses";
const MAX_CV_SIZE = 5 * 1024 * 1024;
const CV_ANALYSIS_LISTS = [
  ["strengths", "cv-strengths", "Chưa có điểm mạnh được ghi nhận."],
  ["weaknesses", "cv-weaknesses", "Chưa ghi nhận điểm cần cải thiện."],
  ["missing_skills", "cv-missing-skills", "Chưa xác định kỹ năng còn thiếu."],
  ["improvement_suggestions", "cv-improvement-suggestions", "Chưa có gợi ý cải thiện."],
];

function escapeCVText(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function getCVErrorMessage(data, response) {
  if (response.status === 401) {
    return "Vui lòng đăng nhập bằng tài khoản sinh viên để phân tích CV.";
  }
  if (response.status === 403) {
    return "Tính năng phân tích CV chỉ dành cho tài khoản sinh viên.";
  }

  const detail = data?.detail ?? data?.message;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    return detail.map((item) => item.msg).filter(Boolean).join(" ");
  }
  return `Không thể phân tích CV lúc này (mã lỗi ${response.status}).`;
}

function validateCVResult(data) {
  const listFields = CV_ANALYSIS_LISTS.map(([field]) => field);
  if (
    !data ||
    typeof data.summary !== "string" ||
    !Number.isInteger(data.score) ||
    data.score < 0 ||
    data.score > 100 ||
    listFields.some((field) => !Array.isArray(data[field]) || data[field].some((item) => typeof item !== "string"))
  ) {
    throw new Error("Kết quả phân tích từ máy chủ không đúng định dạng.");
  }
}

function renderCVResult(data) {
  validateCVResult(data);

  document.getElementById("cv-summary").textContent = data.summary;
  document.getElementById("cv-score").textContent = String(data.score);
  const progress = document.getElementById("cv-score-progress");
  progress.style.width = `${data.score}%`;
  progress.parentElement.setAttribute("aria-valuenow", String(data.score));
  document.getElementById("cv-result-filename").textContent = data.filename
    ? `Tệp đã phân tích: ${data.filename}`
    : "";

  CV_ANALYSIS_LISTS.forEach(([field, elementId, emptyMessage]) => {
    const list = document.getElementById(elementId);
    const items = data[field];
    list.innerHTML = items.length
      ? items.map((item) => `<li>${escapeCVText(item)}</li>`).join("")
      : `<li>${escapeCVText(emptyMessage)}</li>`;
  });

  document.getElementById("cv-analysis-results").hidden = false;
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("cv-analysis-form");
  const fileInput = document.getElementById("cv-analysis-file");
  const fileName = document.getElementById("cv-file-name");
  const submitButton = document.getElementById("cv-analysis-submit");
  const errorMessage = document.getElementById("cv-analysis-error");
  const results = document.getElementById("cv-analysis-results");

  fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    fileName.textContent = file ? file.name : "Chọn CV từ thiết bị";
    submitButton.disabled = !file;
    errorMessage.hidden = true;
    results.hidden = true;
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const file = fileInput.files[0];
    if (!file) {
      errorMessage.textContent = "Vui lòng chọn CV PDF hoặc DOCX.";
      errorMessage.hidden = false;
      return;
    }

    const extension = file.name.split(".").pop().toLowerCase();
    if (!["pdf", "docx"].includes(extension)) {
      errorMessage.textContent = "Chỉ hỗ trợ CV định dạng PDF hoặc DOCX.";
      errorMessage.hidden = false;
      return;
    }
    if (file.size === 0) {
      errorMessage.textContent = "File CV đang rỗng. Vui lòng chọn file có nội dung.";
      errorMessage.hidden = false;
      return;
    }
    if (file.size > MAX_CV_SIZE) {
      errorMessage.textContent = "CV vượt quá giới hạn 5 MB.";
      errorMessage.hidden = false;
      return;
    }

    errorMessage.hidden = true;
    results.hidden = true;
    submitButton.disabled = true;
    submitButton.textContent = "Đang phân tích...";
    form.setAttribute("aria-busy", "true");

    try {
      const headers = {};
      const token = localStorage.getItem("careerhub_token");
      if (token) headers.Authorization = `Bearer ${token}`;

      const body = new FormData();
      body.append("file", file);
      const response = await fetch(CV_ANALYSIS_URL, {
        method: "POST",
        headers,
        body,
      });

      let data;
      try {
        data = await response.json();
      } catch {
        throw new Error("Máy chủ trả về dữ liệu không hợp lệ.");
      }

      if (!response.ok) {
        throw new Error(getCVErrorMessage(data, response));
      }

      renderCVResult(data);
    } catch (error) {
      errorMessage.textContent = error.message || "Không thể phân tích CV. Vui lòng thử lại.";
      errorMessage.hidden = false;
    } finally {
      submitButton.disabled = !fileInput.files.length;
      submitButton.textContent = "Phân tích CV";
      form.removeAttribute("aria-busy");
    }
  });
});
