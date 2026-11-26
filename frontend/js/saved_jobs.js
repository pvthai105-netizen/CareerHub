
/* =====================================================
   FILE: saved_jobs.js

   Chức năng:
   - Gọi API để lưu công việc.
   - Gọi API để bỏ lưu công việc.
   - Lấy danh sách công việc đã lưu.
   - Kiểm tra một công việc đã được lưu hay chưa.
   - Thiết lập hoạt động cho nút Lưu / Bỏ lưu.

   File này được sử dụng ở:
   - Trang chủ.
   - Trang chi tiết công việc.
   - Trang Việc làm của tôi.

   Lưu ý:
   Phải nạp saved_jobs.js SAU api.js vì file này sử dụng
   biến api để gửi yêu cầu đến Backend.

   Các API Backend:
   GET    /user/saved-jobs                 : Lấy danh sách đã lưu.
   POST   /user/saved-jobs/{job_id}        : Lưu công việc.
   DELETE /user/saved-jobs/{job_id}        : Bỏ lưu công việc.
   GET    /user/saved-jobs/{job_id}/check  : Kiểm tra trạng thái lưu.
   ===================================================== */


// Tạo đối tượng SavedJobs để quản lý các chức năng liên quan đến việc làm đã lưu.
const SavedJobs = {

  // --------------------------------------------------
  // 1. LẤY DANH SÁCH CÔNG VIỆC ĐÃ LƯU
  // --------------------------------------------------

  // Hàm bất đồng bộ dùng để lấy danh sách việc làm đã lưu của người dùng.
  async list() {

    // Gửi yêu cầu GET đến Backend.
    // skip=0: Bắt đầu lấy dữ liệu từ phần tử đầu tiên.
    // limit=100: Lấy tối đa 100 công việc.
    // Kết quả API được trả về cho nơi gọi hàm.
    return await api.get("/user/saved-jobs?skip=0&limit=100");
  },


  // --------------------------------------------------
  // 2. LƯU MỘT CÔNG VIỆC
  // --------------------------------------------------

  // jobId: ID của công việc muốn lưu.
  async save(jobId) {

    // Gửi yêu cầu POST đến Backend để lưu công việc có ID tương ứng.
    // Nối jobId vào cuối đường dẫn API.
    return await api.post("/user/saved-jobs/" + jobId);
  },


  // --------------------------------------------------
  // 3. BỎ LƯU MỘT CÔNG VIỆC
  // --------------------------------------------------

  // jobId: ID của công việc muốn bỏ lưu.
  async unsave(jobId) {

    // Kiểm tra trong api.js có hỗ trợ phương thức delete hay không.
    // Nếu không có thì không thể gửi yêu cầu xóa dữ liệu.
    if (typeof api.delete !== "function") {

      // Tạo lỗi và thông báo rõ nguyên nhân cho người lập trình.
      throw new Error("api.js chưa có hàm delete – xem hướng dẫn bước 3 để thêm vào.");
    }

    // Gửi yêu cầu DELETE đến Backend để xóa công việc khỏi danh sách đã lưu.
    return await api.delete("/user/saved-jobs/" + jobId);
  },


  // --------------------------------------------------
  // 4. KIỂM TRA MỘT CÔNG VIỆC ĐÃ ĐƯỢC LƯU HAY CHƯA
  // --------------------------------------------------

  // jobId: ID của công việc cần kiểm tra.
  async isSaved(jobId) {

    // Gửi yêu cầu GET đến API kiểm tra trạng thái lưu của công việc.
    // Backend trả về dữ liệu có dạng: { is_saved: true/false }.
    const result = await api.get("/user/saved-jobs/" + jobId + "/check");

    // Trả về giá trị is_saved.
    // true: Công việc đã được lưu.
    // false: Công việc chưa được lưu.
    return result.is_saved;
  },


  // --------------------------------------------------
  // 5. LẤY DANH SÁCH ID CỦA CÁC CÔNG VIỆC ĐÃ LƯU
  // --------------------------------------------------

  async getIds() {

    // Sử dụng try để thử lấy danh sách công việc đã lưu.
    try {

      // Gọi hàm list() để lấy toàn bộ danh sách việc làm đã lưu.
      const items = await SavedJobs.list();

      // Dùng map() để duyệt qua từng công việc trong danh sách.
      // Chỉ lấy thuộc tính job_id của mỗi công việc.
      // Ví dụ: [{job_id: 3}, {job_id: 7}] sẽ thành [3, 7].
      return items.map(function (item) {
        return item.job_id;
      });

    } catch (error) {

      // Nếu xảy ra lỗi (ví dụ chưa đăng nhập hoặc API lỗi),
      // trả về mảng rỗng để tránh làm gián đoạn trang.
      return [];
    }
  }
};


// =====================================================
// 6. THIẾT LẬP NÚT LƯU / BỎ LƯU CÔNG VIỆC
// =====================================================

// Hàm này dùng để biến một nút HTML thành nút Lưu / Bỏ lưu.
//
// button: Phần tử nút HTML cần thiết lập.
// jobId: ID của công việc tương ứng với nút.
// options: Các tùy chọn bổ sung.
//
// options.short = true:
// Chỉ hiển thị biểu tượng trái tim ♡ / ♥.
//
// options.saved = true hoặc false:
// Truyền trạng thái đã biết trước để không phải gọi API kiểm tra.
async function setupSaveButton(button, jobId, options) {

    // Nếu không truyền options thì khởi tạo một đối tượng rỗng.
    options = options || {};

    // Mặc định công việc chưa được lưu.
    let saved = false;


    // --------------------------------------------------
    // 6.1. KIỂM TRA NGƯỜI DÙNG ĐÃ ĐĂNG NHẬP HAY CHƯA
    // --------------------------------------------------

    // Tạo hàm kiểm tra trạng thái đăng nhập.
    function isLoggedIn() {

        // Lấy thông tin người dùng hiện tại từ AuthGuard.
        const currentUser = AuthGuard.getUser();

        // Chuyển kết quả thành kiểu Boolean.
        // Có thông tin người dùng: true.
        // Không có thông tin người dùng: false.
        return !!currentUser;
    }


    // --------------------------------------------------
    // 6.2. HIỂN THỊ TRẠNG THÁI CỦA NÚT
    // --------------------------------------------------

    // Hàm cập nhật nội dung và tiêu đề của nút.
    function showState() {

        // Nếu options.short bằng true thì chỉ hiển thị biểu tượng.
        if (options.short) {

            // Đã lưu: ♥.
            // Chưa lưu: ♡.
            button.textContent = saved ? "♥" : "♡";

        } else {

            // Nếu không dùng chế độ short thì hiển thị nội dung đầy đủ.
            button.textContent = saved
                ? "♥ Đã lưu"
                : "♡ Lưu công việc";
        }

        // Cập nhật nội dung gợi ý khi người dùng di chuột vào nút.
        // Đã lưu thì hiện "Bỏ lưu".
        // Chưa lưu thì hiện "Lưu công việc".
        button.title = saved ? "Bỏ lưu" : "Lưu công việc";
    }


    // --------------------------------------------------
    // 6.3. KIỂM TRA TRẠNG THÁI LƯU BAN ĐẦU
    // --------------------------------------------------

    // Kiểm tra người dùng đã đăng nhập hay chưa thông qua Token.
    if (!Auth.getToken()) {

        // Nếu không có Token thì mặc định công việc chưa được lưu.
        saved = false;

    } else if (options.saved !== undefined) {

        // Nếu đã truyền sẵn trạng thái lưu qua options.saved,
        // sử dụng luôn giá trị đó mà không cần gọi API.
        saved = options.saved;

    } else {

        // Nếu đã đăng nhập nhưng chưa có trạng thái lưu,
        // gọi API để kiểm tra công việc đã được lưu hay chưa.
        try {

            // Nhận kết quả true hoặc false từ API.
            saved = await SavedJobs.isSaved(jobId);

        } catch (error) {

            // Nếu API gặp lỗi thì mặc định công việc chưa được lưu.
            saved = false;
        }
    }

    // Sau khi xác định trạng thái ban đầu,
    // gọi showState() để hiển thị đúng nội dung của nút.
    showState();


    // --------------------------------------------------
    // 6.4. XỬ LÝ SỰ KIỆN KHI NGƯỜI DÙNG NHẤN NÚT
    // --------------------------------------------------

    // Gán sự kiện onclick cho nút.
    // Hàm bên trong sẽ chạy khi người dùng nhấn nút.
    button.onclick = async function (event) {

      // Ngăn hành vi mặc định của nút hoặc thẻ liên kết.
      // Ví dụ: ngăn chuyển trang khi nút nằm trong thẻ <a>.
      event.preventDefault();

      // Ngăn sự kiện nhấn nút lan lên các phần tử cha.
      // Giúp tránh trường hợp nhấn nút lưu nhưng lại kích hoạt thẻ công việc.
      event.stopPropagation();


      // ------------------------------------------------
      // 6.4.1. KIỂM TRA ĐĂNG NHẬP TRƯỚC KHI LƯU
      // ------------------------------------------------

      // Kiểm tra cả Token và thông tin người dùng.
      // Nếu thiếu một trong hai thì yêu cầu đăng nhập.
      if (!Auth.getToken() || !AuthGuard.getUser()) {

        // Hiển thị thông báo yêu cầu đăng nhập.
        alert("Vui lòng đăng nhập để lưu công việc!");

        // Lấy URL hiện tại của trang đang sử dụng.
        const currentUrl = window.location.href;

        // Chuyển người dùng đến trang đăng nhập.
        // Đồng thời đính kèm URL hiện tại vào tham số redirect.
        // Sau khi đăng nhập có thể sử dụng URL này để quay lại trang trước.
        window.location.href =
            "login.html?redirect=" + encodeURIComponent(currentUrl);

        // Dừng hàm tại đây, không thực hiện lưu công việc.
        return;
      }


      // ------------------------------------------------
      // 6.4.2. KHÓA NÚT TRONG KHI GỌI API
      // ------------------------------------------------

      // Vô hiệu hóa nút để tránh người dùng nhấn liên tục
      // trong lúc Backend đang xử lý yêu cầu.
      button.disabled = true;


      // ------------------------------------------------
      // 6.4.3. GỌI API LƯU HOẶC BỎ LƯU
      // ------------------------------------------------

      // Dùng try để xử lý các lỗi có thể xảy ra khi gọi API.
      try {

        // Nếu saved = true nghĩa là công việc đã được lưu.
        if (saved) {

          // Gọi API để bỏ lưu công việc.
          await SavedJobs.unsave(jobId);

        } else {

          // Nếu saved = false thì gọi API để lưu công việc.
          await SavedJobs.save(jobId);
        }


        // ------------------------------------------------
        // 6.4.4. CẬP NHẬT TRẠNG THÁI SAU KHI API THÀNH CÔNG
        // ------------------------------------------------

        // Đảo ngược trạng thái lưu.
        // true thành false, false thành true.
        // Chỉ thực hiện sau khi API trả về thành công.
        saved = !saved;

        // Cập nhật lại nội dung và biểu tượng của nút.
        showState();


      } catch (error) {

        // Nếu gọi API thất bại thì ghi lỗi vào Console.
        console.error("Lỗi lưu công việc:", error);

        // Hiển thị thông báo lỗi cho người dùng.
        // Nếu Backend trả về nội dung lỗi thì hiển thị nội dung đó.
        // Nếu không có thì sử dụng thông báo mặc định.
        alert(
            error.message ||
            "Không thực hiện được. Vui lòng thử lại."
        );

      } finally {

        // Luôn mở lại nút sau khi xử lý xong,
        // kể cả khi gọi API thành công hay thất bại.
        button.disabled = false;
      }
    };
}