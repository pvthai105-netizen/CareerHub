/**
 * CareerHub - Admin Management Logic (Task T02CF62)
 * Quản lý tài khoản (Users) & Kiểm duyệt tin tuyển dụng (Jobs)
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. Kiểm tra quyền Admin (Chặn nếu không phải Admin)
  const currentUser = AuthGuard.requireRoles(["admin"]);
  if (!currentUser) return;

  // Hiển thị email Admin trên thanh Sidebar & Topbar
  const adminEmailDisplay = document.getElementById("sidebarAdminEmail");
  const topbarEmailDisplay = document.getElementById("topbarAdminEmail");
  if (adminEmailDisplay) adminEmailDisplay.textContent = currentUser.email || "Admin";
  if (topbarEmailDisplay) topbarEmailDisplay.textContent = currentUser.email || "Admin";

  // Nút đăng xuất
  const btnLogout = document.getElementById("btnLogout");
  if (btnLogout) {
    btnLogout.addEventListener("click", () => {
      Auth.clear();
      window.location.href = "login.html";
    });
  }

  // ============================================================
  // TOAST & MODAL HELPERS
  // ============================================================
  const toastEl = document.getElementById("adminToast");
  function showToast(message, type = "success") {
    toastEl.className = `toast-msg ${type}`;
    toastEl.textContent = message;
    toastEl.style.display = "flex";
    setTimeout(() => {
      toastEl.style.display = "none";
    }, 3000);
  }

  // Confirm Modal state
  const confirmModal = document.getElementById("confirmModal");
  const confirmTitle = document.getElementById("confirmModalTitle");
  const confirmMessage = document.getElementById("confirmModalMessage");
  const btnConfirmYes = document.getElementById("btnConfirmYes");
  const btnConfirmNo = document.getElementById("btnConfirmNo");
  const btnCancelConfirm = document.getElementById("btnCancelConfirm");
  let onConfirmCallback = null;

  function openConfirmModal(title, message, callback, isDanger = false) {
    confirmTitle.textContent = title;
    confirmMessage.textContent = message;
    onConfirmCallback = callback;
    btnConfirmYes.className = isDanger ? "btn btn-danger" : "btn btn-primary";
    confirmModal.classList.add("open");
  }

  function closeConfirmModal() {
    confirmModal.classList.remove("open");
    onConfirmCallback = null;
  }

  btnConfirmYes.addEventListener("click", async () => {
    if (onConfirmCallback) {
      await onConfirmCallback();
    }
    closeConfirmModal();
  });
  btnConfirmNo.addEventListener("click", closeConfirmModal);
  btnCancelConfirm.addEventListener("click", closeConfirmModal);

  // Detail Modal
  const detailModal = document.getElementById("detailModal");
  const detailTitle = document.getElementById("detailModalTitle");
  const detailBody = document.getElementById("detailModalBody");
  const btnCloseDetail = document.getElementById("btnCloseDetail");
  const btnCloseDetailFooter = document.getElementById("btnCloseDetailFooter");

  function openDetailModal(title, htmlContent) {
    detailTitle.textContent = title;
    detailBody.innerHTML = htmlContent;
    detailModal.classList.add("open");
  }
  function closeDetailModal() {
    detailModal.classList.remove("open");
  }
  btnCloseDetail.addEventListener("click", closeDetailModal);
  btnCloseDetailFooter.addEventListener("click", closeDetailModal);

  // ============================================================
  // TAB SWITCHING LOGIC
  // ============================================================
  const tabBtns = document.querySelectorAll(".admin-tab-btn");
  const tabPanes = document.querySelectorAll(".admin-tab-pane");

  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      tabBtns.forEach((b) => b.classList.remove("active"));
      tabPanes.forEach((p) => p.classList.remove("active"));

      btn.classList.add("active");
      const targetTab = document.getElementById(btn.getAttribute("data-tab"));
      if (targetTab) targetTab.classList.add("active");

      // Load dữ liệu khi chuyển tab
      if (btn.id === "tabBtnUsers") loadUsers(1);
      if (btn.id === "tabBtnJobs") loadJobs(1);
    });
  });

  // ============================================================
  // TAB 1: QUẢN LÝ NGƯỜI DÙNG (USERS)
  // ============================================================
  let userCurrentPage = 1;
  const userTableBody = document.getElementById("userTableBody");
  const userPagination = document.getElementById("userPagination");

  async function loadUsers(page = 1) {
    userCurrentPage = page;
    userTableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 24px; color: var(--muted);">Đang tải dữ liệu...</td></tr>`;

    const search = document.getElementById("filterUserSearch").value.trim();
    const role = document.getElementById("filterUserRole").value;
    const isLocked = document.getElementById("filterUserLocked").value;

    let query = `/admin/users?page=${page}&limit=10`;
    if (search) query += `&search=${encodeURIComponent(search)}`;
    if (role) query += `&role=${encodeURIComponent(role)}`;
    if (isLocked !== "") query += `&is_locked=${isLocked}`;

    try {
      const data = await api.get(query);
      document.getElementById("badgeTotalUsers").textContent = data.total;

      if (!data.items || data.items.length === 0) {
        userTableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 24px; color: var(--muted);">Không tìm thấy người dùng nào phù hợp.</td></tr>`;
        userPagination.innerHTML = "";
        return;
      }

      userTableBody.innerHTML = data.items
        .map((u) => {
          const roleClass = u.role === "student" ? "badge-student" : u.role === "employer" ? "badge-employer" : "badge-admin";
          const roleName = u.role === "student" ? "Sinh viên" : u.role === "employer" ? "Doanh nghiệp" : "Admin";
          const statusBadge = u.is_locked
            ? `<span class="badge-status status-rejected">Đã bị khóa</span>`
            : `<span class="badge-status status-active">Đang hoạt động</span>`;
          const lockBtnText = u.is_locked ? "Mở khóa" : "Khóa tài khoản";
          const lockBtnClass = u.is_locked ? "btn-success" : "btn-danger";

          return `
            <tr>
              <td><strong>#${u.id}</strong></td>
              <td>${u.email}</td>
              <td>${u.display_name || '<em style="color: var(--muted)">Chưa cập nhật</em>'}</td>
              <td><span class="badge-role ${roleClass}">${roleName}</span></td>
              <td>${new Date(u.created_at).toLocaleDateString("vi-VN")}</td>
              <td>${statusBadge}</td>
              <td style="text-align: center;">
                <div class="action-btn-group" style="justify-content: center;">
                  <button type="button" class="btn btn-outline btn-sm" onclick="viewUserDetail(${u.id})">Chi tiết</button>
                  <button type="button" class="btn ${lockBtnClass} btn-sm" onclick="toggleLockUser(${u.id}, '${u.email}', ${u.is_locked})">
                    ${lockBtnText}
                  </button>
                </div>
              </td>
            </tr>
          `;
        })
        .join("");

      renderPagination(userPagination, data.total, data.page, data.limit, loadUsers);
    } catch (err) {
      userTableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 24px; color: var(--error-text);">Lỗi: ${err.message}</td></tr>`;
    }
  }

  // Khóa / Mở khóa người dùng
  window.toggleLockUser = (userId, email, currentLocked) => {
    const actionText = currentLocked ? "mở khóa" : "khóa";
    const title = currentLocked ? "Xác nhận mở khóa tài khoản" : "Xác nhận khóa tài khoản";
    const msg = currentLocked
      ? `Bạn có chắc chắn muốn mở khóa cho tài khoản "${email}"? Người dùng này sẽ có thể đăng nhập lại vào hệ thống.`
      : `Bạn có chắc chắn muốn khóa tài khoản "${email}"? Người dùng này sẽ bị đăng xuất và không thể đăng nhập vào hệ thống nữa.`;

    openConfirmModal(
      title,
      msg,
      async () => {
        try {
          await api.patch(`/admin/users/${userId}/status`, { is_locked: !currentLocked });
          showToast(`Đã ${actionText} tài khoản ${email} thành công!`);
          loadUsers(userCurrentPage);
        } catch (err) {
          showToast(`Lỗi: ${err.message}`, "error");
        }
      },
      !currentLocked // nếu là khóa thì dùng nút đỏ cảnh báo
    );
  };

  // Xem chi tiết tài khoản
  window.viewUserDetail = async (userId) => {
    try {
      const u = await api.get(`/admin/users/${userId}`);
      let profileHtml = "";

      if (u.student_profile) {
        const sp = u.student_profile;
        profileHtml = `
          <h4 style="color: var(--indigo); margin-top: 16px; margin-bottom: 12px;">🎓 Hồ sơ sinh viên</h4>
          <div class="detail-group"><div class="detail-label">Họ và tên:</div><div class="detail-value">${sp.full_name || "Chưa có"}</div></div>
          <div class="detail-group"><div class="detail-label">Số điện thoại:</div><div class="detail-value">${sp.phone || "Chưa có"}</div></div>
          <div class="detail-group"><div class="detail-label">Trường đại học:</div><div class="detail-value">${sp.university || "Chưa có"}</div></div>
          <div class="detail-group"><div class="detail-label">Chuyên ngành:</div><div class="detail-value">${sp.major || "Chưa có"}</div></div>
          <div class="detail-group"><div class="detail-label">Kỹ năng:</div><div class="detail-value">${sp.skills || "Chưa có"}</div></div>
        `;
      } else if (u.employer_profile) {
        const ep = u.employer_profile;
        profileHtml = `
          <h4 style="color: var(--indigo); margin-top: 16px; margin-bottom: 12px;">🏢 Hồ sơ doanh nghiệp</h4>
          <div class="detail-group"><div class="detail-label">Tên công ty:</div><div class="detail-value">${ep.company_name || "Chưa có"}</div></div>
          <div class="detail-group"><div class="detail-label">Website:</div><div class="detail-value">${ep.company_website || "Chưa có"}</div></div>
          <div class="detail-group"><div class="detail-label">Địa chỉ:</div><div class="detail-value">${ep.address || "Chưa có"}</div></div>
          <div class="detail-group"><div class="detail-label">Điện thoại liên hệ:</div><div class="detail-value">${ep.phone || "Chưa có"}</div></div>
        `;
      }

      const content = `
        <div class="detail-group"><div class="detail-label">Email tài khoản:</div><div class="detail-value"><strong>${u.email}</strong></div></div>
        <div class="detail-group"><div class="detail-label">Vai trò:</div><div class="detail-value">${u.role}</div></div>
        <div class="detail-group"><div class="detail-label">Trạng thái tài khoản:</div><div class="detail-value">${u.is_locked ? "Đã bị khóa" : "Đang hoạt động"}</div></div>
        <div class="detail-group"><div class="detail-label">Ngày đăng ký:</div><div class="detail-value">${new Date(u.created_at).toLocaleString("vi-VN")}</div></div>
        ${profileHtml}
      `;

      openDetailModal(`Thông tin tài khoản #${u.id}`, content);
    } catch (err) {
      showToast(`Không thể tải thông tin: ${err.message}`, "error");
    }
  };

  document.getElementById("btnFilterUsers").addEventListener("click", () => loadUsers(1));

  // ============================================================
  // TAB 2: KIỂM DUYỆT TIN TUYỂN DỤNG (JOBS)
  // ============================================================
  let jobCurrentPage = 1;
  const jobTableBody = document.getElementById("jobTableBody");
  const jobPagination = document.getElementById("jobPagination");

  async function loadJobs(page = 1) {
    jobCurrentPage = page;
    jobTableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 24px; color: var(--muted);">Đang tải danh sách tin...</td></tr>`;

    const keyword = document.getElementById("filterJobKeyword").value.trim();
    const status = document.getElementById("filterJobStatus").value;

    let query = `/admin/jobs?page=${page}&limit=10`;
    if (keyword) query += `&keyword=${encodeURIComponent(keyword)}`;
    if (status) query += `&status=${encodeURIComponent(status)}`;

    try {
      const data = await api.get(query);
      document.getElementById("badgeTotalJobs").textContent = data.total;

      if (!data.items || data.items.length === 0) {
        jobTableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 24px; color: var(--muted);">Không có tin tuyển dụng nào theo điều kiện lọc.</td></tr>`;
        jobPagination.innerHTML = "";
        return;
      }

      jobTableBody.innerHTML = data.items
        .map((j) => {
          let statusBadge = "";
          let actionButtons = "";

          if (j.status === "DRAFT") {
            statusBadge = `<span class="badge-status status-pending">Chờ duyệt</span>`;
            actionButtons = `
              <button type="button" class="btn btn-success btn-sm" onclick="approveJob(${j.job_id}, '${escapeQuote(j.title)}')">Duyệt tin</button>
              <button type="button" class="btn btn-danger btn-sm" onclick="hideJob(${j.job_id}, '${escapeQuote(j.title)}')">Ẩn tin</button>
            `;
          } else if (j.status === "ACTIVE") {
            statusBadge = `<span class="badge-status status-active">Đang mở</span>`;
            actionButtons = `
              <button type="button" class="btn btn-warning btn-sm" onclick="hideJob(${j.job_id}, '${escapeQuote(j.title)}')">Ẩn tin</button>
            `;
          } else if (j.status === "PAUSED") {
            statusBadge = `<span class="badge-status status-rejected">Bị ẩn</span>`;
            actionButtons = `
              <button type="button" class="btn btn-success btn-sm" onclick="approveJob(${j.job_id}, '${escapeQuote(j.title)}')">Mở lại</button>
            `;
          } else {
            statusBadge = `<span class="badge-status">${j.status}</span>`;
            actionButtons = `<span style="font-size: 12px; color: var(--muted)">Đã đóng</span>`;
          }

          return `
            <tr>
              <td><strong>#${j.job_id}</strong></td>
              <td>
                <div style="font-weight: 600; color: var(--ink);">${j.title}</div>
                <div style="font-size: 12px; color: var(--muted);">${j.industry}</div>
              </td>
              <td>${j.company_name || j.employer_email || '<em style="color: var(--muted)">Doanh nghiệp</em>'}</td>
              <td>${j.location}</td>
              <td>${new Date(j.deadline).toLocaleDateString("vi-VN")}</td>
              <td>${statusBadge}</td>
              <td style="text-align: center;">
                <div class="action-btn-group" style="justify-content: center;">
                  <button type="button" class="btn btn-outline btn-sm" onclick="viewJobDetail(${j.job_id})">Xem JD</button>
                  ${actionButtons}
                </div>
              </td>
            </tr>
          `;
        })
        .join("");

      renderPagination(jobPagination, data.total, data.page, data.limit, loadJobs);
    } catch (err) {
      jobTableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 24px; color: var(--error-text);">Lỗi: ${err.message}</td></tr>`;
    }
  }

  function escapeQuote(str) {
    return (str || "").replace(/'/g, "\\'").replace(/"/g, "&quot;");
  }

  // Duyệt tin
  window.approveJob = (jobId, title) => {
    openConfirmModal(
      "Phê duyệt tin tuyển dụng",
      `Bạn có chắc chắn muốn duyệt tin "${title}"? Tin này sẽ xuất hiện công khai trên trang chủ để sinh viên tìm kiếm và nộp đơn.`,
      async () => {
        try {
          await api.post(`/admin/jobs/${jobId}/approve`);
          showToast(`Đã duyệt tin #${jobId} thành công!`);
          loadJobs(jobCurrentPage);
        } catch (err) {
          showToast(`Lỗi: ${err.message}`, "error");
        }
      }
    );
  };

  // Ẩn tin
  window.hideJob = (jobId, title) => {
    openConfirmModal(
      "Ẩn tin tuyển dụng",
      `Bạn có chắc chắn muốn ẩn tin "${title}"? Tin này sẽ bị gỡ bỏ ngay lập tức khỏi các trang tìm kiếm công khai.`,
      async () => {
        try {
          await api.post(`/admin/jobs/${jobId}/hide`);
          showToast(`Đã ẩn tin #${jobId} thành công!`);
          loadJobs(jobCurrentPage);
        } catch (err) {
          showToast(`Lỗi: ${err.message}`, "error");
        }
      },
      true // danger button
    );
  };

  // Xem chi tiết tin
  window.viewJobDetail = async (jobId) => {
    try {
      const j = await api.get(`/admin/jobs/${jobId}`);
      const salary =
        j.salary_min && j.salary_max
          ? `${j.salary_min.toLocaleString()} - ${j.salary_max.toLocaleString()} VNĐ`
          : "Thỏa thuận";

      const content = `
        <div class="detail-group"><div class="detail-label">Tiêu đề:</div><div class="detail-value" style="font-size: 16px; font-weight: 700; color: var(--indigo);">${j.title}</div></div>
        <div class="detail-group"><div class="detail-label">Công ty đăng tuyển:</div><div class="detail-value">${j.company_name || "Chưa rõ"} (${j.employer_email})</div></div>
        <div class="detail-group"><div class="detail-label">Địa điểm / Hình thức:</div><div class="detail-value">${j.location} · ${j.job_type}</div></div>
        <div class="detail-group"><div class="detail-label">Mức lương:</div><div class="detail-value">${salary}</div></div>
        <div class="detail-group"><div class="detail-label">Hạn nộp hồ sơ:</div><div class="detail-value">${new Date(j.deadline).toLocaleDateString("vi-VN")}</div></div>
        <div class="detail-group"><div class="detail-label">Trạng thái:</div><div class="detail-value"><strong>${j.status}</strong></div></div>
        <div class="detail-group">
          <div class="detail-label">Mô tả công việc:</div>
          <div class="detail-value" style="background: var(--bg); padding: 12px; border-radius: var(--radius-sm); white-space: pre-wrap;">${j.description}</div>
        </div>
      `;

      openDetailModal(`Chi tiết tin tuyển dụng #${j.job_id}`, content);
    } catch (err) {
      showToast(`Không thể tải thông tin: ${err.message}`, "error");
    }
  };

  document.getElementById("btnFilterJobs").addEventListener("click", () => loadJobs(1));

  // ============================================================
  // PAGINATION COMPONENT
  // ============================================================
  function renderPagination(container, total, page, limit, onPageChange) {
    const totalPages = Math.ceil(total / limit) || 1;
    if (totalPages <= 1) {
      container.innerHTML = "";
      return;
    }

    let html = `
      <button class="page-btn" ${page <= 1 ? "disabled" : ""} onclick="(${onPageChange})(${page - 1})">← Trước</button>
      <span style="font-size: 13px; color: var(--muted); margin: 0 12px;">Trang <strong>${page}</strong> / ${totalPages} (Tổng ${total} mục)</span>
      <button class="page-btn" ${page >= totalPages ? "disabled" : ""} onclick="(${onPageChange})(${page + 1})">Sau →</button>
    `;
    container.innerHTML = html;
  }

  // Khởi chạy nạp dữ liệu Tab 1 đầu tiên
  loadUsers(1);
});