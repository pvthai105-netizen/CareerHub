/**
 * company_detail.js - Nạp thông tin công ty công khai và tin tuyển dụng đang mở
 */

document.addEventListener("DOMContentLoaded", async () => {
  // Lấy id công ty từ URL (?id=1)
  const urlParams = new URLSearchParams(window.location.search);
  const profileId = urlParams.get("id") || 1; // Mặc định ID = 1 nếu không truyền

  const compLogo = document.getElementById("comp-logo");
  const compName = document.getElementById("comp-name");
  const compAddress = document.getElementById("comp-address");
  const compWebsite = document.getElementById("comp-website");
  const compDescription = document.getElementById("comp-description");
  const compTaxCode = document.getElementById("comp-tax-code");
  const compEmail = document.getElementById("comp-email");
  const compPhone = document.getElementById("comp-phone");
  const compContactPerson = document.getElementById("comp-contact-person");
  const compJobsCount = document.getElementById("comp-jobs-count");
  const jobsBadge = document.getElementById("jobs-badge");
  const jobsListContainer = document.getElementById("company-jobs-list");
  const emptyState = document.getElementById("jobs-empty-state");

  // Format mức lương hiển thị thân thiện
  function formatSalary(min, max) {
    if (!min && !max) return "Thỏa thuận";
    const toMil = (v) => (v / 1_000_000).toLocaleString("vi-VN");
    if (min && max) return `${toMil(min)} – ${toMil(max)} triệu / tháng`;
    if (min) return `Từ ${toMil(min)} triệu / tháng`;
    return `Đến ${toMil(max)} triệu / tháng`;
  }

  // Chuyển mã JobType sang tiếng Việt
  const jobTypeLabels = {
    FULL_TIME: "Toàn thời gian",
    PART_TIME: "Bán thời gian",
    INTERNSHIP: "Thực tập",
    REMOTE: "Làm từ xa",
  };

  try {
    // 1. Lấy thông tin công ty theo profileId
    const company = await api.get(`/employers/${profileId}`);
    if (company) {
      document.title = `${company.company_name} – CareerHub`;
      compName.textContent = company.company_name;
      if (company.logo_url) compLogo.src = company.logo_url;
      if (company.address) compAddress.textContent = company.address;
      if (company.tax_code) compTaxCode.textContent = company.tax_code;
      if (company.email) compEmail.textContent = company.email;
      if (company.phone) compPhone.textContent = company.phone;
      if (company.contact_name) compContactPerson.textContent = company.contact_name;
      if (company.description) compDescription.textContent = company.description;

      if (company.company_website) {
        compWebsite.href = company.company_website;
        compWebsite.textContent = company.company_website.replace(/^https?:\/\//, "");
      }
    }

    // 2. Lấy danh sách tin tuyển dụng của công ty
    let jobs = [];
    try {
      jobs = await api.get(`/employers/${profileId}/jobs`);
    } catch (e) {
      // Fallback: nếu chưa có route riêng, lọc từ API jobs chung
      const res = await api.get(`/jobs/?limit=50`);
      if (res && res.items) {
        jobs = res.items.filter((j) => j.employer_id === company.user_id);
      }
    }

    // Hiển thị số lượng tin
    const count = Array.isArray(jobs) ? jobs.length : 0;
    compJobsCount.textContent = `${count} vị trí đang tuyển`;
    jobsBadge.textContent = `${count} công việc`;

    if (count === 0) {
      jobsListContainer.innerHTML = "";
      emptyState.style.display = "block";
      return;
    }

    emptyState.style.display = "none";
    jobsListContainer.innerHTML = jobs
      .map(
        (job) => `
        <div class="public-job-card">
          <div class="job-card-info">
            <h3 class="job-card-title">${escapeHtml(job.title)}</h3>
            <div class="job-card-meta">
              <span class="job-type-badge">${jobTypeLabels[job.job_type] || job.job_type}</span>
              <span>📍 ${escapeHtml(job.location)}</span>
              <span>📅 Hạn: ${job.deadline ? new Date(job.deadline).toLocaleDateString("vi-VN") : "Đang mở"}</span>
            </div>
            <div class="job-card-salary">${formatSalary(job.salary_min, job.salary_max)}</div>
          </div>
          <a href="home.html?job_id=${job.job_id || job.id}" class="btn btn-primary" style="white-space: nowrap;">
            Ứng tuyển ngay
          </a>
        </div>
      `
      )
      .join("");
  } catch (err) {
    jobsListContainer.innerHTML = `<div style="color:var(--error); padding: 20px;">Không thể tải dữ liệu công ty: ${err.message}</div>`;
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
});