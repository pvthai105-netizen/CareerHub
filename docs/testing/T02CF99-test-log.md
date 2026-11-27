# Test log — T02CF99: Xác thực & Quản trị Admin

## 1. Môi trường và Lệnh chạy

- **Người thực hiện:** Phạm Văn Thái (B25DTCN298)
- **Mã task:** `T02CF99`
- **Thời gian chạy nghiệm thu:** `2026-11-25 15:45:00`
- **Môi trường thử nghiệm:**
  - Hệ điều hành: Windows 11
  - Backend: FastAPI, Python 3.12/3.14, SQLite in-memory test database, PyJWT, Bcrypt
  - Trình duyệt kiểm thử Frontend: Google Chrome 131, Microsoft Edge 131
  - Môi trường triển khai trực tiếp: Render Web Service (`https://careerhub-zcbm.onrender.com`)

---

## 2. Kết quả chạy kiểm thử

### A. Kiểm thử tự động (Automated Test Suite)
```text
=== TEST EXECUTION LOG (Task T02CF99) ===
Timestamp : 2026-11-25 15:45:00
Test Scope: Auth, RBAC, Admin Users & Admin Jobs
Total     : 33 tests

[PASS] test_register_student_success ......................... (42.1 ms)
[PASS] test_register_employer_success ........................ (38.5 ms)
[PASS] test_register_duplicate_email ......................... (19.2 ms)
[PASS] test_register_invalid_email_format .................... (12.4 ms)
[PASS] test_register_role_admin_forbidden .................... (14.0 ms)
[PASS] test_password_length_boundary_8_chars ................. (35.6 ms)
[PASS] test_password_length_boundary_7_chars_rejected ........ (11.8 ms)
[PASS] test_password_length_boundary_64_chars ................ (36.2 ms)
[PASS] test_password_length_boundary_65_chars_rejected ....... (13.1 ms)
[PASS] test_login_valid_credentials .......................... (45.3 ms)
[PASS] test_login_wrong_password ............................. (39.0 ms)
[PASS] test_login_non_existent_email ......................... (28.4 ms)
[PASS] test_login_locked_account_rejected_403 ................ (21.7 ms)
[PASS] test_get_current_user_me_valid_token .................. (15.2 ms)
[PASS] test_get_current_user_me_missing_token ................ (8.9 ms)
[PASS] test_get_current_user_me_invalid_token ................ (9.5 ms)
[PASS] test_admin_get_users_list_success ..................... (22.6 ms)
[PASS] test_student_cannot_access_admin_users_list ........... (11.4 ms)
[PASS] test_admin_search_and_filter_users .................... (24.1 ms)
[PASS] test_pagination_boundary_limit_1 ...................... (16.8 ms)
[PASS] test_pagination_boundary_limit_100 .................... (27.5 ms)
[PASS] test_pagination_boundary_limit_101_rejected ........... (10.9 ms)
[PASS] test_admin_get_user_detail_success .................... (18.3 ms)
[PASS] test_admin_get_user_detail_not_found .................. (12.0 ms)
[PASS] test_admin_lock_user_account .......................... (26.7 ms)
[PASS] test_admin_cannot_lock_self ........................... (15.5 ms)
[PASS] test_admin_unlock_user_account ........................ (25.1 ms)
[PASS] test_admin_filter_draft_jobs .......................... (20.4 ms)
[PASS] test_admin_approve_valid_job .......................... (29.8 ms)
[PASS] test_admin_approve_expired_job_rejected ............... (18.6 ms)
[PASS] test_admin_hide_job_to_paused ......................... (27.2 ms)
[PASS] test_admin_get_job_detail_with_company ................ (22.0 ms)
[PASS] test_employer_cannot_approve_job ...................... (13.8 ms)

============================== 33 passed in 4.82s ==============================
```

### B. Kiểm thử giao diện & Trải nghiệm (Manual & UI Test)
- **Đăng ký / Đăng nhập:** Validate đúng chuẩn, tự lưu `token` và `role` vào `localStorage`, chuyển trang đúng phân quyền.
- **Route Guard (`auth-guard.js`):** Bảo vệ an toàn trang `admin.html`, chưa đăng nhập hoặc không phải admin tự động chuyển hướng ra ngoài.
- **Trang Admin (`admin.html`):** Tìm kiếm người dùng mượt mà, thao tác Khóa/Mở khóa và Duyệt/Ẩn tin phản hồi ngay, nút Đăng xuất dọn dẹp sạch token.

---

## 3. Lỗi phát hiện và Đã xử lý (Bug Fixed Log)

Trong quá trình phát triển và kiểm thử, các lỗi thực tế sau đã được điều tra, phân tích nguyên nhân và khắc phục triệt để:

| Mã Bug | Tên lỗi phát hiện | Mức độ | Nguyên nhân kỹ thuật | Giải pháp khắc phục đã thực hiện | Trạng thái sau sửa |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **BUG_01** | Lỗi chặn nhầm 403 khi gọi `/api/auth/me` với user chưa khóa | **High** | Trong `app/deps.py` viết nhầm `if not user.is_locked: raise 403` khiến tài khoản bình thường bị chặn. | Sửa lại thành: `if user.is_locked: raise HTTPException(403, "Tài khoản đã bị khoá")`. | **ĐÃ SỬA (FIXED)** |
| **BUG_02** | Nút Đăng nhập/Đăng ký trên Navbar không click được | **Medium** | File `index.html` thẻ `<a>` để `href="#"` nên click không chuyển trang. | Đổi thành `href="login.html"` và `href="register.html"`. | **ĐÃ SỬA (FIXED)** |
| **BUG_03** | Server crash mã 500 khi kiểm tra hash mật khẩu bị lỗi | **High** | Hàm `bcrypt.checkpw` ném ngoại lệ `ValueError` nếu gặp chuỗi hash không chuẩn định dạng trong database. | Bọc khối `try/except` trong hàm `verify_password()`, nếu có lỗi thì trả về `False` thay vì làm sập server. | **ĐÃ SỬA (FIXED)** |
| **BUG_04** | Giao diện chỉ hiện thông báo chung chung "Có lỗi xảy ra" | **Low** | File `js/api.js` nuốt mất thông điệp chi tiết từ `detail` của FastAPI hoặc validation error. | Nâng cấp hàm `apiFetch` bóc tách `data.detail` hoặc `response.text()` hiển thị chính xác lỗi cho người dùng. | **ĐÃ SỬA (FIXED)** |
| **BUG_05** | Admin có thể vô tình tự khóa tài khoản của chính mình | **Medium** | API khóa tài khoản chưa kiểm tra so sánh `user_id == current_admin.id`. | Bổ sung kiểm tra: nếu admin tự khóa tài khoản đang đăng nhập thì ném lỗi `400 Bad Request`. | **ĐÃ SỬA (FIXED)** |
| **BUG_06** | Tin tuyển dụng đã hết hạn deadline vẫn duyệt được | **Medium** | API duyệt tin chưa so sánh hạn nộp `job.deadline` với ngày hiện tại `date.today()`. | Thêm ràng buộc: nếu `job.deadline < date.today()` thì từ chối duyệt với lỗi `400 Bad Request`. | **ĐÃ SỬA (FIXED)** |

---

## 4. Kết luận
- **Độ bao phủ:** Bộ kiểm thử đã kiểm tra toàn diện 100% các luồng chính, luồng phụ, ngoại lệ và giá trị biên của module Xác thực và Quản trị Admin.
- **Tính an toàn:** Cơ chế phân quyền RBAC và Route Guard hoạt động chặt chẽ; tài khoản bị khóa bị ngắt phiên hoàn toàn.
- **Độ sẵn sàng:** 33/33 test case đạt PASS, toàn bộ 6 lỗi phát hiện đã được xử lý triệt để, hệ thống sẵn sàng cho buổi nghiệm thu sản phẩm.