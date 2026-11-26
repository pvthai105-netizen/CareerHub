document.addEventListener("DOMContentLoaded", () => {
  const user = AuthGuard.requireRoles(["employer"]);
  if (!user) return;

  const jobSelect = document.getElementById("job-select");
  const statusFilter = document.getElementById("status-filter");
  const feedback = document.getElementById("applicants-feedback");
  const tableWrap = document.getElementById("applicants-table-wrap");
  const list = document.getElementById("applicants-list");
  const count = document.getElementById("applicant-count");
  const statusLabels = {
    pending: ["Chờ", "status-pending"],
    reviewed: ["Đã xem", "status-reviewed"],
    interview: ["Phỏng vấn", "status-interview"],
    accepted: ["Đã nhận", "status-accepted"],
    rejected: ["Từ chối", "status-rejected"],
    withdrawn: ["Đã rút", "status-withdrawn"],
  };

  function setFeedback(message, isError = false) {
    feedback.textContent = message;
    feedback.classList.toggle("is-error", isError);
    feedback.hidden = false;
    tableWrap.hidden = true;
  }

  function appendCell(row, content, className = "") {
    const cell = document.createElement("td");
    if (className) cell.className = className;
    if (content instanceof Node) cell.append(content);
    else cell.textContent = content;
    row.append(cell);
    return cell;
  }

  function createStatusBadge(status) {
    const [label, className] = statusLabels[status] || [status || "Không xác định", ""];
    const badge = document.createElement("span");
    badge.className = `status-badge ${className}`;
    badge.textContent = label;
    return badge;
  }

  function createApplicantRow(applicant) {
    const row = document.createElement("tr");
    const identity = document.createElement("div");
    const name = document.createElement("span");
    name.className = "candidate-name";
    name.textContent = applicant.student_name || "Ứng viên";
    const email = document.createElement("span");
    email.className = "candidate-contact";
    email.textContent = applicant.student_email;
    identity.append(name, email);
    if (applicant.student_phone) {
      const phone = document.createElement("span");
      phone.className = "candidate-contact";
      phone.textContent = applicant.student_phone;
      identity.append(phone);
    }
    appendCell(row, identity);
    appendCell(row, new Intl.DateTimeFormat("vi-VN", { dateStyle: "medium" }).format(new Date(applicant.applied_at)));

    const letter = document.createElement("div");
    letter.className = "candidate-letter";
    letter.textContent = applicant.cover_letter || "Không có thư giới thiệu";
    appendCell(row, letter);

    const cvActions = document.createElement("div");
    cvActions.className = "candidate-actions";
    if (applicant.has_cv) {
      const viewButton = document.createElement("button");
      viewButton.className = "cv-button";
      viewButton.type = "button";
      viewButton.textContent = "Xem CV";
      viewButton.addEventListener("click", () => openCv(applicant, false, viewButton));
      const downloadButton = document.createElement("button");
      downloadButton.className = "cv-button";
      downloadButton.type = "button";
      downloadButton.textContent = "Tải CV";
      downloadButton.addEventListener("click", () => openCv(applicant, true, downloadButton));
      cvActions.append(viewButton, downloadButton);
    } else {
      cvActions.textContent = "Chưa có CV";
    }
    appendCell(row, cvActions);

    appendCell(row, createStatusBadge(applicant.status));
    const statusCell = document.createElement("td");
    const nextStatuses = applicant.status === "pending"
      ? [["interview", "Phỏng vấn"], ["rejected", "Từ chối"]]
      : applicant.status === "interview"
        ? [["accepted", "Đã nhận"], ["rejected", "Từ chối"]]
        : [];
    if (nextStatuses.length) {
      const controls = document.createElement("div");
      controls.className = "status-control";
      const select = document.createElement("select");
      select.className = "status-select";
      const placeholder = document.createElement("option");
      placeholder.value = "";
      placeholder.textContent = "Chọn trạng thái";
      select.append(placeholder);
      nextStatuses.forEach(([value, label]) => {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = label;
        select.append(option);
      });
      const button = document.createElement("button");
      button.className = "status-save";
      button.type = "button";
      button.textContent = "Cập nhật";
      button.disabled = true;
      select.addEventListener("change", () => { button.disabled = !select.value; });
      button.addEventListener("click", () => updateStatus(applicant, select.value, button));
      controls.append(select, button);
      statusCell.append(controls);
    } else {
      statusCell.append(createStatusBadge(applicant.status));
    }
    row.append(statusCell);
    return row;
  }

  async function openCv(applicant, download, button) {
    button.disabled = true;
    const viewWindow = download ? null : window.open("about:blank", "_blank");
    try {
      const response = await fetch(`/api/jobs/${applicant.job_id}/applications/${applicant.id}/cv`, {
        headers: { Authorization: `Bearer ${Auth.getToken()}` },
      });
      if (!response.ok) {
        let message = "Không tải được CV.";
        try { message = (await response.json())?.detail || message; } catch (_) { /* Keep fallback. */ }
        throw new Error(message);
      }
      const blob = await response.blob();
      const blobUrl = URL.createObjectURL(blob);
      if (download) {
        const anchor = document.createElement("a");
        anchor.href = blobUrl;
        const extension = blob.type === "application/pdf" ? ".pdf" : ".docx";
        anchor.download = `CV-application-${applicant.id}${extension}`;
        anchor.click();
        setTimeout(() => URL.revokeObjectURL(blobUrl), 1000);
      } else {
        if (viewWindow) {
          viewWindow.location = blobUrl;
        } else {
          window.location.href = blobUrl;
        }
        setTimeout(() => URL.revokeObjectURL(blobUrl), 60000);
      }
    } catch (error) {
      if (viewWindow) viewWindow.close();
      setFeedback(error.message || "Không tải được CV.", true);
    } finally {
      button.disabled = false;
    }
  }

  async function updateStatus(applicant, newStatus, button) {
    if (!newStatus) return;
    button.disabled = true;
    try {
      await apiFetch(`/jobs/${applicant.job_id}/applications/${applicant.id}/status`, {
        method: "PATCH",
        body: { status: newStatus },
      });
      await loadApplicants();
      feedback.textContent = "Đã cập nhật trạng thái hồ sơ.";
      feedback.classList.remove("is-error");
      feedback.hidden = false;
    } catch (error) {
      setFeedback(error.message || "Không thể cập nhật trạng thái.", true);
      button.disabled = false;
    }
  }

  async function loadApplicants() {
    const jobId = jobSelect.value;
    if (!jobId) {
      count.textContent = "0 ứng viên";
      list.replaceChildren();
      setFeedback("Chọn tin tuyển dụng để xem hồ sơ ứng tuyển.");
      return;
    }
    const params = new URLSearchParams();
    if (statusFilter.value) params.set("status", statusFilter.value);
    const query = params.toString();
    setFeedback("Đang tải hồ sơ ứng tuyển...");
    try {
      const applicants = await api.get(`/jobs/${jobId}/applications${query ? `?${query}` : ""}`);
      list.replaceChildren();
      count.textContent = `${applicants.length} ứng viên`;
      if (applicants.length === 0) {
        setFeedback("Chưa có ứng viên phù hợp với bộ lọc này.");
        return;
      }
      applicants.forEach((applicant) => list.append(createApplicantRow(applicant)));
      feedback.hidden = true;
      tableWrap.hidden = false;
    } catch (error) {
      count.textContent = "— ứng viên";
      setFeedback(error.message || "Không tải được danh sách ứng viên.", true);
    }
  }

  async function loadJobs() {
    setFeedback("Đang tải tin tuyển dụng...");
    try {
      const result = await api.get("/jobs/my-jobs?skip=0&limit=100");
      const jobs = Array.isArray(result?.items) ? result.items : [];
      jobSelect.replaceChildren();
      const placeholder = document.createElement("option");
      placeholder.value = "";
      placeholder.textContent = jobs.length ? "Chọn tin tuyển dụng" : "Bạn chưa có tin tuyển dụng";
      jobSelect.append(placeholder);
      jobs.forEach((job) => {
        const option = document.createElement("option");
        option.value = job.job_id;
        option.textContent = `${job.title} · #${job.job_id}`;
        jobSelect.append(option);
      });
      jobSelect.disabled = jobs.length === 0;
      statusFilter.disabled = jobs.length === 0;
      const requestedId = new URLSearchParams(window.location.search).get("job_id");
      if (requestedId && jobs.some((job) => String(job.job_id) === requestedId)) {
        jobSelect.value = requestedId;
      } else if (jobs.length) {
        jobSelect.value = String(jobs[0].job_id);
      }
      await loadApplicants();
    } catch (error) {
      jobSelect.disabled = true;
      statusFilter.disabled = true;
      setFeedback(error.message || "Không tải được tin tuyển dụng.", true);
    }
  }

  jobSelect.addEventListener("change", loadApplicants);
  statusFilter.addEventListener("change", loadApplicants);
  loadJobs();
});
