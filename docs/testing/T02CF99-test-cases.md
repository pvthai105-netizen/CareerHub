# Test case — T02CF99: Xác thực (Auth), Phân quyền (RBAC), Quản trị người dùng & Kiểm duyệt tin (Admin)

Phạm vi kiểm thử gồm toàn bộ chức năng do **Phạm Văn Thái (B25DTCN298)** phụ trách:
1. **Module Xác thực & Đăng nhập/Đăng ký (`T02CEBD`):** `/api/auth/register`, `/api/auth/login`, `/api/auth/me`, `login.html`, `register.html`, `js/auth.js`, `js/auth-guard.js`.
2. **Module Admin Quản lý người dùng (`T02CEF4`, `T02CF62`):** `/api/admin/users`, `/api/admin/users/{id}/lock`, `admin.html` (Tab Người dùng), `js/admin.js`.
3. **Module Admin Kiểm duyệt tin tuyển dụng (`T02CF2A`, `T02CF62`):** `/api/admin/jobs`, `/api/admin/jobs/{id}/approve`, `/api/admin/jobs/{id}/hide`, `admin.html` (Tab Tin tuyển dụng).

---

## 1. Test Case Backend API

### I. Module Xác thực & Tài khoản (Auth: Register, Login, Me)

| ID | Loại | Tình huống | Kết quả mong đợi |
|---|---|---|---|
| TC_AUTH_01 | **Đúng** | Đăng ký tài khoản Sinh viên hợp lệ (`role: student`, pass >= 8 ký tự) | HTTP 201 Created; trả về user object, `is_locked=False`, không lộ `password`/`hashed_password`. |
| TC_AUTH_02 | **Đúng** | Đăng ký tài khoản Nhà tuyển dụng hợp lệ (`role: employer`) | HTTP 201 Created; user có `role="employer"`. |
| TC_AUTH_03 | **Sai** | Đăng ký với email đã tồn tại trong hệ thống | HTTP 409 Conflict; báo lỗi "Email đã được sử dụng". |
| TC_AUTH_04 | **Sai** | Đăng ký với chuỗi không phải email (`"sinhvien-khong-phai-email"`) | HTTP 422 Unprocessable Entity; pydantic validation từ chối. |
| TC_AUTH_05 | **Sai** | Gửi request cố tình gán quyền quản trị (`role: admin`) | HTTP 422; chỉ chấp nhận giá trị `student` hoặc `employer`. |
| TC_AUTH_06 | **Biên** | Mật khẩu đúng 8 ký tự (Cận dưới: `"12345678"`) | HTTP 201 Created; đăng ký thành công. |
| TC_AUTH_07 | **Biên** | Mật khẩu 7 ký tự (Dưới cận dưới: `"1234567"`) | HTTP 422; báo lỗi mật khẩu tối thiểu 8 ký tự. |
| TC_AUTH_08 | **Biên** | Mật khẩu đúng 64 ký tự (Cận trên) | HTTP 201 Created; đăng ký thành công. |
| TC_AUTH_09 | **Biên** | Mật khẩu 65 ký tự (Vượt cận trên) | HTTP 422; báo lỗi mật khẩu tối đa 64 ký tự. |
| TC_AUTH_10 | **Đúng** | Đăng nhập với email và mật khẩu chính xác | HTTP 200 OK; trả về `access_token` JWT và `token_type: "bearer"`. |
| TC_AUTH_11 | **Sai** | Đăng nhập với mật khẩu không đúng | HTTP 401 Unauthorized; báo "Email hoặc mật khẩu không đúng". |
| TC_AUTH_12 | **Sai** | Đăng nhập với email chưa từng đăng ký | HTTP 401 Unauthorized; thông báo bảo mật thống nhất "Email hoặc mật khẩu không đúng". |
| TC_AUTH_13 | **Sai** | Đăng nhập tài khoản đang bị khóa (`is_locked=True`) | HTTP 403 Forbidden; báo rõ ràng "Tài khoản đã bị khoá". |
| TC_AUTH_14 | **Đúng** | Gọi `/api/auth/me` kèm Header `Authorization: Bearer <valid_token>` | HTTP 200 OK; trả về đúng thông tin user đang đăng nhập. |
| TC_AUTH_15 | **Sai** | Gọi `/api/auth/me` không gửi kèm token | HTTP 401 Unauthorized; báo "Chưa đăng nhập hoặc token không hợp lệ". |
| TC_AUTH_16 | **Sai** | Gọi `/api/auth/me` với token giả mạo hoặc đã hết hạn | HTTP 401 Unauthorized; từ chối truy cập. |

---

### II. Module Phân quyền (RBAC) & Quản lý người dùng (Admin Users)

| ID | Loại | Tình huống | Kết quả mong đợi |
|---|---|---|---|
| TC_ADMU_01 | **Đúng** | Admin gọi lấy danh sách người dùng (`GET /api/admin/users`) | HTTP 200 OK; trả về danh sách phân trang `{ total, page, limit, items }`. |
| TC_ADMU_02 | **Sai** | Sinh viên hoặc Nhà tuyển dụng gọi `GET /api/admin/users` | HTTP 403 Forbidden; báo "Bạn không có quyền truy cập". |
| TC_ADMU_03 | **Đúng** | Tìm kiếm người dùng theo từ khóa email và lọc role | HTTP 200 OK; kết quả lọc chính xác theo tiêu chí truyền vào. |
| TC_ADMU_04 | **Biên** | Phân trang với `limit=1` (Cận dưới) | HTTP 200 OK; trả về đúng 1 bản ghi. |
| TC_ADMU_05 | **Biên** | Phân trang với `limit=100` (Cận trên) | HTTP 200 OK; chấp nhận và trả về tối đa 100 bản ghi. |
| TC_ADMU_06 | **Biên** | Phân trang với `limit=101` hoặc `limit=0` | HTTP 422 Unprocessable Entity; từ chối do ngoài khoảng `[1, 100]`. |
| TC_ADMU_07 | **Đúng** | Xem chi tiết người dùng tồn tại (`GET /api/admin/users/{id}`) | HTTP 200 OK; trả về đầy đủ thông tin tài khoản và profile liên kết. |
| TC_ADMU_08 | **Sai** | Xem chi tiết người dùng không tồn tại (`id=99999`) | HTTP 404 Not Found; báo "Không tìm thấy người dùng". |
| TC_ADMU_09 | **Đúng** | Admin khóa tài khoản vi phạm (`PATCH /api/admin/users/{id}/lock` với `is_locked: true`) | HTTP 200 OK; trạng thái chuyển thành `is_locked=True`, user bị chặn đăng nhập ngay sau đó. |
| TC_ADMU_10 | **Sai/Biên** | Admin cố tình tự khóa tài khoản của chính mình | HTTP 400 Bad Request; báo lỗi "Admin không thể tự khóa tài khoản của chính mình". |
| TC_ADMU_11 | **Đúng** | Admin mở khóa tài khoản đang bị khóa (`is_locked: false`) | HTTP 200 OK; `is_locked=False`, tài khoản khôi phục đăng nhập bình thường. |

---

### III. Module Kiểm duyệt tin tuyển dụng (Admin Jobs)

| ID | Loại | Tình huống | Kết quả mong đợi |
|---|---|---|---|
| TC_ADMJ_01 | **Đúng** | Admin lọc danh sách tin chờ duyệt (`GET /api/admin/jobs?status=DRAFT`) | HTTP 200 OK; chỉ trả về các tin tuyển dụng ở trạng thái `DRAFT`. |
| TC_ADMJ_02 | **Đúng** | Admin duyệt tin tuyển dụng còn hạn (`POST /api/admin/jobs/{id}/approve`) | HTTP 200 OK; tin chuyển sang trạng thái `ACTIVE` và xuất hiện công khai trên sàn việc làm. |
| TC_ADMJ_03 | **Biên/Sai** | Admin bấm duyệt tin có `deadline` đã qua (quá hạn) | HTTP 400 Bad Request; từ chối duyệt và báo "Không thể duyệt tin khi hạn nộp đã qua". |
| TC_ADMJ_04 | **Đúng** | Admin ẩn tin tuyển dụng vi phạm (`POST /api/admin/jobs/{id}/hide`) | HTTP 200 OK; tin chuyển sang `PAUSED`, lập tức biến mất khỏi danh sách việc làm công khai. |
| TC_ADMJ_05 | **Đúng** | Xem chi tiết tin tuyển dụng kèm thông tin công ty | HTTP 200 OK; trả về đầy đủ JD, mức lương, hạn nộp, tên doanh nghiệp và liên hệ. |
| TC_ADMJ_06 | **Sai** | Nhà tuyển dụng gọi API duyệt tin của Admin | HTTP 403 Forbidden; bị chặn do không có quyền quản trị. |

---

## 2. Test Case Frontend UI & Route Guard

| ID | Loại | Tình huống | Kết quả mong đợi |
|---|---|---|---|
| TC_FE_01 | **Đúng** | Nhập form Đăng nhập/Đăng ký hợp lệ và nhấn Submit | Nút submit chuyển sang trạng thái Loading (vô hiệu hóa tạm thời để tránh click đúp), chuyển trang mượt mà. |
| TC_FE_02 | **Sai** | Nhập sai định dạng email hoặc mật khẩu < 8 ký tự trên form | Giao diện hiển thị cảnh báo đỏ ngay dưới ô nhập liệu hoặc qua Toast notification; không gửi request rác lên server. |
| TC_FE_03 | **Đúng** | Chưa đăng nhập cố tình mở trực tiếp `admin.html` trong trình duyệt | `auth-guard.js` phát hiện không có token hợp lệ, lập tức điều hướng về `login.html`. |
| TC_FE_04 | **Đúng** | Đăng nhập tài khoản Sinh viên/Doanh nghiệp cố tình mở `admin.html` | `auth-guard.js` kiểm tra vai trò không phải `admin`, chặn truy cập và chuyển về trang phù hợp (`home.html` hoặc `index.html`). |
| TC_FE_05 | **Đúng** | Nhấn nút "Đăng xuất" trên thanh điều hướng Admin | Xóa sạch `token`, `role`, thông tin user trong `localStorage` và chuyển về `login.html`. |
| TC_FE_06 | **Đúng** | Bấm thao tác Khóa/Mở khóa hoặc Duyệt/Ẩn tin trên `admin.html` | Bảng dữ liệu tự động re-render cập nhật trạng thái mới nhất ngay lập tức kèm thông báo thành công (Toast). |