document.addEventListener("DOMContentLoaded", () => {
  const user = AuthGuard.requireRoles(["student"]);
  if (!user) return;

  const form = document.getElementById("application-form");
  const jobSelect = document.getElementById("job-select");
  const jobsHint = document.getElementById("jobs-hint");
  const cvInput = document.getElementById("cv-file");
  const cvFileName = document.getElementById("cv-file-name");
  const cvHint = document.getElementById("cv-hint");
  const feedback = document.getElementById("application-feedback");
  const submitButton = document.getElementById("submit-application");
  const listFeedback = document.getElementById("list-feedback");
  const applicationsList = document.getElementById("applications-list");
  const applicationsTable = document.getElementById("applications-table-wrap");
  const applicationCount = document.getElementById("application-count");
  const MAX_CV_SIZE = 5 * 1024 * 1024;
  const MIME_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  };
  const STATUS_LABELS = {
    pending: { label: "Chờ", className: "status-pending" },
    reviewed: { label: "Đã xem", className: "status-reviewed" },
    accepted: { label: "Được nhận", className: "status-accepted" },
    rejected: { label: "Từ chối", className: "status-rejected" },
    withdrawn: { label: "Đã rút", className: "status-withdrawn" },
  };

  function setFeedback(message, type = "") {
    feedback.textContent = message;
    feedback.className = `form-feedback${type ? ` is-${type}` : ""}`;
  }

  function appendOption(label, value = "", disabled = false) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = label;
    option.disabled = disabled;
    jobSelect.append(option);
    return option;
  }

  async function loadJobs() {
    jobSelect.replaceChildren();
    jobSelect.disabled = true;
    appendOption("Đang tải danh sách công việc...", "", true);
    try {
      const response = await fetch("/jobs/?page=1&limit=100");
      const result = await response.json();
      if (!response.ok) {
        throw new Error(result?.detail || "Không tải được danh sách công việc.");
      }
      const jobs = Array.isArray(result?.items) ? result.items : [];
      jobSelect.replaceChildren();
      appendOption("Chọn công việc muốn ứng tuyển", "", true);

      if (jobs.length === 0) {
        appendOption("Hiện chưa có công việc đang tuyển", "", true);
        jobsHint.textContent = "Bạn hãy quay lại sau khi có tin tuyển dụng phù hợp.";
        return;
      }

      jobs.forEach((job) => {
        const title = job.title || `Tin tuyển dụng #${job.job_id}`;
        const details = [job.location, job.job_type].filter(Boolean).join(" · ");
        appendOption(details ? `${title} — ${details}` : title, String(job.job_id));
      });

      const requestedJobId = new URLSearchParams(window.location.search).get("job_id");
      if (requestedJobId && jobs.some((job) => String(job.job_id) === requestedJobId)) {
        jobSelect.value = requestedJobId;
      }
    } catch (error) {
      jobSelect.replaceChildren();
      appendOption("Không tải được danh sách công việc", "", true);
      jobsHint.textContent = error.message || "Vui lòng tải lại trang để thử lại.";
    } finally {
      jobSelect.disabled = false;
    }
  }

  function formatDate(value) {
    if (!value) return "—";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "—";
    return new Intl.DateTimeFormat("vi-VN", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    }).format(date);
  }

  function createApplicationRow(application) {
    const row = document.createElement("tr");

    const jobCell = document.createElement("td");
    const title = document.createElement("span");
    title.className = "job-title-cell";
    title.textContent = application.job_title || `Tin tuyển dụng #${application.job_id}`;
    const jobId = document.createElement("span");
    jobId.className = "job-id-cell";
    jobId.textContent = `Mã tin #${application.job_id}`;
    jobCell.append(title, jobId);

    const dateCell = document.createElement("td");
    dateCell.textContent = formatDate(application.applied_at);

    const coverCell = document.createElement("td");
    const coverPreview = document.createElement("span");
    coverPreview.className = "cover-preview";
    coverPreview.textContent = application.cover_letter || "Chưa gửi thư giới thiệu";
    coverCell.append(coverPreview);

    const statusCell = document.createElement("td");
    const status = STATUS_LABELS[application.status] || {
      label: application.status || "Không xác định",
      className: "status-withdrawn",
    };
    const badge = document.createElement("span");
    badge.className = `status-badge ${status.className}`;
    badge.textContent = status.label;
    statusCell.append(badge);

    const actionCell = document.createElement("td");
    if (application.status === "pending") {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "withdraw-button";
      button.textContent = "Rút đơn";
      button.setAttribute("aria-label", `Rút đơn ứng tuyển ${title.textContent}`);
      button.addEventListener("click", () => withdrawApplication(application.id, button));
      actionCell.append(button);
    } else {
      actionCell.textContent = "—";
    }

    row.append(jobCell, dateCell, coverCell, statusCell, actionCell);
    return row;
  }

  async function loadApplications() {
    listFeedback.className = "list-feedback";
    listFeedback.textContent = "Đang tải đơn ứng tuyển...";
    listFeedback.hidden = false;
    applicationsTable.hidden = true;
    applicationsList.replaceChildren();

    try {
      const result = await api.get("/applications/my");
      const applications = Array.isArray(result) ? result : [];
      applicationCount.textContent = `${applications.length} đơn`;

      if (applications.length === 0) {
        listFeedback.textContent = "Bạn chưa gửi đơn ứng tuyển nào. Hãy chọn một công việc phù hợp ở biểu mẫu phía trên.";
        return;
      }

      applications.forEach((application) => {
        applicationsList.append(createApplicationRow(application));
      });
      listFeedback.hidden = true;
      applicationsTable.hidden = false;
    } catch (error) {
      listFeedback.className = "list-feedback is-error";
      listFeedback.textContent = error.message || "Không tải được danh sách đơn ứng tuyển.";
      applicationCount.textContent = "— đơn";
    }
  }

  async function withdrawApplication(applicationId, button) {
    button.disabled = true;
    button.textContent = "Đang rút...";
    try {
      await api.post(`/applications/${applicationId}/withdraw`);
      await loadApplications();
    } catch (error) {
      button.disabled = false;
      button.textContent = "Rút đơn";
      setFeedback(error.message || "Không thể rút đơn ứng tuyển.", "error");
    }
  }

  cvInput.addEventListener("change", () => {
    cvInput.setCustomValidity("");
    const file = cvInput.files?.[0];
    cvHint.className = "field-hint";
    if (!file) {
      cvFileName.textContent = "Chọn CV từ thiết bị";
      cvHint.textContent = "CV sẽ được gửi kèm hồ sơ ứng tuyển.";
      return;
    }

    cvFileName.textContent = file.name;
    const extension = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
    if (!MIME_TYPES[extension] || file.type !== MIME_TYPES[extension]) {
      cvHint.textContent = "Chỉ nhận CV PDF hoặc DOCX hợp lệ.";
      cvHint.className = "field-hint is-error";
      cvInput.setCustomValidity("Chọn file PDF hoặc DOCX và đúng MIME type.");
      return;
    }
    if (file.size > MAX_CV_SIZE) {
      cvHint.textContent = "CV vượt quá giới hạn 5 MB.";
      cvHint.className = "field-hint is-error";
      cvInput.setCustomValidity("CV không được vượt quá 5 MB.");
      return;
    }

    cvInput.setCustomValidity("");
    cvHint.textContent = `${(file.size / (1024 * 1024)).toFixed(2)} MB · File sẵn sàng gửi.`;
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    setFeedback("");

    const file = cvInput.files?.[0];
    if (!jobSelect.value) {
      setFeedback("Vui lòng chọn công việc muốn ứng tuyển.", "error");
      jobSelect.focus();
      return;
    }
    if (!form.reportValidity() || !file) return;

    const body = new FormData();
    body.append("cv", file);
    body.append("cover_letter", document.getElementById("cover-letter").value.trim());

    submitButton.disabled = true;
    submitButton.innerHTML = 'Đang gửi hồ sơ <span aria-hidden="true">…</span>';
    try {
      await api.post(`/jobs/${jobSelect.value}/applications`, body);
      form.reset();
      cvFileName.textContent = "Chọn CV từ thiết bị";
      cvHint.className = "field-hint";
      cvHint.textContent = "CV sẽ được gửi kèm hồ sơ ứng tuyển.";
      setFeedback("Hồ sơ đã được gửi thành công. Trạng thái đơn hiện là Chờ.", "success");
      await loadApplications();
    } catch (error) {
      setFeedback(error.message || "Không thể gửi hồ sơ ứng tuyển.", "error");
    } finally {
      submitButton.disabled = false;
      submitButton.innerHTML = 'Gửi hồ sơ <span aria-hidden="true">→</span>';
    }
  });

  loadJobs();
  loadApplications();
});
