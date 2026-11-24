const AI_JOB_SEARCH_URL = "http://127.0.0.1:8000/api/jobs/ai-search";
const JOB_TYPE_LABELS = {
  FULL_TIME: "Toàn thời gian",
  PART_TIME: "Bán thời gian",
  INTERNSHIP: "Thực tập",
  REMOTE: "Làm từ xa",
  CONTRACT: "Hợp đồng",
};

function escapeHTML(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function formatSalary(job) {
  const formatMillions = (amount) =>
    new Intl.NumberFormat("vi-VN", { maximumFractionDigits: 2 }).format(Number(amount) / 1_000_000);
  const hasMinimum = job.salary_min != null;
  const hasMaximum = job.salary_max != null;

  if (hasMinimum && hasMaximum) {
    return `${formatMillions(job.salary_min)} – ${formatMillions(job.salary_max)} triệu / tháng`;
  }
  if (hasMinimum) return `Từ ${formatMillions(job.salary_min)} triệu / tháng`;
  if (hasMaximum) return `Đến ${formatMillions(job.salary_max)} triệu / tháng`;
  return "Thỏa thuận";
}

function renderRecommendation(item, index) {
  const job = item.job;
  const jobId = Number(job.job_id);
  const matchPercentage = Math.min(100, Math.max(0, Number(item.match_percentage) || 0));
  const company = job.employer_id ? `Employer #${job.employer_id}` : "Nhà tuyển dụng";
  const jobType = JOB_TYPE_LABELS[job.job_type] || job.job_type || "";
  const reasons = Array.isArray(item.reasons) ? item.reasons : [];
  const reasonsHTML = reasons.length
    ? reasons.map((reason) => `<li>${escapeHTML(reason)}</li>`).join("")
    : "<li>Chưa có thông tin lý do phù hợp.</li>";

  return `
    <article class="ai-recommendation">
      <div class="ai-recommendation-header">
        <span class="ai-rank">#${index + 1} gợi ý</span>
        <span class="ai-match">${matchPercentage}% phù hợp</span>
      </div>
      <small class="ai-job-company">${escapeHTML(company)}</small>
      <h2 class="ai-job-title">
        <a href="./home.html#/job/${jobId}">${escapeHTML(job.title)}</a>
      </h2>
      <p class="ai-job-meta">${escapeHTML(job.location)} · ${escapeHTML(jobType)} · ${escapeHTML(job.industry)}</p>
      <p class="ai-job-salary">${escapeHTML(formatSalary(job))}</p>
      <div class="ai-match-reasons">
        <h3>Lý do phù hợp</h3>
        <ul>${reasonsHTML}</ul>
      </div>
      <a class="ai-detail-link" href="./home.html#/job/${jobId}">Xem chi tiết tin tuyển dụng →</a>
    </article>
  `;
}

function getErrorMessage(data, status) {
  if (status === 401) {
    return "Vui lòng đăng nhập bằng tài khoản sinh viên để sử dụng tính năng này.";
  }
  if (status === 403) {
    return "Tính năng tìm việc bằng AI chỉ dành cho tài khoản sinh viên.";
  }

  const detail = data?.detail ?? data?.message;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    return detail[0].msg || "Thông tin tìm kiếm chưa hợp lệ.";
  }
  return `Không thể tìm việc lúc này (mã lỗi ${status}).`;
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("ai-search-form");
  const queryInput = document.getElementById("ai-search-query");
  const submitButton = document.getElementById("ai-search-submit");
  const status = document.getElementById("ai-search-status");
  const results = document.getElementById("ai-search-results");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const query = queryInput.value.trim();

    if (query.length < 3) {
      status.className = "ai-search-status error";
      status.textContent = "Vui lòng nhập ít nhất 3 ký tự mô tả nhu cầu.";
      queryInput.focus();
      return;
    }

    submitButton.disabled = true;
    submitButton.textContent = "Đang phân tích...";
    form.setAttribute("aria-busy", "true");
    status.className = "ai-search-status";
    status.textContent = "AI đang phân tích nhu cầu của bạn...";
    results.innerHTML = "";

    try {
      const headers = { "Content-Type": "application/json" };
      const token = localStorage.getItem("careerhub_token");
      if (token) headers.Authorization = `Bearer ${token}`;

      const response = await fetch(AI_JOB_SEARCH_URL, {
        method: "POST",
        headers,
        body: JSON.stringify({ query }),
      });

      let data;
      try {
        data = await response.json();
      } catch {
        throw new Error("Máy chủ trả về dữ liệu không hợp lệ.");
      }

      if (!response.ok) {
        throw new Error(getErrorMessage(data, response.status));
      }
      if (!Array.isArray(data.items)) {
        throw new Error("Danh sách gợi ý việc làm không hợp lệ.");
      }

      const items = data.items.slice(0, 10);
      if (items.length === 0) {
        status.textContent = "Chưa tìm thấy việc làm phù hợp. Hãy thử mô tả nhu cầu khác nhé.";
        results.innerHTML = '<div class="ai-search-empty">Chưa có tin tuyển dụng phù hợp với nhu cầu của bạn.</div>';
        return;
      }

      status.textContent = `Đây là ${items.length} việc làm phù hợp nhất với nhu cầu của bạn${data.used_fallback ? " (xếp hạng theo từ khóa)" : ""}.`;
      results.innerHTML = items.map(renderRecommendation).join("");
    } catch (error) {
      status.className = "ai-search-status error";
      status.textContent = error.message || "Không thể tìm việc lúc này. Vui lòng thử lại.";
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = "Tìm việc phù hợp";
      form.removeAttribute("aria-busy");
    }
  });
});
