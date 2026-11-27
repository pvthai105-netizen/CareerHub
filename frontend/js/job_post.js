// Debounce: Giảm số lần gọi xử lý khi người dùng nhập tìm kiếm.
function debounce(fn, delay) {
  let timeout;

  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => fn(...args), delay);
  };
}

/**
 * Các phần tử HTML được sử dụng.
 */
const selectors = {
  tabButtons: document.querySelectorAll('.status-tabs .tab-btn'),
  searchInput: document.querySelector('.search-box .search-input'),
  filterSelect: document.querySelector('.filter-box .filter-select'),
  tableBody: document.querySelector('.job-table tbody'),

  // Lấy nút X có sẵn trong HTML làm mẫu
  deleteButtonTemplate: document.querySelector('.job-table tbody .action-delete'),

  paginationInfo: document.querySelector('.pagination-info'),
  paginationPages: document.querySelector('.pagination-pages'),
  createBtn: document.querySelector('.btn-create-job'),
};

/**
 * Trạng thái hiện tại của trang.
 */
let currentState = {
  page: 1,
  pageSize: 6,
  status: '',
  search: '',
  tab: 'all',
};

/**
 * Lưu toàn bộ danh sách tin lấy từ backend.
 */
let allJobs = [];

/**
 * Kiểm tra quyền truy cập.
 */
const user = AuthGuard.requireRoles(['employer']);

if (!user) {
  throw new Error('Không có quyền truy cập');
}

/**
 * Lấy ID của tin tuyển dụng.
 * Backend sử dụng job_id làm khóa chính.
 */
function getJobId(job) {
  return job.job_id ?? job.id;
}

/**
 * Chuẩn hóa trạng thái để so sánh.
 */
function normalizeStatus(status) {
  return String(status || '')
    .toLowerCase()
    .replace('jobstatus.', '');
}

/**
 * Chuyển trạng thái sang đúng kiểu chữ mà backend đang sử dụng.
 * Ví dụ: ACTIVE -> CLOSED hoặc active -> closed.
 */
function getApiStatusValue(currentStatus, newStatus) {
  const current = String(currentStatus || '');

  if (current && current === current.toUpperCase()) {
    return newStatus.toUpperCase();
  }

  return newStatus.toLowerCase();
}

/**
 * Lấy toàn bộ danh sách tin từ backend.
 * Không truyền job_status để tránh lỗi 422 do Enum.
 *
 * Backend giới hạn tối đa 100 tin mỗi lần gọi,
 * vì vậy cần gọi nhiều lần nếu có trên 100 tin.
 */
async function fetchAllJobs() {
  const limit = 100;
  let skip = 0;
  let total = 0;
  const jobs = [];

  do {
    const path = `/jobs/my-jobs?skip=${skip}&limit=${limit}`;

    const response = await api.get(path);

    // Hỗ trợ cả trường hợp API trả trực tiếp dữ liệu
    // hoặc dữ liệu nằm trong thuộc tính data.
    const result = response.data ?? response;

    const items = result.items || [];

    jobs.push(...items);

    total = result.total ?? jobs.length;

    skip += items.length;

    if (items.length === 0) {
      break;
    }

  } while (jobs.length < total);

  return jobs;
}

/**
 * Tải danh sách tin tuyển dụng.
 */
async function loadJobs() {
  try {
    allJobs = await fetchAllJobs();

    // Lọc theo trạng thái.
    let filteredJobs = [...allJobs];

    if (currentState.status) {
      filteredJobs = filteredJobs.filter(job =>
        normalizeStatus(job.status) === currentState.status
      );
    }

    // Lọc theo từ khóa tìm kiếm.
    if (currentState.search) {
      const keyword = currentState.search.toLowerCase();

      filteredJobs = filteredJobs.filter(job =>
        String(job.title || '').toLowerCase().includes(keyword)
      );
    }

    // Nếu dữ liệu thay đổi khiến trang hiện tại không còn tồn tại.
    const totalPages = Math.ceil(
      filteredJobs.length / currentState.pageSize
    );

    if (currentState.page > totalPages && totalPages > 0) {
      currentState.page = totalPages;
    }

    if (totalPages === 0) {
      currentState.page = 1;
    }

    renderJobs(filteredJobs);

  } catch (err) {
    console.error('Lỗi tải danh sách tin:', err);

    alert(err.message || 'Lỗi khi tải danh sách tin tuyển dụng');
  }
}

/**
 * Hiển thị danh sách tin tuyển dụng.
 */
function renderJobs(filteredJobs) {
  if (!selectors.tableBody) return;

  selectors.tableBody.innerHTML = '';

  const total = filteredJobs.length;

  // Tính vị trí bắt đầu và kết thúc của trang.
  const start = (currentState.page - 1) * currentState.pageSize;
  const end = start + currentState.pageSize;

  const pageJobs = filteredJobs.slice(start, end);

  if (pageJobs.length === 0) {
    selectors.tableBody.innerHTML = `
      <tr>
        <td colspan="6" class="no-data">
          Chưa có tin nào phù hợp.
        </td>
      </tr>
    `;
  } else {
    pageJobs.forEach(renderJobRow);
  }

  // Cập nhật thông tin hiển thị.
  if (selectors.paginationInfo) {
    selectors.paginationInfo.textContent =
      `Hiển thị ${pageJobs.length} trên ${total} tin tuyển dụng`;
  }

  // Cập nhật phân trang.
  const totalPages = Math.ceil(total / currentState.pageSize) || 1;

  renderPagination(totalPages);

  // Cập nhật số lượng tin trên các tab.
  updateTabCounts();
}

/**
 * Render một hàng tin tuyển dụng.
 */
function renderJobRow(job) {
  const tr = document.createElement('tr');

  // Cột vị trí và ngành nghề.
  const tdName = document.createElement('td');

  const nameDiv = document.createElement('div');
  nameDiv.className = 'job-name';
  nameDiv.textContent = job.title || '';

  const catDiv = document.createElement('div');
  catDiv.className = 'job-category';
  catDiv.textContent = job.industry || job.category || '';

  tdName.append(nameDiv, catDiv);

  // Cột ngày đăng.
  const tdDate = document.createElement('td');
  tdDate.className = 'text-date';
  tdDate.textContent = formatDate(job.created_at);

  // Cột hạn tuyển dụng.
  const tdDeadline = document.createElement('td');
  tdDeadline.className = 'text-date';
  tdDeadline.textContent = formatDate(job.deadline);

  // Cột số ứng viên.
  const tdCandidates = document.createElement('td');
  tdCandidates.className = 'text-candidates';
  tdCandidates.textContent = job.candidate_count ?? 0;

  // Cột trạng thái.
  const tdStatus = document.createElement('td');

  const badge = document.createElement('span');
  badge.className = `badge ${statusBadgeClass(job.status)}`;
  badge.textContent = statusLabel(job.status);

  tdStatus.appendChild(badge);

  // Cột thao tác.
  const tdActions = document.createElement('td');
  tdActions.className = 'actions-cell';

  tdActions.appendChild(
    actionLink('Sửa', () => editJob(getJobId(job)))
  );

  if (normalizeStatus(job.status) === 'closed') {
  tdActions.appendChild(
    actionLink('Mở lại', () => reopenJob(job))
    );
  } else {
    tdActions.appendChild(
      actionLink('Đóng', () => closeJob(job))
    );
  }

  // Lấy nút X có sẵn trong HTML
  const deleteBtn = selectors.deleteButtonTemplate.cloneNode(true);

  // Gán sự kiện xóa cho nút X
  deleteBtn.addEventListener('click', (event) => {
    event.preventDefault();
    deleteJob(job);
  });

  // Thêm nút X vào cột thao tác
  tdActions.appendChild(deleteBtn);

  tr.append(
    tdName,
    tdDate,
    tdDeadline,
    tdCandidates,
    tdStatus,
    tdActions
  );

  selectors.tableBody.appendChild(tr);
}

/**
 * Định dạng ngày tháng.
 */
function formatDate(dateStr) {
  if (!dateStr) return '';

  const date = new Date(dateStr);

  if (Number.isNaN(date.getTime())) return '';

  return date.toLocaleDateString('vi-VN');
}

/**
 * Chuyển trạng thái thành tên hiển thị.
 */
function statusLabel(status) {
  switch (normalizeStatus(status)) {
    case 'active':
      return 'Hoạt động';

    case 'draft':
      return 'Bản nháp';

    case 'closed':
      return 'Đã đóng';

    default:
      return status || '';
  }
}

/**
 * Lấy class CSS tương ứng với trạng thái.
 */
function statusBadgeClass(status) {
  switch (normalizeStatus(status)) {
    case 'active':
      return 'badge-active';

    case 'draft':
      return 'badge-draft';

    case 'closed':
      return 'badge-closed';

    default:
      return '';
  }
}

/**
 * Tạo nút thao tác.
 */
function actionLink(text, handler) {
  const a = document.createElement('a');

  a.href = '#';
  a.className = 'action-btn';
  a.textContent = text;

  a.addEventListener('click', (e) => {
    e.preventDefault();
    handler();
  });

  return a;
}

/**
 * Điều hướng đến trang sửa tin.
 */
function editJob(jobId) {
  if (!jobId) {
    alert('Không tìm thấy ID tin tuyển dụng');
    return;
  }

  window.location.href = `create_job.html?edit_id=${jobId}`;
}

/**
 * Đóng tin tuyển dụng.
 */
async function closeJob(job) {
  if (normalizeStatus(job.status) === 'closed') {
    alert('Tin này đã được đóng');
    return;
  }

  const ok = confirm('Bạn có chắc muốn đóng tin tuyển dụng này?');

  if (!ok) return;

  try {
    const jobId = getJobId(job);

    const newStatus = getApiStatusValue(
      job.status,
      'closed'
    );

    await api.patch(
      `/jobs/${jobId}/status`,
      { status: newStatus }
    );

    alert('Đã đóng tin thành công');

    await loadJobs();

  } catch (err) {
    console.error('Lỗi đóng tin:', err);

    alert(err.message || 'Không thể đóng tin');
  }
}


/**
 * Mở lại tin tuyển dụng đã đóng.
 */
async function reopenJob(job) {
  const ok = confirm('Bạn có chắc muốn mở lại tin tuyển dụng này?');

  if (!ok) return;

  try {
    const jobId = getJobId(job);

    const newStatus = getApiStatusValue(
      job.status,
      'active'
    );

    await api.patch(
      `/jobs/${jobId}/status`,
      { status: newStatus }
    );

    alert('Đã mở lại tin tuyển dụng thành công');

    await loadJobs();

  } catch (err) {
    console.error('Lỗi mở lại tin:', err);
    alert(err.message || 'Không thể mở lại tin');
  }
}


/**
 * Xóa tin tuyển dụng.
 */
async function deleteJob(job) {
  const ok = confirm(
    'Bạn có chắc muốn xóa tin này? Hành động không thể hoàn tác.'
  );

  if (!ok) return;

  try {
    const jobId = getJobId(job);

    await api.delete(`/jobs/my-jobs/${jobId}`);

    alert('Đã xóa tin thành công');

    await loadJobs();

  } catch (err) {
    console.error('Lỗi xóa tin:', err);

    alert(err.message || 'Không thể xóa tin');
  }
}

/**
 * Render các nút phân trang.
 */
function renderPagination(totalPages) {
  if (!selectors.paginationPages) return;

  const container = selectors.paginationPages;

  // Xóa các nút số trang cũ.
  container.querySelectorAll('.page-number').forEach(btn => {
    btn.remove();
  });

  // Tìm nút chuyển trang.
  const prevBtn = container.querySelector('.page-arrow.prev');
  const nextBtn = container.querySelector('.page-arrow.next');

  // Tạo các nút số trang.
  for (let i = 1; i <= totalPages; i++) {
    const btn = document.createElement('button');

    btn.className = 'page-number';

    if (i === currentState.page) {
      btn.classList.add('active');
    }

    btn.textContent = i;

    btn.addEventListener('click', () => {
      if (currentState.page !== i) {
        currentState.page = i;
        renderCurrentJobs();
      }
    });

    if (nextBtn) {
      container.insertBefore(btn, nextBtn);
    } else {
      container.appendChild(btn);
    }
  }

  // Trạng thái nút trang trước.
  if (prevBtn) {
    prevBtn.disabled = currentState.page <= 1;

    prevBtn.onclick = () => {
      if (currentState.page > 1) {
        currentState.page--;
        renderCurrentJobs();
      }
    };
  }

  // Trạng thái nút trang sau.
  if (nextBtn) {
    nextBtn.disabled = currentState.page >= totalPages;

    nextBtn.onclick = () => {
      if (currentState.page < totalPages) {
        currentState.page++;
        renderCurrentJobs();
      }
    };
  }
}

/**
 * Lọc lại dữ liệu đã tải để chuyển trang.
 * Không cần gọi API lại khi chỉ chuyển trang.
 */
function renderCurrentJobs() {
  let filteredJobs = [...allJobs];

  if (currentState.status) {
    filteredJobs = filteredJobs.filter(job =>
      normalizeStatus(job.status) === currentState.status
    );
  }

  if (currentState.search) {
    const keyword = currentState.search.toLowerCase();

    filteredJobs = filteredJobs.filter(job =>
      String(job.title || '').toLowerCase().includes(keyword)
    );
  }

  renderJobs(filteredJobs);
}

/**
 * Cập nhật số lượng tin trên các tab.
 */
function updateTabCounts() {
  const counts = {
    all: allJobs.length,
    active: 0,
    draft: 0,
    closed: 0,
  };

  allJobs.forEach(job => {
    const status = normalizeStatus(job.status);

    if (counts[status] !== undefined) {
      counts[status]++;
    }
  });

  selectors.tabButtons.forEach(btn => {
    const currentText = btn.dataset.originalLabel ||
      btn.textContent.trim();

    // Lưu tên tab ban đầu để tránh nối số nhiều lần.
    if (!btn.dataset.originalLabel) {
      btn.dataset.originalLabel = currentText.replace(/\s+\d+\s*$/, '');
    }

    const label = btn.dataset.originalLabel;

    if (label.startsWith('Tất cả')) {
      btn.textContent = `${label} ${counts.all}`;
    } else if (label.startsWith('Đang hoạt động')) {
      btn.textContent = `${label} ${counts.active}`;
    } else if (label.startsWith('Bản nháp')) {
      btn.textContent = `${label} ${counts.draft}`;
    } else if (label.startsWith('Đã đóng')) {
      btn.textContent = `${label} ${counts.closed}`;
    }
  });
}

/**
 * Xử lý sự kiện các tab trạng thái.
 */
selectors.tabButtons.forEach(btn => {
  btn.addEventListener('click', function () {
    selectors.tabButtons.forEach(b => {
      b.classList.remove('active');
    });

    this.classList.add('active');

    const label = this.dataset.originalLabel ||
      this.textContent.trim();

    if (label.startsWith('Tất cả')) {
      currentState.status = '';
      currentState.tab = 'all';
    } else if (label.startsWith('Đang hoạt động')) {
      currentState.status = 'active';
      currentState.tab = 'active';
    } else if (label.startsWith('Bản nháp')) {
      currentState.status = 'draft';
      currentState.tab = 'draft';
    } else if (label.startsWith('Đã đóng')) {
      currentState.status = 'closed';
      currentState.tab = 'closed';
    }

    // Đồng bộ dropdown.
    if (selectors.filterSelect) {
      selectors.filterSelect.value = currentState.status;
    }

    currentState.page = 1;

    renderCurrentJobs();
  });
});

/**
 * Xử lý tìm kiếm.
 */
if (selectors.searchInput) {
  selectors.searchInput.addEventListener(
    'input',
    debounce((e) => {
      currentState.search = e.target.value.trim();

      currentState.page = 1;

      renderCurrentJobs();
    }, 400)
  );
}

/**
 * Xử lý dropdown lọc trạng thái.
 */
if (selectors.filterSelect) {
  selectors.filterSelect.addEventListener('change', (e) => {
    currentState.status = normalizeStatus(e.target.value);

    currentState.page = 1;

    // Đồng bộ trạng thái tab.
    selectors.tabButtons.forEach(btn => {
      const label = btn.dataset.originalLabel ||
        btn.textContent.trim();

      const isActive =
        (label.startsWith('Tất cả') && !currentState.status) ||
        (label.startsWith('Đang hoạt động') &&
          currentState.status === 'active') ||
        (label.startsWith('Bản nháp') &&
          currentState.status === 'draft') ||
        (label.startsWith('Đã đóng') &&
          currentState.status === 'closed');

      btn.classList.toggle('active', isActive);
    });

    renderCurrentJobs();
  });
}

/**
 * Nút đăng tin mới.
 */
if (selectors.createBtn) {
  selectors.createBtn.addEventListener('click', () => {
    window.location.href = 'create_job.html';
  });
}

// XỬ LÝ ĐĂNG XUẤT
const logoutBtn = document.querySelector(".logout-link");
const confirmLogoutBtn = document.querySelector("#confirmLogoutBtn");

const logoutModalElement = document.querySelector("#logoutModal");

if (logoutBtn && logoutModalElement && confirmLogoutBtn) {
  const logoutModal = new bootstrap.Modal(logoutModalElement);

  // Bấm đăng xuất ở sidebar -> mở popup
  logoutBtn.addEventListener("click", function (event) {
    event.preventDefault();
    logoutModal.show();
  });

  // Xác nhận đăng xuất
  confirmLogoutBtn.addEventListener("click", function () {
    Auth.clear();
    window.location.href = "./login.html";
  });
}

/**
 * Khởi chạy trang.
 */
loadJobs();
