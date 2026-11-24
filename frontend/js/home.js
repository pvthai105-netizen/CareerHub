
// 1. CẤU HÌNH VÀ DỮ LIỆU
const API_URL = "http://127.0.0.1:8000/jobs/";  // Địa chỉ API của backend FastAPI, Frontend sẽ gọi địa chỉ này để lấy danh sách việc làm
const PER_PAGE = 6;  // Số lượng việc làm hiển thị trên mỗi trang

// Đối tượng lưu tên hiển thị tương ứng với từng mức lương.
// Key là giá trị được sử dụng trong code.
// Value là nội dung hiển thị cho người dùng.
const SALARY_LABELS = {
  "lt4": "Dưới 4 triệu",
  "4-5": "4 – 5 triệu",
  "ge5": "Từ 5 triệu trở lên"
};

// Chuyển mã loại công việc từ backend thành tiếng Việt.
// Ví dụ: INTERNSHIP sẽ hiển thị là Thực tập.
const TYPE_NAMES = {
  INTERNSHIP: "Thực tập",
  PART_TIME: "Bán thời gian",
  FULL_TIME: "Toàn thời gian",
  REMOTE: "Làm từ xa"
};

// Mảng lưu toàn bộ việc làm được lấy từ API.
// Ban đầu chưa tải dữ liệu nên mảng rỗng.
let JOBS = [];

// Lưu tổng số việc làm backend trả về.
let totalJobs = 0;

// Lưu tổng số trang dữ liệu backend trả về.
let totalPages = 0;

// Hàm thêm số 0 phía trước nếu số nhỏ hơn 10.
// Ví dụ: pad(5) trả về "05".
// Hiện tại hàm này chưa được sử dụng ở phần code bên dưới.
function pad(n) {
  return n < 10 ? "0" + n : "" + n;
}

/* =====================================================
   2. TRẠNG THÁI
   ===================================================== */

// Lưu trạng thái các bộ lọc mà người dùng đang chọn.
let filters = {
  keyword: "",  // Từ khóa tìm kiếm, ví dụ: Python, Java, React.
  location: "",  // Địa điểm người dùng chọn.
  field: "",  // Lĩnh vực người dùng chọn.
  salary: "",  // Mức lương người dùng chọn.
  types: []  // Mảng chứa các loại công việc được chọn, Ví dụ: ["Thực tập", "Bán thời gian"]
};

// Lưu kiểu sắp xếp hiện tại.
// "new" nghĩa là sắp xếp theo ID mới nhất.
let sortBy = "new";

// Lưu số trang frontend hiện tại.
// Ban đầu người dùng ở trang 1.
let currentPage = 1;

// Lưu trạng thái công việc đã được người dùng yêu thích.
// Ví dụ: savedJobs[1] = true nghĩa là đã lưu công việc ID 1.
let savedJobs = {};


// Hàm hỏi backend xem người dùng đã lưu những việc nào, rồi ghi vào savedJobs
async function loadSavedState() {
  savedJobs = {};
  const ids = await SavedJobs.getIds();      // ví dụ [3, 7]; nếu chưa đăng nhập thì là []
  for (let i = 0; i < ids.length; i++) {
    savedJobs[ids[i]] = true;
  }
}

// Hàm đưa tất cả bộ lọc về trạng thái ban đầu.
function resetFilters() {

  // Gán lại một đối tượng filters mới với các giá trị rỗng.
  filters = {
    keyword: "",
    location: "",
    field: "",
    salary: "",
    types: []
  };
}

/* =====================================================
   3. CHUYỂN ĐỔI DỮ LIỆU API
   ===================================================== */

// Hàm nhận một việc làm lấy từ API.
// Sau đó chuyển dữ liệu thành định dạng mà frontend đang sử dụng.
function convertJob(item) {

  // Trả về một đối tượng việc làm mới.
  return {

    // Lấy ID từ backend và chuyển thành kiểu Number.
    id: Number(item.job_id),

    // Lấy tiêu đề công việc.
    // Nếu không có dữ liệu thì sử dụng chuỗi rỗng.
    title: item.title || "",

    // Lấy ID nhà tuyển dụng.
    // Nếu có ID thì tạo tên dạng Employer #1.
    // Nếu không có thì để trống.
    company: item.employer_id
      ? `Employer #${item.employer_id}`
      : "",

    // Lấy lĩnh vực tuyển dụng.
    field: item.industry || "",

    // Lấy địa điểm làm việc.
    location: item.location || "",

    // Chuyển mã loại công việc thành tiếng Việt.
    // Nếu không tìm thấy mã tương ứng thì giữ giá trị gốc.
    type: TYPE_NAMES[item.job_type] || item.job_type || "",

    // Lấy lương tối thiểu.
    // Backend lưu bằng đồng nên chia cho 1.000.000 để đổi sang triệu.
    min: item.salary_min != null ? Number(item.salary_min) / 1000000 : 0,  // Nếu không có dữ liệu thì mặc định bằng 0
    max: item.salary_max != null ? Number(item.salary_max) / 1000000 : 0,  // Lấy lương tối đa và đổi sang đơn vị triệu đồng.
    desc: item.description || "",                                          // Lấy mô tả công việc.
    deadline: item.deadline || ""                                          // Lấy hạn ứng tuyển.
  };
}

/* =====================================================
   4. TẢI TOÀN BỘ DỮ LIỆU TỪ API
   ===================================================== */

// async cho biết đây là hàm bất đồng bộ.
// Hàm này có thể sử dụng await để chờ API trả dữ liệu.
async function loadJobs() {
  try {  // try dùng để chạy đoạn code có thể phát sinh lỗi.
    // Tạo tham số gửi lên API.
    // page = 1: lấy trang đầu tiên.
    // limit = 6: mỗi trang lấy tối đa 6 việc làm.
    const firstQuery = new URLSearchParams({
      page: 1,
      limit: PER_PAGE
    });

    // Gửi yêu cầu GET đến API.
    // await giúp chờ backend phản hồi rồi mới chạy tiếp.
    const firstResponse = await fetch(`${API_URL}?${firstQuery}`);

    // Kiểm tra phản hồi HTTP.
    // Nếu status không nằm trong nhóm thành công thì phát sinh lỗi.
    if (!firstResponse.ok) {
      throw new Error(`HTTP ${firstResponse.status}`);
    }

    // Chuyển dữ liệu JSON backend trả về thành đối tượng JavaScript.
    const firstData = await firstResponse.json();

    // Kiểm tra API có trả về mảng items hay không.
    // Nếu không phải mảng thì dữ liệu không đúng cấu trúc mong đợi.
    if (!Array.isArray(firstData.items)) {
      throw new Error("Dữ liệu API không đúng cấu trúc.");
    }

    // Lưu tổng số việc làm backend trả về.
    // Number() chuyển dữ liệu sang kiểu số.
    // || 0 nghĩa là nếu không có giá trị hợp lệ thì dùng 0.
    totalJobs = Number(firstData.total) || 0;

    // Lưu tổng số trang backend trả về.
    totalPages = Number(firstData.total_pages) || 0;

    // Sao chép các việc làm của trang đầu tiên vào mảng allItems.
    // Dấu ... là toán tử spread, dùng để sao chép các phần tử mảng.
    let allItems = [...firstData.items];

    // Bắt đầu từ trang 2.
    // Lặp cho đến khi tải hết số trang backend cung cấp.
    for (let page = 2; page <= totalPages; page++) {

      // Tạo tham số để lấy trang hiện tại.
      const query = new URLSearchParams({
        page: page,
        limit: PER_PAGE
      });

      // Gọi API để lấy dữ liệu của trang hiện tại.
      const response = await fetch(`${API_URL}?${query}`);

      // Nếu API trả về lỗi thì dừng và chuyển sang catch.
      if (!response.ok) {
        throw new Error(`Không tải được trang ${page}: HTTP ${response.status}`);
      }

      // Chuyển phản hồi JSON thành đối tượng JavaScript.
      const data = await response.json();

      // Kiểm tra dữ liệu của trang hiện tại có đúng định dạng không.
      if (!Array.isArray(data.items)) {
        throw new Error(`Dữ liệu trang ${page} không hợp lệ.`);
      }

      // Nối các việc làm vừa tải vào mảng allItems.
      // concat() tạo mảng mới chứa cả dữ liệu cũ và dữ liệu mới.
      allItems = allItems.concat(data.items);
    }

    // Duyệt qua toàn bộ dữ liệu API.
    // Mỗi item được đưa vào hàm convertJob().
    // Kết quả được lưu vào mảng JOBS.
    JOBS = allItems.map(convertJob);
    await loadSavedState();  

    // In tổng số việc làm backend báo cáo ra Console.
    console.log("Tổng việc làm từ API:", totalJobs);

    // In số việc làm thực tế đã tải được.
    console.log("Số việc làm đã tải:", JOBS.length);

    // Sau khi tải dữ liệu thành công, bắt đầu khởi tạo giao diện.
    startApp();

  } catch (error) {
    console.error("Lỗi tải việc làm:", error);  // Nếu có lỗi thì in lỗi ra Console để kiểm tra.
    JOBS = [];      // Đưa dữ liệu về mảng rỗng vì tải thất bại.
    totalJobs = 0;  // Đưa tổng số việc làm về 0.
    totalPages = 0; // Đưa tổng số trang về 0.

    alert(`Không tải được dữ liệu việc làm: ${error.message}`);  // Hiển thị thông báo lỗi cho người dùng.
    startApp();   // Vẫn khởi tạo giao diện để ứng dụng không bị dừng hoàn toàn.
  }
}

/* =====================================================
   5. LỌC VÀ SẮP XẾP
   ===================================================== */

// Hàm lấy danh sách việc làm sau khi áp dụng các bộ lọc.
function getFilteredJobs() {
  const result = [];  // Tạo mảng rỗng để chứa kết quả phù hợp.

  // Lấy từ khóa tìm kiếm.
  // toLowerCase() chuyển chữ thành chữ thường.
  // trim() xóa khoảng trắng ở đầu và cuối.
  const keyword = filters.keyword.toLowerCase().trim();

  // Duyệt qua từng việc làm trong mảng JOBS.
  for (let i = 0; i < JOBS.length; i++) {
    const job = JOBS[i];   // Lấy việc làm tại vị trí i.

    // Ghép các thông tin thành một chuỗi để tìm kiếm.
    // Bao gồm tên việc làm, công ty, lĩnh vực và mô tả.
    const text = (
      job.title + " " +
      job.company + " " +
      job.field + " " +
      job.desc
    ).toLowerCase();

    // Nếu có từ khóa mà nội dung không chứa từ khóa đó
    // thì bỏ qua việc làm này.
    if (keyword !== "" && !text.includes(keyword)) continue;

    // Nếu người dùng chọn địa điểm
    // và địa điểm việc làm không trùng thì bỏ qua.
    if (
      filters.location !== "" &&
      job.location !== filters.location
    ) continue;

    // Nếu người dùng chọn lĩnh vực
    // và lĩnh vực việc làm không trùng thì bỏ qua.
    if (
      filters.field !== "" &&
      job.field !== filters.field
    ) continue;

    // Nếu người dùng chọn loại công việc
    // nhưng việc làm hiện tại không thuộc loại đã chọn thì bỏ qua.
    if (
      filters.types.length > 0 &&
      !filters.types.includes(job.type)
    ) continue;

    // Nếu chọn mức lương dưới 4 triệu
    // nhưng lương tối thiểu từ 4 triệu trở lên thì bỏ qua.
    if (filters.salary === "lt4" && job.min >= 4) continue;

    // Nếu chọn mức lương từ 4 đến dưới 5 triệu
    // thì loại các việc có lương tối thiểu ngoài khoảng đó.
    if (
      filters.salary === "4-5" &&
      (job.min < 4 || job.min >= 5)
    ) continue;

    // Nếu chọn mức lương từ 5 triệu trở lên
    // nhưng lương tối thiểu dưới 5 triệu thì bỏ qua.
    if (filters.salary === "ge5" && job.min < 5) continue;

    // Nếu không bị loại bởi bất kỳ điều kiện nào
    // thì thêm việc làm vào danh sách kết quả.
    result.push(job);
  }

  // Kiểm tra kiểu sắp xếp mà người dùng đã chọn.
  if (sortBy === "salary") {
    // Sắp xếp theo lương tối đa giảm dần.
    // Việc làm có lương cao hơn sẽ đứng trước.
    result.sort((a, b) => b.max - a.max);

  } else {
    // Nếu không chọn sắp xếp theo lương
    // thì sắp xếp theo ID giảm dần.
    // ID lớn hơn thường là việc làm được tạo sau.
    result.sort((a, b) => b.id - a.id);
  }

  return result;  // Trả về danh sách việc làm sau khi lọc và sắp xếp.
}

/* =====================================================
   6. HIỂN THỊ VIỆC LÀM
   ===================================================== */

// Hàm chuyển thông tin lương thành chuỗi để hiển thị.
function salaryText(job) {
  // Ghép lương tối thiểu và tối đa thành một chuỗi.
  // Ví dụ: 4 – 7 triệu.
  // replace() thay dấu chấm thập phân thành dấu phẩy.
  return (
    job.min + " – " + job.max + " triệu"
  ).replace(".", ",").replace(".", ",");
}

// Hàm tạo HTML cho một thẻ việc làm.
function jobCardHTML(job) {
  // Dấu backtick cho phép tạo chuỗi HTML nhiều dòng.
  // ${} dùng để chèn giá trị JavaScript vào HTML.
  return `
    <!-- Khi bấm vào thẻ sẽ chuyển sang trang chi tiết -->
    <a href="#/job/${job.id}" class="job-card">

      <!-- Hiển thị tên công ty -->
      <small>${escapeHTML(job.company)}</small>

      <!-- Hiển thị tiêu đề công việc -->
      <h3>${escapeHTML(job.title)}</h3>

      <!-- Hiển thị địa điểm và loại công việc -->
      <span>${escapeHTML(job.location)} · ${escapeHTML(job.type)}</span>

      <!-- Hiển thị mức lương -->
      <b>${salaryText(job)}</b>

    </a>
  `;
}

/* =====================================================
   7. TRANG CHỦ
   ===================================================== */

// Hàm hiển thị dữ liệu tại trang chủ.
function renderHome() {

  // Sao chép mảng JOBS để không làm thay đổi mảng gốc.
  // Sắp xếp ID giảm dần để việc làm mới nhất đứng trước.
  // slice(0, 3) chỉ lấy 3 việc làm đầu tiên.
  const latestJobs = [...JOBS]
    .sort((a, b) => b.id - a.id)
    .slice(0, 3);

  // Tạo chuỗi HTML rỗng.
  let html = "";

  // Duyệt qua 3 việc làm mới nhất.
  for (let i = 0; i < latestJobs.length; i++) {

    // Tạo HTML cho từng việc làm rồi nối vào chuỗi html.
    html += jobCardHTML(latestJobs[i]);
  }

  // Tìm phần tử có ID home-jobs trong HTML.
  // Đưa danh sách việc làm vừa tạo vào phần tử đó.
  document.getElementById("home-jobs").innerHTML = html;

  // Danh sách các lĩnh vực sẽ hiển thị trên trang chủ.
  const names = [
    "Công nghệ thông tin",
    "Thiết kế",
    "Marketing",
    "Kinh doanh / Bán hàng"
  ];

  // Tạo chuỗi HTML cho các ô lĩnh vực.
  let tiles = "";

  // Duyệt qua từng lĩnh vực.
  for (let i = 0; i < names.length; i++) {

    // Ban đầu số lượng việc làm của lĩnh vực bằng 0.
    let count = 0;

    // Duyệt qua toàn bộ việc làm.
    for (let j = 0; j < JOBS.length; j++) {

      // Nếu lĩnh vực của việc làm trùng với lĩnh vực đang xét.
      if (JOBS[j].field === names[i]) {

        // Tăng số lượng lên 1.
        count++;
      }
    }

    // Tạo một thẻ HTML cho lĩnh vực.
    // Hiển thị tên lĩnh vực và số lượng việc làm.
    tiles += `
      <a href="#/jobs" class="field-tile"
         onclick="chooseField('${names[i]}')">
        ${names[i]} · ${count}
      </a>
    `;
  }

  // Đưa danh sách lĩnh vực vào phần tử home-fields.
  document.getElementById("home-fields").innerHTML = tiles;
}

/* =====================================================
   8. TRANG DANH SÁCH VIỆC LÀM
   ===================================================== */

// Hàm hiển thị danh sách việc làm.
function renderJobs() {

  // Gọi hàm lọc và sắp xếp.
  // list chứa những việc làm phù hợp với điều kiện hiện tại.
  const list = getFilteredJobs();

  // Tính tổng số trang cần hiển thị.
  // Math.ceil() làm tròn lên.
  // Ví dụ: 13 việc làm / 6 = 2,17 → 3 trang.
  const pages = Math.ceil(list.length / PER_PAGE);

  // Nếu trang hiện tại lớn hơn tổng số trang
  // và vẫn còn kết quả thì quay về trang 1.
  if (currentPage > pages && pages > 0) {
    currentPage = 1;
  }

  // Nếu không có kết quả thì đặt trang hiện tại về 1.
  if (pages === 0) {
    currentPage = 1;
  }

  // Hiển thị tổng số việc làm phù hợp.
  document.getElementById("result-count").textContent = list.length + " việc làm phù hợp";

  // Hiển thị các bộ lọc đang được áp dụng.
  renderChips();

  // Tính vị trí bắt đầu lấy dữ liệu của trang hiện tại.
  // Trang 1: (1 - 1) * 6 = 0.
  // Trang 2: (2 - 1) * 6 = 6.
  const start = (currentPage - 1) * PER_PAGE;

  // Lấy tối đa 6 việc làm từ vị trí start.
  const pageItems = list.slice(start, start + PER_PAGE);

  // Chuyển từng việc làm thành HTML.
  // join("") nối các chuỗi HTML thành một chuỗi duy nhất.
  const html = pageItems
    .map(job => jobCardHTML(job))
    .join("");

  // Đưa HTML danh sách việc làm vào trang.
  document.getElementById("job-list").innerHTML = html;

  // Nếu có kết quả thì ẩn thông báo trống.
  // Nếu không có kết quả thì hiện thông báo.
  document.getElementById("empty").hidden = list.length > 0;

  // Tạo các nút chuyển trang.
  renderPagination(pages);
}

/* =====================================================
   9. BỘ LỌC ĐANG ĐƯỢC ÁP DỤNG
   ===================================================== */

// Hàm tạo một thẻ bộ lọc nhỏ.
// Ví dụ: Python × hoặc Hà Nội ×.
function chipHTML(text, key, value) {

  // Nút × gọi removeFilter() để xóa bộ lọc tương ứng.
  return `
    <span class="chip">
      ${text}
      <button onclick="removeFilter('${key}', '${value}')">×</button>
    </span>
  `;
}

// Hàm hiển thị tất cả bộ lọc đang được áp dụng.
function renderChips() {

  // Khởi tạo chuỗi HTML rỗng.
  let html = "";

  // Nếu có từ khóa thì tạo chip từ khóa.
  if (filters.keyword !== "") {
    html += chipHTML(
      "“" + escapeHTML(filters.keyword) + "”",
      "keyword",
      ""
    );
  }

  // Nếu có địa điểm thì tạo chip địa điểm.
  if (filters.location !== "") {
    html += chipHTML(filters.location, "location", "");
  }

  // Nếu có lĩnh vực thì tạo chip lĩnh vực.
  if (filters.field !== "") {
    html += chipHTML(filters.field, "field", "");
  }

  // Nếu có mức lương thì tạo chip mức lương.
  if (filters.salary !== "") {
    html += chipHTML(
      SALARY_LABELS[filters.salary],
      "salary",
      ""
    );
  }

  // Duyệt qua các loại công việc đã chọn.
  for (let i = 0; i < filters.types.length; i++) {

    // Tạo chip cho từng loại công việc.
    html += chipHTML(filters.types[i], "type", filters.types[i]);
  }

  // Hiển thị các chip trong phần tử có ID chips.
  document.getElementById("chips").innerHTML = html;
}

/* =====================================================
   10. PHÂN TRANG FRONTEND
   ===================================================== */

// Hàm tạo các nút chuyển trang.
// pages là tổng số trang cần hiển thị.
function renderPagination(pages) {

  // Nếu chỉ có 1 trang hoặc không có trang nào
  // thì không cần hiển thị nút phân trang.
  if (pages <= 1) {

    // Xóa toàn bộ HTML phân trang.
    document.getElementById("pagination").innerHTML = "";
    return;
  }

  // Khởi tạo chuỗi HTML.
  let html = "";

  // Tạo nút trang trước.
  // Nếu đang ở trang 1 thì vô hiệu hóa nút này.
  html += ` <button onclick="goToPage(${currentPage - 1})" ${currentPage === 1 ? "disabled" : ""}>←</button>`;

  // Duyệt từ trang 1 đến trang cuối.
  for (let i = 1; i <= pages; i++) {

    // Tạo nút cho từng trang.
    html += `
      <button
        onclick="goToPage(${i})"
        class="${i === currentPage ? "active" : ""}"
      >${i}</button>
    `;
  }

  // Tạo nút trang tiếp theo.
  // Nếu đang ở trang cuối thì vô hiệu hóa nút.
  html += `
    <button
      onclick="goToPage(${currentPage + 1})"
      ${currentPage === pages ? "disabled" : ""}
    >→</button>
  `;

  // Đưa các nút phân trang vào HTML.
  document.getElementById("pagination").innerHTML = html;
}

// Hàm chuyển sang một trang khác.
function goToPage(number) {

  // Lấy danh sách việc làm sau khi lọc.
  const list = getFilteredJobs();

  // Tính tổng số trang của danh sách đã lọc.
  const pages = Math.ceil(list.length / PER_PAGE);

  // Nếu số trang yêu cầu nhỏ hơn 1 hoặc lớn hơn trang cuối
  // thì không thực hiện chuyển trang.
  if (number < 1 || number > pages) return;

  // Cập nhật số trang hiện tại.
  currentPage = number;

  // Hiển thị lại danh sách theo trang mới.
  // Không cần gọi API vì JOBS đã chứa toàn bộ dữ liệu.
  renderJobs();

  // Cuộn màn hình về đầu trang.
  window.scrollTo(0, 0);
}

/* =====================================================
   11. TRANG CHI TIẾT
   ===================================================== */

// Hàm nhận ID việc làm và hiển thị thông tin chi tiết.
function renderDetail(id) {

  // Ban đầu chưa tìm thấy việc làm.
  let job = null;

  // Duyệt qua toàn bộ danh sách việc làm.
  for (let i = 0; i < JOBS.length; i++) {

    // So sánh ID của việc làm với ID trên URL.
    if (JOBS[i].id === id) {

      // Nếu trùng thì lưu việc làm tìm được.
      job = JOBS[i];

      // Dừng vòng lặp vì đã tìm thấy.
      break;
    }
  }

  // Nếu không tìm thấy việc làm.
  if (job === null) {

    // Hiển thị thông báo không tìm thấy.
    document.getElementById("page-detail").innerHTML = `
      <div class="empty" style="margin-top:40px">
        <h3>Không tìm thấy tin tuyển dụng</h3>
        <a href="#/jobs" class="btn">Về danh sách việc làm</a>
      </div>
    `;

    // Dừng hàm, không chạy các đoạn bên dưới.
    return;
  }

  // Khởi tạo HTML cho danh sách công việc tương tự.
  let similarHTML = "";

  // Biến đếm số công việc tương tự đã tìm thấy.
  let found = 0;

  // Duyệt toàn bộ việc làm.
  for (let i = 0; i < JOBS.length; i++) {

    // Kiểm tra công việc có cùng lĩnh vực không.
    // Không lấy chính công việc đang xem.
    // Chỉ lấy tối đa 2 công việc tương tự.
    if (
      JOBS[i].field === job.field &&
      JOBS[i].id !== job.id &&
      found < 2
    ) {

      // Tạo HTML cho công việc tương tự.
      similarHTML += jobCardHTML(JOBS[i]);

      // Tăng số lượng công việc đã tìm được.
      found++;
    }
  }

  // Nếu không có công việc tương tự thì hiển thị thông báo.
  if (similarHTML === "") {
    similarHTML = `<p class="muted">Chưa có việc tương tự.</p>`;
  }

  // Kiểm tra công việc đã được lưu hay chưa.
  // Nếu đã lưu thì hiện "Đã lưu".
  // Nếu chưa lưu thì hiện "Lưu công việc".
  const saveText = savedJobs[job.id] ? "♥  Đã lưu" : "♡  Lưu công việc";

  // Tạo giao diện chi tiết công việc.
  // Các giá trị job được lấy từ đối tượng đã tìm thấy.
  document.getElementById("page-detail").innerHTML = `
    <p class="crumbs">
      Trang chủ / Tìm việc / ${escapeHTML(job.title)}
    </p>

    <section class="card detail-head">
      <div>
        <small>${escapeHTML(job.company)}</small>
        <h1>${escapeHTML(job.title)}</h1>
        <p class="muted">
          ${escapeHTML(job.location)} ·
          ${escapeHTML(job.type)} ·
          ${escapeHTML(job.field)}
        </p>

        <div class="badges">
          <span class="chip">${salaryText(job)} / tháng</span>
          <span class="chip">Hạn ứng tuyển: ${escapeHTML(job.deadline)}</span>
        </div>
      </div>

      <div class="detail-buttons">
        <button class="btn"
          onclick="alert('Bạn đã bấm Ứng tuyển (bản demo).')">
          Ứng tuyển ngay
        </button>

        <button class="btn btn-outline"
          onclick="toggleSave(${job.id})">
          ${saveText}
        </button>
      </div>
    </section>

    <div class="detail-layout">
      <section class="card">
        <h2>Mô tả công việc</h2>
        <p class="muted">${escapeHTML(job.desc)}</p>
        <p class="address">
          Địa điểm làm việc: ${escapeHTML(job.location)}
        </p>
      </section>

      <aside class="side">
        <div class="card">
          <h2 style="margin-top:0">Về ${escapeHTML(job.company)}</h2>
          <div class="info-row">
            <b>Lĩnh vực</b> ${escapeHTML(job.field)}
          </div>
          <div class="info-row">
            <b>Địa điểm</b> ${escapeHTML(job.location)}
          </div>
        </div>

        <h3>Công việc tương tự</h3>
        <div style="display:grid;gap:16px">
          ${similarHTML}
        </div>
      </aside>
    </div>
  `;
}

/* =====================================================
   12. ĐIỀU HƯỚNG
   ===================================================== */

// Hàm xác định người dùng đang ở trang nào.
function route() {

  // Lấy phần hash trên URL.
  // Ví dụ: #/jobs hoặc #/job/1.
  const hash = location.hash;

  // Mặc định trang hiện tại là trang chủ.
  let page = "home";

  // Mặc định chưa có ID việc làm nào.
  let jobId = 0;

  // Nếu URL là #/jobs thì chuyển sang trang danh sách.
  if (hash === "#/jobs") {
    page = "jobs";
  }

  // Nếu URL bắt đầu bằng #/job/
  // thì đây là trang chi tiết.
  if (hash.startsWith("#/job/")) {

    // Xác định trang là detail.
    page = "detail";

    // Cắt phần #/job/ khỏi URL rồi chuyển phần còn lại thành số.
    // Ví dụ: #/job/15 → 15.
    jobId = Number(hash.replace("#/job/", ""));
  }

  // Hiện hoặc ẩn trang chủ.
  // Nếu page là home thì hidden = false.
  document.getElementById("page-home").hidden = page !== "home";

  // Hiện hoặc ẩn trang danh sách.
  document.getElementById("page-jobs").hidden = page !== "jobs";

  // Hiện hoặc ẩn trang chi tiết.
  document.getElementById("page-detail").hidden = page !== "detail";

  // Đánh dấu menu trang chủ đang được chọn.
  document.getElementById("nav-home").className =
    page === "home" ? "active" : "";

  // Đánh dấu menu tìm việc đang được chọn.
  document.getElementById("nav-jobs").className =
    page !== "home" ? "active" : "";

  // Nếu đang ở trang chủ thì gọi renderHome().
  if (page === "home") {
    renderHome();
  }

  // Nếu đang ở trang danh sách thì đồng bộ bộ lọc
  // và hiển thị danh sách việc làm.
  if (page === "jobs") {
    syncInputs();
    renderJobs();
  }

  // Nếu đang ở trang chi tiết thì tìm việc làm theo ID.
  if (page === "detail") {
    renderDetail(jobId);
  }

  // Cuộn màn hình lên đầu trang.
  window.scrollTo(0, 0);
}


/* =====================================================
   13. ĐỒNG BỘ INPUT
   ===================================================== */

// Hàm cập nhật giá trị của các ô nhập liệu theo filters.
function syncInputs() {
  // Gán từ khóa tìm kiếm vào ô keyword.
  document.getElementById("keyword").value = filters.keyword;

  // Gán địa điểm vào ô location.
  document.getElementById("location").value = filters.location;

  // Gán địa điểm vào bộ lọc bên sidebar.
  document.getElementById("f-location").value = filters.location;

  // Gán lĩnh vực vào bộ lọc bên sidebar.
  document.getElementById("f-field").value = filters.field;

  // Gán mức lương vào bộ lọc bên sidebar.
  document.getElementById("f-salary").value = filters.salary;

  // Gán kiểu sắp xếp vào ô sort.
  document.getElementById("sort").value = sortBy;

  // Lấy tất cả checkbox loại công việc trong f-types.
  const boxes = document.querySelectorAll("#f-types input");

  // Duyệt qua từng checkbox.
  for (let i = 0; i < boxes.length; i++) {

    // Nếu giá trị checkbox nằm trong filters.types
    // thì đánh dấu checkbox đó đã được chọn.
    boxes[i].checked = filters.types.includes(boxes[i].value);
  }
}

// Hàm áp dụng các bộ lọc hiện tại.
function applyFilters() {
  // Khi thay đổi bộ lọc thì quay lại trang 1.
  currentPage = 1;

  // Cập nhật giá trị trên các ô nhập liệu.
  syncInputs();

  // Lọc và hiển thị lại danh sách.
  renderJobs();
}

// Hàm xử lý dữ liệu trước khi đưa vào HTML.
function escapeHTML(text) {
  // Chuyển dữ liệu thành chuỗi.
  // Nếu dữ liệu null hoặc undefined thì thay bằng chuỗi rỗng.
  return String(text ?? "")

    // Chuyển ký tự & thành mã HTML an toàn.
    .replace(/&/g, "&amp;")

    // Chuyển ký tự < thành mã HTML an toàn.
    .replace(/</g, "&lt;")

    // Chuyển ký tự > thành mã HTML an toàn.
    .replace(/>/g, "&gt;")

    // Chuyển dấu nháy kép thành mã HTML an toàn.
    .replace(/"/g, "&quot;")

    // Chuyển dấu nháy đơn thành mã HTML an toàn.
    .replace(/'/g, "&#039;");
}

/* =====================================================
   14. CÁC HÀM ĐƯỢC GỌI TỪ HTML
   ===================================================== */

// Hàm tìm kiếm từ trang chủ.
function homeSearch() {

  // Xóa các bộ lọc cũ.
  resetFilters();

  // Lấy từ khóa người dùng nhập ở trang chủ.
  // trim() loại bỏ khoảng trắng thừa.
  filters.keyword = document
    .getElementById("home-keyword")
    .value.trim();

  // Lấy địa điểm người dùng chọn ở trang chủ.
  filters.location = document
    .getElementById("home-location")
    .value;

  // Đưa trang hiện tại về trang 1.
  currentPage = 1;

  // Chuyển URL sang trang danh sách việc làm.
  location.hash = "#/jobs";

  // Nếu URL đã là #/jobs thì không có sự kiện hashchange mới.
  // Vì vậy cần gọi route() trực tiếp để cập nhật giao diện.
  if (location.hash === "#/jobs") {
    route();
  }
}

// Hàm được gọi khi người dùng chọn một lĩnh vực trên trang chủ.
function chooseField(name) {

  // Xóa các bộ lọc cũ.
  resetFilters();

  // Gán lĩnh vực vừa chọn vào bộ lọc.
  filters.field = name;

  // Đưa trang hiện tại về trang 1.
  currentPage = 1;
}

// Hàm tìm kiếm trên trang danh sách việc làm.
function doSearch() {

  // Lấy từ khóa từ ô tìm kiếm.
  filters.keyword = document
    .getElementById("keyword")
    .value.trim();

  // Lấy địa điểm từ ô tìm kiếm.
  filters.location = document
    .getElementById("location")
    .value;

  // Áp dụng bộ lọc và cập nhật giao diện.
  applyFilters();
}

// Hàm xử lý khi người dùng thay đổi bộ lọc sidebar.
function onSidebarChange() {

  // Lấy lĩnh vực được chọn.
  filters.field = document.getElementById("f-field").value;

  // Lấy địa điểm được chọn.
  filters.location = document.getElementById("f-location").value;

  // Lấy mức lương được chọn.
  filters.salary = document.getElementById("f-salary").value;

  // Xóa danh sách loại công việc đã chọn trước đó.
  filters.types = [];

  // Lấy tất cả checkbox loại công việc.
  const boxes = document.querySelectorAll("#f-types input");

  // Duyệt qua từng checkbox.
  for (let i = 0; i < boxes.length; i++) {

    // Nếu checkbox đang được tích.
    if (boxes[i].checked) {

      // Thêm giá trị checkbox vào filters.types.
      filters.types.push(boxes[i].value);
    }
  }

  // Áp dụng toàn bộ bộ lọc.
  applyFilters();
}

// Hàm xử lý khi người dùng thay đổi kiểu sắp xếp.
function onSortChange() {

  // Lấy giá trị sắp xếp từ ô select.
  sortBy = document.getElementById("sort").value;

  // Sắp xếp và hiển thị lại danh sách.
  applyFilters();
}

// Hàm xóa tất cả bộ lọc.
function clearAll() {

  // Đưa filters về trạng thái ban đầu.
  resetFilters();

  // Cập nhật giao diện.
  applyFilters();
}

// Hàm xóa một bộ lọc cụ thể.
function removeFilter(key, value) {

  // Nếu bộ lọc cần xóa là loại công việc.
  if (key === "type") {

    // Tạo mảng mới chỉ giữ lại các loại không trùng với value.
    filters.types = filters.types.filter(type => type !== value);

  } else {

    // Với các bộ lọc khác, chỉ cần gán chuỗi rỗng.
    filters[key] = "";
  }

  // Áp dụng lại các bộ lọc sau khi xóa.
  applyFilters();
}

// Hàm bật hoặc tắt trạng thái lưu công việc.
async function toggleSave(id) {
  try {
    if (savedJobs[id]) {
      await SavedJobs.unsave(id);   // đã lưu → gọi API bỏ lưu
      savedJobs[id] = false;
    } else {
      await SavedJobs.save(id);     // chưa lưu → gọi API lưu
      savedJobs[id] = true;
    }
    renderDetail(id);               // vẽ lại để đổi chữ ♡ / ♥
  } catch (error) {
    // Lỗi hay gặp: chưa đăng nhập (401)
    alert(error.message || "Không lưu được. Hãy đăng nhập rồi thử lại.");
  }
}

/* =====================================================
   15. KHỞI TẠO CÁC Ô SELECT
   ===================================================== */

// Hàm tạo các option cho một thẻ select.
// selectId: ID của thẻ select trong HTML.
// key: tên thuộc tính cần lấy từ JOBS.
// firstText: nội dung của option đầu tiên.
function fillSelect(selectId, key, firstText) {

  // Tạo mảng lưu các giá trị không bị trùng lặp.
  const values = [];

  // Duyệt qua toàn bộ việc làm.
  for (let i = 0; i < JOBS.length; i++) {

    // Lấy giá trị của thuộc tính tương ứng.
    // Ví dụ key = "location" thì lấy JOBS[i].location.
    const value = JOBS[i][key];

    // Nếu có giá trị và chưa xuất hiện trong mảng values.
    if (value && !values.includes(value)) {

      // Thêm giá trị vào mảng.
      values.push(value);
    }
  }

  // Tạo option đầu tiên.
  // Ví dụ: Tất cả địa điểm.
  let html = `<option value="">${firstText}</option>`;

  // Duyệt qua danh sách các giá trị không trùng.
  for (let i = 0; i < values.length; i++) {

    // Tạo một option tương ứng với mỗi giá trị.
    html += `
      <option value="${escapeHTML(values[i])}">
        ${escapeHTML(values[i])}
      </option>
    `;
  }

  // Đưa các option vào thẻ select trong HTML.
  document.getElementById(selectId).innerHTML = html;
}


/* =====================================================
   16. KHỞI ĐỘNG ỨNG DỤNG
   ===================================================== */

// Hàm khởi tạo các thành phần giao diện sau khi có dữ liệu.
function startApp() {

  // Tạo danh sách lĩnh vực trong bộ lọc sidebar.
  fillSelect("f-field", "field", "Tất cả");

  // Tạo danh sách địa điểm trong bộ lọc sidebar.
  fillSelect("f-location", "location", "Tất cả");

  // Tạo danh sách địa điểm trong ô tìm kiếm trang danh sách.
  fillSelect("location", "location", "Tất cả địa điểm");

  // Tạo danh sách địa điểm trong ô tìm kiếm trang chủ.
  fillSelect("home-location", "location", "Địa điểm");

  // Lắng nghe sự thay đổi của URL hash.
  // Khi URL thay đổi thì gọi route() để chuyển giao diện.
  window.onhashchange = route;

  // Kiểm tra URL hiện tại và hiển thị đúng trang.
  route();
}

// Bắt đầu chạy ứng dụng.
// Gọi API để tải dữ liệu việc làm trước.
// Sau khi tải xong, loadJobs() sẽ gọi startApp().
loadJobs();
