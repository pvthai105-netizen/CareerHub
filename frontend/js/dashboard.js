/**
 * ==========================================================================
 * CareerHub - Dashboard Client Logic
 * Handles data fetching, Chart.js rendering, status mapping, and UI interactions
 * for Employer, Admin, and Student dashboards.
 * ==========================================================================
 */

const Dashboard = {
  // Chart.js instances cache to destroy old charts on re-render
  charts: {},

  // Format number: e.g. 12480 -> "12.480"
  formatNumber(val) {
    if (val === null || val === undefined || isNaN(val)) return "0";
    return Number(val).toLocaleString("vi-VN");
  },

  // Format date: "2026-11-10T14:30:00" -> "10/11/2026"
  formatDate(dateStr) {
    if (!dateStr) return "—";
    try {
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return dateStr;
      const day = String(d.getDate()).padStart(2, "0");
      const month = String(d.getMonth() + 1).padStart(2, "0");
      const year = d.getFullYear();
      return `${day}/${month}/${year}`;
    } catch {
      return dateStr;
    }
  },

  // Format short date: "2026-11-05" -> "5/11"
  formatShortDate(dateStr) {
    if (!dateStr) return "";
    try {
      const parts = dateStr.split("-");
      if (parts.length === 3) {
        return `${parseInt(parts[2], 10)}/${parseInt(parts[1], 10)}`;
      }
      return dateStr;
    } catch {
      return dateStr;
    }
  },

  // Format month label: "2026-06" -> "T6"
  formatMonthLabel(dateStr) {
    if (!dateStr) return "";
    try {
      const parts = dateStr.split("-");
      if (parts.length >= 2) {
        return `T${parseInt(parts[1], 10)}`;
      }
      return dateStr;
    } catch {
      return dateStr;
    }
  },

  // Relative time format: "2 phút trước", "1 giờ trước"
  formatRelativeTime(dateStr) {
    if (!dateStr) return "—";
    try {
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return dateStr;
      const diffMs = Date.now() - d.getTime();
      const diffMin = Math.floor(diffMs / (1000 * 60));
      if (diffMin < 1) return "Vừa xong";
      if (diffMin < 60) return `${diffMin} phút trước`;
      const diffHours = Math.floor(diffMin / 60);
      if (diffHours < 24) return `${diffHours} giờ trước`;
      const diffDays = Math.floor(diffHours / 24);
      if (diffDays <= 7) return `${diffDays} ngày trước`;
      return this.formatDate(dateStr);
    } catch {
      return dateStr;
    }
  },

  // Map status code to Vietnamese label and CSS class
  getStatusBadge(status) {
    const s = String(status || "").toLowerCase();
    switch (s) {
      case "pending":
        return { label: "Đang chờ", class: "badge-pending" };
      case "reviewed":
        return { label: "Đã xem", class: "badge-reviewed" };
      case "interview":
        return { label: "Phỏng vấn", class: "badge-interview" };
      case "accepted":
        return { label: "Được nhận", class: "badge-accepted" };
      case "rejected":
        return { label: "Từ chối", class: "badge-rejected" };
      case "active":
        return { label: "Đang hoạt động", class: "badge-success" };
      case "closed":
        return { label: "Đã đóng", class: "badge-error" };
      case "draft":
        return { label: "Bản nháp", class: "badge-warning" };
      default:
        return { label: status || "Không xác định", class: "badge-warning" };
    }
  },

  // Destroy existing Chart.js instance by canvas ID
  destroyChart(id) {
    if (this.charts[id]) {
      this.charts[id].destroy();
      delete this.charts[id];
    }
  },

  // Setup common logout handler
  setupLogout() {
    const logoutBtn = document.getElementById("btnLogout");
    if (logoutBtn) {
      logoutBtn.addEventListener("click", () => {
        Auth.clear();
        window.location.href = "login.html";
      });
    }
  },

  // Render error message inside a container
  renderError(containerId, message, retryFn) {
    const el = document.getElementById(containerId);
    if (!el) return;
    el.innerHTML = `
      <div class="dash-error-banner">
        <span>⚠️ ${message}</span>
        ${retryFn ? '<button class="dash-btn-outline" style="padding: 6px 12px; font-size: 12px;" onclick="' + retryFn + '()">Thử lại</button>' : ""}
      </div>
    `;
  },

  // =========================================================================
  // 1. NHÀ TUYỂN DỤNG (EMPLOYER DASHBOARD)
  // =========================================================================
  async initEmployerDashboard() {
    const user = AuthGuard.requireRoles(["employer"]);
    if (!user) return;
    this.setupLogout();

    const mainContainer = document.getElementById("employerContent");
    try {
      const data = await api.get("/dashboard/employer");

      // 1. Render KPIs
      const kpi = data.kpi || {};
      const elTotalJobs = document.getElementById("kpiTotalJobs");
      const elActiveJobs = document.getElementById("kpiActiveJobs");
      const elTotalApplicants = document.getElementById("kpiTotalApplicants");
      const elNewApplicants = document.getElementById("kpiNewApplicants");

      if (elTotalJobs) elTotalJobs.textContent = this.formatNumber(kpi.total_jobs);
      if (elActiveJobs) elActiveJobs.textContent = this.formatNumber(kpi.active_jobs);
      if (elTotalApplicants) elTotalApplicants.textContent = this.formatNumber(kpi.total_applicants);
      if (elNewApplicants) elNewApplicants.textContent = this.formatNumber(kpi.new_applicants_7d);

      // 2. Render Applications by Date (Bar Chart)
      const chartCanvas = document.getElementById("employerApplicationsChart");
      if (chartCanvas && typeof Chart !== "undefined") {
        this.destroyChart("employerApplicationsChart");
        const dateItems = data.applications_by_date || [];
        const labels = dateItems.map((item) => this.formatShortDate(item.date));
        const counts = dateItems.map((item) => item.count);

        const ctx = chartCanvas.getContext("2d");
        this.charts["employerApplicationsChart"] = new Chart(ctx, {
          type: "bar",
          data: {
            labels: labels.length > 0 ? labels : ["T2", "T3", "T4", "T5", "T6", "T7", "CN"],
            datasets: [
              {
                label: "Lượt ứng tuyển",
                data: counts.length > 0 ? counts : [0, 0, 0, 0, 0, 0, 0],
                backgroundColor: "#8176B5",
                hoverBackgroundColor: "#6255A5",
                borderRadius: 6,
                borderSkipped: false,
                barThickness: 28,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: {
                backgroundColor: "#292642",
                titleFont: { family: "Inter", size: 12 },
                bodyFont: { family: "Inter", size: 13, weight: "bold" },
                padding: 10,
                cornerRadius: 8,
                callbacks: {
                  label: (context) => ` ${context.parsed.y} ứng viên`,
                },
              },
            },
            scales: {
              x: {
                grid: { display: false },
                ticks: { font: { family: "Inter", size: 12 }, color: "#77738B" },
              },
              y: {
                beginAtZero: true,
                grid: { color: "#E8E5F0" },
                ticks: {
                  precision: 0,
                  font: { family: "Inter", size: 12 },
                  color: "#77738B",
                },
              },
            },
          },
        });
      }

      // 3. Render Status Distribution Progress Bars
      const percentages = data.status_percentages || {};
      const statusDist = data.status_distribution || {};

      const renderStatusItem = (statusKey, fillElId, valElId) => {
        const fillEl = document.getElementById(fillElId);
        const valEl = document.getElementById(valElId);
        const pct = percentages[statusKey] !== undefined ? percentages[statusKey] : 0;
        const count = statusDist[statusKey] !== undefined ? statusDist[statusKey] : 0;
        if (fillEl) fillEl.style.width = `${pct}%`;
        if (valEl) valEl.textContent = `${pct}% (${count})`;
      };

      renderStatusItem("pending", "barPendingFill", "valPending");
      renderStatusItem("reviewed", "barReviewedFill", "valReviewed");
      renderStatusItem("interview", "barInterviewFill", "valInterview");
      renderStatusItem("accepted", "barAcceptedFill", "valAccepted");

      // 4. Render Recent Applicants List
      const applicantsListEl = document.getElementById("recentApplicantsList");
      if (applicantsListEl) {
        const recent = data.recent_applicants || [];
        if (recent.length === 0) {
          applicantsListEl.innerHTML = `
            <div class="dash-empty-state">
              <span class="dash-empty-icon">📂</span>
              <p>Chưa có ứng viên nào nộp hồ sơ gần đây</p>
            </div>
          `;
        } else {
          applicantsListEl.innerHTML = recent
            .slice(0, 6)
            .map((item) => {
              const badge = this.getStatusBadge(item.status);
              return `
              <div class="dash-list-item">
                <div class="dash-list-info">
                  <span class="dash-list-title">${escapeHtml(item.student_name)}</span>
                  <span class="dash-list-sub">${escapeHtml(item.job_title)} · ${this.formatRelativeTime(item.applied_at)}</span>
                </div>
                <span class="badge ${badge.class}">${badge.label}</span>
              </div>
            `;
            })
            .join("");
        }
      }

      // 5. Render Applications by Job (Tin tuyển dụng gần đây)
      const jobListEl = document.getElementById("applicationsByJobList");
      if (jobListEl) {
        const jobs = data.applications_by_job || [];
        if (jobs.length === 0) {
          jobListEl.innerHTML = `
            <div class="dash-empty-state">
              <span class="dash-empty-icon">📝</span>
              <p>Chưa có tin tuyển dụng nào</p>
            </div>
          `;
        } else {
          jobListEl.innerHTML = jobs
            .slice(0, 6)
            .map((job) => {
              const badge = this.getStatusBadge(job.status);
              return `
              <div class="dash-list-item">
                <div class="dash-list-info">
                  <span class="dash-list-title">${escapeHtml(job.title)}</span>
                  <span class="dash-list-sub">${job.total_applications} ứng viên</span>
                </div>
                <span class="badge ${badge.class}">${badge.label}</span>
              </div>
            `;
            })
            .join("");
        }
      }
    } catch (err) {
      console.error("Lỗi tải dashboard nhà tuyển dụng:", err);
      this.renderError("employerErrorSlot", err.message || "Không thể tải dữ liệu thống kê", "Dashboard.initEmployerDashboard");
    }
  },

  // =========================================================================
  // 2. QUẢN TRỊ VIÊN (ADMIN DASHBOARD)
  // =========================================================================
  async initAdminDashboard() {
    const user = AuthGuard.requireRoles(["admin"]);
    if (!user) return;
    this.setupLogout();

    try {
      const data = await api.get("/dashboard/admin");

      // 1. Render User & Job Stats
      const uStats = data.user_stats || {};
      const jStats = data.job_stats || {};

      const elTotalUsers = document.getElementById("kpiTotalUsers");
      const elStudentsSub = document.getElementById("kpiStudentsSub");
      const elEmployersCount = document.getElementById("kpiEmployersCount");
      const elAdminsSub = document.getElementById("kpiAdminsSub");
      const elTotalJobs = document.getElementById("kpiTotalJobs");
      const elActiveJobsSub = document.getElementById("kpiActiveJobsSub");
      const elDraftJobs = document.getElementById("kpiDraftJobs");

      if (elTotalUsers) elTotalUsers.textContent = this.formatNumber(uStats.total_users);
      if (elStudentsSub) elStudentsSub.textContent = `${this.formatNumber(uStats.students_count)} sinh viên`;
      if (elEmployersCount) elEmployersCount.textContent = this.formatNumber(uStats.employers_count);
      if (elAdminsSub) elAdminsSub.textContent = `${this.formatNumber(uStats.admins_count)} quản trị viên`;
      if (elTotalJobs) elTotalJobs.textContent = this.formatNumber(jStats.total_jobs);
      if (elActiveJobsSub) elActiveJobsSub.textContent = `${this.formatNumber(jStats.active_jobs)} đang hoạt động`;
      if (elDraftJobs) elDraftJobs.textContent = this.formatNumber(jStats.draft_jobs);

      // Cần xử lý card text
      const elActionDraftCount = document.getElementById("actionDraftCount");
      if (elActionDraftCount) {
        elActionDraftCount.textContent = `${jStats.draft_jobs || 0} tin tuyển dụng chờ duyệt cần kiểm tra hôm nay.`;
      }

      // 2. Render User Growth Chart (Smooth Line Chart with Area)
      const growthCanvas = document.getElementById("adminUserGrowthChart");
      if (growthCanvas && typeof Chart !== "undefined") {
        this.destroyChart("adminUserGrowthChart");
        const growthItems = data.user_growth || [];
        const labels = growthItems.map((item) => this.formatMonthLabel(item.date));
        const counts = growthItems.map((item) => item.count);

        const ctx = growthCanvas.getContext("2d");
        const gradient = ctx.createLinearGradient(0, 0, 0, 240);
        gradient.addColorStop(0, "rgba(98, 85, 165, 0.28)");
        gradient.addColorStop(1, "rgba(98, 85, 165, 0.0)");

        this.charts["adminUserGrowthChart"] = new Chart(ctx, {
          type: "line",
          data: {
            labels: labels.length > 0 ? labels : ["T6", "T7", "T8", "T9", "T10", "T11"],
            datasets: [
              {
                label: "Người dùng mới",
                data: counts.length > 0 ? counts : [0, 0, 0, 0, 0, 0],
                borderColor: "#6255A5",
                borderWidth: 3,
                backgroundColor: gradient,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: "#6255A5",
                pointBorderColor: "#FFFFFF",
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
              tooltip: {
                backgroundColor: "#292642",
                titleFont: { family: "Inter", size: 12 },
                bodyFont: { family: "Inter", size: 13, weight: "bold" },
                padding: 10,
                cornerRadius: 8,
                callbacks: {
                  label: (context) => ` ${context.parsed.y} thành viên mới`,
                },
              },
            },
            scales: {
              x: {
                grid: { display: false },
                ticks: { font: { family: "Inter", size: 12 }, color: "#77738B" },
              },
              y: {
                beginAtZero: true,
                grid: { color: "#E8E5F0" },
                ticks: {
                  precision: 0,
                  font: { family: "Inter", size: 12 },
                  color: "#77738B",
                },
              },
            },
          },
        });
      }

      // 3. Render Job Status Breakdown (Doughnut Chart & Progress Bars)
      const jobStatusCanvas = document.getElementById("adminJobStatusChart");
      const activeJobs = jStats.active_jobs || 0;
      const closedJobs = jStats.closed_jobs || 0;
      const draftJobs = jStats.draft_jobs || 0;
      const totalJobs = activeJobs + closedJobs + draftJobs || 1;

      if (jobStatusCanvas && typeof Chart !== "undefined") {
        this.destroyChart("adminJobStatusChart");
        const ctx = jobStatusCanvas.getContext("2d");
        this.charts["adminJobStatusChart"] = new Chart(ctx, {
          type: "doughnut",
          data: {
            labels: ["Đang hoạt động", "Đã đóng", "Chờ duyệt"],
            datasets: [
              {
                data: [activeJobs, closedJobs, draftJobs],
                backgroundColor: ["#6EAA87", "#77738B", "#E5B96F"],
                borderWidth: 0,
                hoverOffset: 4,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "70%",
            plugins: {
              legend: {
                position: "bottom",
                labels: {
                  font: { family: "Inter", size: 12 },
                  color: "#292642",
                  usePointStyle: true,
                  padding: 14,
                },
              },
              tooltip: {
                backgroundColor: "#292642",
                callbacks: {
                  label: (ctx) => ` ${ctx.label}: ${ctx.raw} tin (${Math.round((ctx.raw / totalJobs) * 100)}%)`,
                },
              },
            },
          },
        });
      }

      // Progress bars
      const pctActive = Math.round((activeJobs / totalJobs) * 100);
      const pctClosed = Math.round((closedJobs / totalJobs) * 100);
      const pctDraft = Math.round((draftJobs / totalJobs) * 100);

      const elBarActive = document.getElementById("barActiveJobsFill");
      const elValActive = document.getElementById("valActiveJobs");
      if (elBarActive) elBarActive.style.width = `${pctActive}%`;
      if (elValActive) elValActive.textContent = `${this.formatNumber(activeJobs)}`;

      const elBarClosed = document.getElementById("barClosedJobsFill");
      const elValClosed = document.getElementById("valClosedJobs");
      if (elBarClosed) elBarClosed.style.width = `${pctClosed}%`;
      if (elValClosed) elValClosed.textContent = `${this.formatNumber(closedJobs)}`;

      const elBarDraft = document.getElementById("barDraftJobsFill");
      const elValDraft = document.getElementById("valDraftJobs");
      if (elBarDraft) elBarDraft.style.width = `${pctDraft}%`;
      if (elValDraft) elValDraft.textContent = `${this.formatNumber(draftJobs)}`;

      // 4. Render Recent Activities List
      const activitiesListEl = document.getElementById("adminRecentActivities");
      if (activitiesListEl) {
        const activities = data.recent_activities || [];
        if (activities.length === 0) {
          activitiesListEl.innerHTML = `
            <div class="dash-empty-state">
              <span class="dash-empty-icon">🔔</span>
              <p>Chưa có hoạt động gần đây nào</p>
            </div>
          `;
        } else {
          activitiesListEl.innerHTML = activities
            .slice(0, 6)
            .map((act) => `
              <div class="dash-list-item">
                <div class="dash-list-info">
                  <span class="dash-list-title">${escapeHtml(act.title)}</span>
                  <span class="dash-list-sub">${this.formatRelativeTime(act.created_at)}</span>
                </div>
                <span class="badge badge-reviewed">Hệ thống</span>
              </div>
            `)
            .join("");
        }
      }
    } catch (err) {
      console.error("Lỗi tải admin dashboard:", err);
      this.renderError("adminErrorSlot", err.message || "Không thể tải dữ liệu quản trị", "Dashboard.initAdminDashboard");
    }
  },

  // =========================================================================
  // 3. SINH VIÊN (STUDENT DASHBOARD - "VIỆC LÀM CỦA TÔI")
  // =========================================================================
  async initStudentDashboard() {
    const user = AuthGuard.requireRoles(["student"]);
    if (!user) return;
    this.setupLogout();

    let allApplications = [];

    try {
      const data = await api.get("/dashboard/student");

      // 1. Render Summary KPI numbers
      const summary = data.summary || {};
      const elApplied = document.getElementById("studentAppliedCount");
      const elSaved = document.getElementById("studentSavedCount");
      const elViewed = document.getElementById("studentViewedCount");

      if (elApplied) elApplied.textContent = String(summary.applied_count || 0).padStart(2, "0");
      if (elSaved) elSaved.textContent = String(summary.saved_count || 0).padStart(2, "0");
      if (elViewed) elViewed.textContent = String(summary.viewed_count || 0).padStart(2, "0");

      // 2. Render Status Doughnut Chart
      const chartCanvas = document.getElementById("studentStatusChart");
      const statusDist = data.status_distribution || {};
      const statusValues = [
        statusDist.pending || 0,
        statusDist.reviewed || 0,
        statusDist.interview || 0,
        statusDist.accepted || 0,
        statusDist.rejected || 0,
      ];
      const totalApps = statusValues.reduce((a, b) => a + b, 0);

      if (chartCanvas && typeof Chart !== "undefined") {
        this.destroyChart("studentStatusChart");
        const ctx = chartCanvas.getContext("2d");
        this.charts["studentStatusChart"] = new Chart(ctx, {
          type: "doughnut",
          data: {
            labels: ["Đang chờ", "Đã xem", "Phỏng vấn", "Được nhận", "Từ chối"],
            datasets: [
              {
                data: totalApps > 0 ? statusValues : [1],
                backgroundColor: totalApps > 0
                  ? ["#E5B96F", "#8176B5", "#6255A5", "#6EAA87", "#D97979"]
                  : ["#E8E5F0"],
                borderWidth: 0,
                hoverOffset: totalApps > 0 ? 4 : 0,
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: "68%",
            plugins: {
              legend: {
                position: "bottom",
                labels: {
                  font: { family: "Inter", size: 12 },
                  color: "#292642",
                  usePointStyle: true,
                  padding: 12,
                },
              },
              tooltip: {
                enabled: totalApps > 0,
                backgroundColor: "#292642",
                callbacks: {
                  label: (ctx) => ` ${ctx.label}: ${ctx.raw} đơn (${totalApps > 0 ? Math.round((ctx.raw / totalApps) * 100) : 0}%)`,
                },
              },
            },
          },
        });
      }

      // 3. Render Applications Table with Search & Filter
      allApplications = data.recent_applications || [];
      const tbody = document.getElementById("studentApplicationsTableBody");
      const footerCount = document.getElementById("studentTableFooterCount");
      const searchInput = document.getElementById("studentSearchInput");
      const statusFilter = document.getElementById("studentStatusFilter");

      const renderTable = () => {
        const query = (searchInput?.value || "").trim().toLowerCase();
        const selectedStatus = statusFilter?.value || "";

        const filtered = allApplications.filter((item) => {
          const matchQuery =
            !query ||
            (item.job_title && item.job_title.toLowerCase().includes(query)) ||
            (item.company_name && item.company_name.toLowerCase().includes(query));

          const matchStatus = !selectedStatus || item.status === selectedStatus;
          return matchQuery && matchStatus;
        });

        if (footerCount) {
          footerCount.textContent = `Hiển thị ${filtered.length} trên ${allApplications.length} công việc`;
        }

        if (!tbody) return;

        if (filtered.length === 0) {
          tbody.innerHTML = `
            <tr>
              <td colspan="4" style="text-align: center; padding: 48px 16px;">
                <div class="dash-empty-state" style="padding: 0;">
                  <span class="dash-empty-icon">🔍</span>
                  <p>Không tìm thấy đơn ứng tuyển nào phù hợp</p>
                </div>
              </td>
            </tr>
          `;
          return;
        }

        tbody.innerHTML = filtered
          .map((app) => {
            const badge = this.getStatusBadge(app.status);
            return `
            <tr>
              <td>
                <div class="table-job-info">
                  <strong>${escapeHtml(app.job_title)}</strong>
                  <span>${escapeHtml(app.company_name)}</span>
                </div>
              </td>
              <td>${this.formatDate(app.applied_at)}</td>
              <td>
                <span class="badge ${badge.class}">${badge.label}</span>
              </td>
              <td>
                <a href="company_detail.html?id=${app.job_id || 1}" class="table-action-link" title="Xem chi tiết việc làm">
                  Chi tiết <span aria-hidden="true">→</span>
                </a>
              </td>
            </tr>
          `;
          })
          .join("");
      };

      // Initial render
      renderTable();

      // Bind search & filter inputs
      if (searchInput) {
        searchInput.addEventListener("input", () => renderTable());
      }
      if (statusFilter) {
        statusFilter.addEventListener("change", () => renderTable());
      }
    } catch (err) {
      console.error("Lỗi tải student dashboard:", err);
      this.renderError("studentErrorSlot", err.message || "Không thể tải dữ liệu đơn ứng tuyển", "Dashboard.initStudentDashboard");
    }
  },
};

// Helper to escape HTML tags for security
function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
