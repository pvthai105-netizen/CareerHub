
// =====================================================
// FILE: saved_tab.js
//
// Chức năng:
// 1. Chuyển đổi giữa tab "Đã ứng tuyển" và "Đã lưu".
// 2. Gọi API lấy danh sách công việc đã lưu.
// 3. Hiển thị danh sách công việc đã lưu lên giao diện.
// 4. Cho phép người dùng bỏ lưu công việc.
//
// File này cần được nạp SAU:
// - api.js
// - saved_jobs.js
// - my_applications.js
//
// File HTML sử dụng: my_applications.html
// =====================================================


// Chờ cho đến khi toàn bộ HTML được tải xong
// rồi mới thực hiện các thao tác với phần tử trên trang.
document.addEventListener("DOMContentLoaded", function () {

  // Đường dẫn đến trang chủ và phần chi tiết công việc.
  // Ví dụ: job_id = 15 thì đường dẫn là home.html#/job/15.
  const DETAIL_URL = "home.html#/job/";

  // Tạo đối tượng ánh xạ mã loại công việc sang tên tiếng Việt.
  // Ví dụ: INTERNSHIP sẽ hiển thị là Thực tập.
  const TYPE_LABELS = {
    INTERNSHIP: "Thực tập",
    PART_TIME: "Bán thời gian",
    FULL_TIME: "Toàn thời gian",
    REMOTE: "Làm từ xa"
  };

  // --------------------------------------------------
  // 1. LẤY CÁC PHẦN TỬ HTML CẦN SỬ DỤNG
  // --------------------------------------------------

  // Lấy nút chuyển sang tab Đã ứng tuyển.
  const tabApplied = document.getElementById("tab-applied");

  // Lấy nút chuyển sang tab Đã lưu.
  const tabSaved = document.getElementById("tab-saved");

  // Lấy khu vực hiển thị nội dung tab Đã ứng tuyển.
  const panelApplied = document.getElementById("panel-applied");

  // Lấy khu vực hiển thị nội dung tab Đã lưu.
  const panelSaved = document.getElementById("panel-saved");

  // Lấy phần tử chứa danh sách các công việc đã lưu.
  const savedList = document.getElementById("saved-list");

  // Lấy phần tử hiển thị thông báo.
  // Ví dụ: Đang tải dữ liệu hoặc chưa có công việc nào.
  const savedMessage = document.getElementById("saved-message");

  // Lấy phần tử hiển thị tổng số công việc đã lưu.
  const savedCount = document.getElementById("saved-count");


  // Kiểm tra xem trang HTML có tồn tại nút và khu vực tab Đã lưu không.
  // Nếu không có thì dừng chương trình để tránh lỗi JavaScript.
  if (!tabSaved || !panelSaved) return;


  // Khởi tạo biến total để lưu tổng số công việc đang được lưu.
  let total = 0;


  // --------------------------------------------------
  // 2. CHUYỂN ĐỔI GIỮA CÁC TAB
  // --------------------------------------------------

  // Hàm showTab() dùng để hiển thị tab mà người dùng lựa chọn.
  // name nhận một trong hai giá trị: "saved" hoặc "applied".
  function showTab(name) {

    // Kiểm tra xem tab được chọn có phải tab Đã lưu hay không.
    // Nếu đúng thì isSaved = true, ngược lại là false.
    const isSaved = (name === "saved");

    // Nếu đang chọn tab Đã lưu thì ẩn nội dung Đã ứng tuyển.
    // Nếu đang chọn tab Đã ứng tuyển thì hiện nội dung này.
    panelApplied.hidden = isSaved;

    // Thực hiện ngược lại đối với khu vực Đã lưu.
    // Chỉ hiện khu vực Đã lưu khi isSaved = true.
    panelSaved.hidden = !isSaved;

    // Thêm hoặc xóa class is-active cho nút Đã ứng tuyển.
    // Nếu tab này được chọn thì thêm class.
    // Nếu không được chọn thì xóa class.
    tabApplied.classList.toggle("is-active", !isSaved);

    // Cập nhật trạng thái active cho nút Đã lưu.
    tabSaved.classList.toggle("is-active", isSaved);

    // Thay đổi phần hash trên URL mà không tải lại trang.
    // Ví dụ: my_applications.html#saved.
    // Điều này giúp có thể mở trực tiếp tab Đã lưu bằng đường dẫn.
    history.replaceState(null, "", "#" + name);
  }


  // --------------------------------------------------
  // 3. CÁC HÀM NHỎ HỖ TRỢ
  // --------------------------------------------------

  // Hàm setCount() dùng để cập nhật số lượng công việc đã lưu.
  // Tham số n là tổng số công việc hiện có.
  function setCount(n) {

    // Gán số lượng mới cho biến total.
    total = n;

    // Hiển thị số lượng lên giao diện HTML.
    savedCount.textContent = n;

    // Kiểm tra nếu danh sách không còn công việc nào.
    if (n === 0) {

      // Hiển thị khu vực thông báo.
      savedMessage.hidden = false;

      // Hiển thị nội dung thông báo khi chưa lưu công việc nào.
      savedMessage.textContent =
        "Bạn chưa lưu việc làm nào. Hãy bấm ♡ ở tin tuyển dụng để lưu lại.";
    }
  }


  // Hàm makeText() dùng để tạo một phần tử HTML có nội dung văn bản.
  // tag: tên thẻ HTML, ví dụ p, a, button.
  // className: tên class CSS.
  // text: nội dung muốn hiển thị.
  function makeText(tag, className, text) {

    // Tạo phần tử HTML theo tên thẻ được truyền vào.
    const element = document.createElement(tag);

    // Gán class CSS cho phần tử vừa tạo.
    element.className = className;

    // Gán nội dung văn bản cho phần tử.
    // textContent giúp hiển thị văn bản an toàn,
    // tránh thực thi mã HTML hoặc JavaScript không mong muốn.
    element.textContent = text;

    // Trả về phần tử HTML đã tạo để sử dụng ở nơi khác.
    return element;
  }


  // Hàm formatSalary() dùng để định dạng mức lương.
  // Ví dụ: 4000000 và 7000000 thành "4 – 7 triệu".
  function formatSalary(min, max) {

    // Chia mức lương tối thiểu cho 1 triệu.
    // Nhân 10 rồi làm tròn để giữ tối đa một chữ số thập phân.
    // Sau đó chia lại cho 10.
    const a = Math.round(min / 1000000 * 10) / 10;

    // Thực hiện tương tự với mức lương tối đa.
    const b = Math.round(max / 1000000 * 10) / 10;

    // Ghép hai mức lương thành chuỗi.
    // Dùng replace() để đổi dấu chấm thập phân thành dấu phẩy.
    return (a + " – " + b + " triệu").replace(/\./g, ",");
  }


  // --------------------------------------------------
  // 4. TẠO GIAO DIỆN CHO MỘT CÔNG VIỆC ĐÃ LƯU
  // --------------------------------------------------

  // Hàm createSavedItem() nhận vào một bản ghi công việc đã lưu.
  // Sau đó tạo ra một dòng HTML để hiển thị công việc đó.
  function createSavedItem(saved) {

    // Lấy thông tin chi tiết công việc từ thuộc tính saved.job.
    const job = saved.job;

    // Tạo thẻ div bao bên ngoài một công việc.
    const item = document.createElement("div");

    // Gán class saved-item để CSS định dạng giao diện.
    item.className = "saved-item";


    // ------------------------------------------------
    // 4.1. KHU VỰC BÊN TRÁI: THÔNG TIN CÔNG VIỆC
    // ------------------------------------------------

    // Tạo thẻ div chứa thông tin công việc.
    const info = document.createElement("div");

    // Gán class CSS cho khu vực thông tin.
    info.className = "saved-info";

    // Tạo thẻ a hiển thị tên công việc.
    // makeText() tạo phần tử và gán nội dung là tên công việc.
    const title = makeText("a", "saved-title", job.title);

    // Gán đường dẫn đến trang chi tiết công việc.
    // job.job_id là ID của công việc.
    title.href = DETAIL_URL + job.job_id;

    // Đưa thẻ tên công việc vào khu vực thông tin.
    info.appendChild(title);


    // Tạo thẻ p hiển thị tên công ty.
    // Nếu company_name không có dữ liệu thì hiển thị chuỗi rỗng.
    info.appendChild(
      makeText("p", "saved-company", job.company_name || "")
    );


    // Lấy tên loại công việc tiếng Việt từ TYPE_LABELS.
    // Nếu không tìm thấy mã loại công việc thì giữ nguyên giá trị ban đầu.
    const typeText = TYPE_LABELS[job.job_type] || job.job_type;

    // Tạo thẻ p hiển thị địa điểm, loại công việc và mức lương.
    info.appendChild(makeText(
      "p",
      "saved-meta",
      job.location + " · " +
      typeText + " · " +
      formatSalary(job.salary_min, job.salary_max)
    ));


    // ------------------------------------------------
    // 4.2. KHU VỰC GIỮA: NGÀY LƯU CÔNG VIỆC
    // ------------------------------------------------

    // Chuyển thời gian lưu từ Backend thành đối tượng Date.
    // toLocaleDateString("vi-VN") định dạng ngày theo kiểu Việt Nam.
    const savedDate = new Date(saved.saved_at).toLocaleDateString("vi-VN");

    // Tạo thẻ p hiển thị ngày người dùng lưu công việc.
    const date = makeText("p", "saved-date", "Đã lưu " + savedDate);


    // ------------------------------------------------
    // 4.3. KHU VỰC BÊN PHẢI: CÁC NÚT THAO TÁC
    // ------------------------------------------------

    // Tạo thẻ div chứa các nút thao tác.
    const actions = document.createElement("div");

    // Gán class CSS cho khu vực thao tác.
    actions.className = "saved-actions";


    // Tạo thẻ a có nội dung Chi tiết.
    const detailLink = makeText("a", "saved-detail", "Chi tiết");

    // Gán đường dẫn đến trang chi tiết công việc.
    detailLink.href = DETAIL_URL + job.job_id;


    // Tạo nút Bỏ lưu.
    const unsaveButton = makeText("button", "saved-unsave", "Bỏ lưu");

    // Đặt type = button để nút không vô tình gửi form.
    unsaveButton.type = "button";


    // Đưa nút Chi tiết vào khu vực thao tác.
    actions.appendChild(detailLink);

    // Đưa nút Bỏ lưu vào khu vực thao tác.
    actions.appendChild(unsaveButton);


    // ------------------------------------------------
    // 4.4. XỬ LÝ SỰ KIỆN BẤM NÚT BỎ LƯU
    // ------------------------------------------------

    // Đăng ký sự kiện click cho nút Bỏ lưu.
    // Hàm bất đồng bộ cho phép sử dụng await khi gọi API.
    unsaveButton.addEventListener("click", async function () {

      // Khóa nút để tránh người dùng nhấn nhiều lần.
      unsaveButton.disabled = true;

      // Thay đổi nội dung nút để thông báo đang xử lý.
      unsaveButton.textContent = "Đang bỏ lưu...";


      // Dùng try để xử lý lỗi khi gọi API.
      try {

        // Gọi hàm unsave() trong SavedJobs để gửi yêu cầu xóa.
        // Truyền ID công việc cần bỏ lưu.
        await SavedJobs.unsave(job.job_id);

        // Chỉ xóa dòng công việc khỏi giao diện
        // sau khi Backend xác nhận bỏ lưu thành công.
        item.remove();

        // Giảm tổng số công việc đã lưu đi 1
        // và cập nhật lại số lượng trên giao diện.
        setCount(total - 1);


      } catch (error) {

        // Nếu API thất bại thì mở khóa nút.
        unsaveButton.disabled = false;

        // Khôi phục nội dung nút ban đầu.
        unsaveButton.textContent = "Bỏ lưu";

        // Hiển thị thông báo lỗi cho người dùng.
        alert(error.message || "Không bỏ lưu được, hãy thử lại.");
      }
    });


    // ------------------------------------------------
    // 4.5. GHÉP CÁC PHẦN TỬ VÀO DÒNG CÔNG VIỆC
    // ------------------------------------------------

    // Đưa khu vực thông tin công việc vào thẻ bao ngoài.
    item.appendChild(info);

    // Đưa khu vực ngày lưu vào thẻ bao ngoài.
    item.appendChild(date);

    // Đưa khu vực nút thao tác vào thẻ bao ngoài.
    item.appendChild(actions);

    // Trả về thẻ HTML hoàn chỉnh để đưa vào danh sách.
    return item;
  }


  // --------------------------------------------------
  // 5. TẢI DANH SÁCH CÔNG VIỆC ĐÃ LƯU TỪ BACKEND
  // --------------------------------------------------

  // Hàm loadSavedJobs() dùng để lấy dữ liệu từ API
  // và hiển thị danh sách công việc đã lưu.
  async function loadSavedJobs() {

    // Hiển thị khu vực thông báo trong lúc đang tải dữ liệu.
    savedMessage.hidden = false;

    // Thay đổi nội dung thông báo thành trạng thái đang tải.
    savedMessage.textContent = "Đang tải việc làm đã lưu...";

    // Xóa toàn bộ danh sách cũ trước khi tải dữ liệu mới.
    savedList.replaceChildren();


    // Dùng try để xử lý lỗi khi gọi API.
    try {

      // Gọi API lấy danh sách công việc đã lưu.
      // Kết quả trả về là một mảng các bản ghi đã lưu.
      const items = await SavedJobs.list();

      // Lấy số lượng phần tử trong mảng.
      // Đây chính là tổng số công việc đã lưu.
      total = items.length;

      // Hiển thị tổng số công việc lên giao diện.
      savedCount.textContent = total;


      // Kiểm tra danh sách có rỗng hay không.
      if (total === 0) {

        // Nếu không có công việc nào thì gọi setCount(0).
        // Hàm này sẽ hiển thị thông báo chưa lưu công việc nào.
        setCount(0);

        // Dừng hàm vì không còn dữ liệu để hiển thị.
        return;
      }


      // Nếu có công việc thì ẩn thông báo tải dữ liệu.
      savedMessage.hidden = true;


      // Duyệt lần lượt từng phần tử trong mảng items.
      for (let i = 0; i < items.length; i++) {

        // Tạo giao diện cho công việc hiện tại bằng createSavedItem().
        // Sau đó đưa dòng công việc vào phần danh sách savedList.
        savedList.appendChild(createSavedItem(items[i]));
      }


    } catch (error) {

      // Nếu không lấy được dữ liệu thì hiển thị thông báo lỗi.
      // Ưu tiên nội dung lỗi từ API, nếu không có thì dùng nội dung mặc định.
      savedMessage.textContent =
        error.message || "Không tải được danh sách việc đã lưu.";
    }
  }


  // --------------------------------------------------
  // 6. KHỞI ĐỘNG CHƯƠNG TRÌNH
  // --------------------------------------------------

  // Khi người dùng nhấn tab Đã ứng tuyển,
  // gọi showTab() để hiển thị nội dung của tab này.
  tabApplied.addEventListener("click", function () {
    showTab("applied");
  });


  // Khi người dùng nhấn tab Đã lưu,
  // gọi showTab() để hiển thị nội dung của tab này.
  tabSaved.addEventListener("click", function () {
    showTab("saved");
  });


  // Kiểm tra phần hash trên URL hiện tại.
  // Nếu URL kết thúc bằng #saved thì tự động mở tab Đã lưu.
  if (window.location.hash === "#saved") {
    showTab("saved");
  }


  // Gọi hàm tải danh sách công việc đã lưu.
  // Tải sẵn dữ liệu để có thể hiển thị số lượng trên tab.
  loadSavedJobs();

});