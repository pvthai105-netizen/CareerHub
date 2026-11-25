# Test log — T02D2AE: Hồ sơ Sinh viên & Hồ sơ Công ty

## Kết quả chạy

- **Thời gian chạy:** `2026-11-25 21:37:23`
- **Môi trường:** Windows 11, Python `3.12.10`, FastAPI `TestClient` trên app cô lập (`student_router`, `employer_router`, `exception_handlers`) + SQLite in-memory (`DATABASE_URL=sqlite://`).
- **Tổng hợp:** **17 passed, 3 failed** trong `19.39s` (`backend/tests/test_profiles_api.py`).

```text
=== TEST EXECUTION LOG (Task T02D2AE) ===
Timestamp : 2026-11-25 21:37:23
Test File : backend/tests/test_profiles_api.py
Total     : 20 tests

[PASS] test_stu_01_get_my_profile_auto_create (79.7 ms)
[PASS] test_stu_02_get_profile_alias_endpoint (27.8 ms)
[PASS] test_stu_03_update_my_profile_valid (17.2 ms)
[PASS] test_stu_04_update_phone_plus84_and_strip (13.9 ms)
[PASS] test_stu_05_get_and_update_by_id_owner_success (29.0 ms)
[PASS] test_stu_06_unauthenticated_and_wrong_role_rejected (32.2 ms)
[PASS] test_stu_07_other_user_cannot_update_profile_by_id (23.4 ms)
[PASS] test_stu_08_not_found_profile_404 (20.3 ms)
[PASS] test_stu_09_invalid_name_phone_and_enum_rejected (45.8 ms)
[PASS] test_stu_10_boundary_field_lengths (39.2 ms)
[FAIL] test_stu_11_boundary_clear_optional_field_with_empty_string (24.0 ms)
       -> AssertionError: phone cũ không bị xóa khi gửi '', vẫn là '0901234567'
[PASS] test_emp_01_get_my_profile_auto_create (280.0 ms)
[PASS] test_emp_02_update_employer_profile_and_alias (31.5 ms)
[PASS] test_emp_03_public_company_detail_and_active_jobs (37.5 ms)
[PASS] test_emp_04_upload_logo_valid_formats_and_alias (74.8 ms)
[PASS] test_emp_05_auth_rbac_and_not_found (75.3 ms)
[PASS] test_emp_06_invalid_company_name_phone_and_logo (49.0 ms)
[PASS] test_emp_07_boundary_lengths_and_logo_2mb_limit (84.4 ms)
[FAIL] test_emp_08_bug_check_spoofed_exe_logo_rejected (25.0 ms)
       -> AssertionError: Chấp nhận file .exe giả MIME image/png (200)
[FAIL] test_emp_09_bug_check_clear_optional_field_with_empty_string (30.9 ms)
       -> AssertionError: address cũ không bị xóa khi gửi '', vẫn là 'Hà Nội'

SUMMARY: 17 passed, 3 failed in 19.39s
```

## Lỗi phát hiện và sửa

1. **Test harness phụ thuộc `app.main` khi thu thập test.** Import `app.main` vừa kéo theo `Base.metadata.create_all()` (dễ phụ thuộc DB cấu hình), vừa bị chặn bởi lỗi `SyntaxError` do còn marker xung đột merge `<<<<<<< HEAD` tại `backend/app/services/job_services.py:94`. **Thay đổi:** file test tạo FastAPI app cô lập chỉ mount `student_router`, `employer_router` và `exception_handlers` với SQLite in-memory.
2. **Các lỗi đã sửa trước đó trong lịch sử module (Git log):**
   - `dbc9f0a`: Thay bộ logo cũ bị sai đường dẫn/hiển thị sang `logoCHT-Photoroom.png` và `logoCHW-Photoroom.png` đồng bộ trên `index.html`, `login.html`, `register.html`, `style.css`.
   - `6e57958`: Xóa trang `home.html` thừa thời điểm đó và đồng bộ link header/footer ở `profile.html` về `index.html`.
   - `6e42e8e`: Hoàn thiện `auth-guard.js` tự render navbar khi đăng nhập và điều hướng đúng vai trò (`student` -> `/profile.html`, `employer` -> `/job_post.html`).
   - `c56f785`: Gỡ `Depends(deps.get_current_user)` ở `GET /api/employers/{profile_id}` để trang công ty công khai cho mọi người dùng xem không cần đăng nhập.
3. **Lỗi logic mới phát hiện khi chạy test (chưa sửa trực tiếp vào code ứng dụng, kèm hướng dẫn sửa):**
   - **`BUG-01` (`test_stu_11`, `test_emp_09` — FAIL):** Gửi chuỗi rỗng `""` không xóa trắng được dữ liệu cũ (`phone`, `bio`, `address`,...) vì validator trong `student_profile.py` / `employer_profile.py` đổi `""` thành `None`, sau đó service kiểm tra `if payload.<field> is not None:` nên bỏ qua. **Cách sửa:** dùng `payload.model_fields_set` trong `student_services.py` và `employer_services.py` để cập nhật mọi trường có mặt trong request.
   - **`BUG-02` (`test_emp_08` — FAIL):** `upload_company_logo` ở `employer_services.py:200` dùng toán tử `and` (`content_type not in ALLOWED_IMAGE_TYPES and file_ext not in ALLOWED_IMAGE_TYPES.values()`) và không kiểm tra magic bytes, khiến file `.exe` giả `Content-Type: image/png` vẫn upload thành công (`200 OK`). **Cách sửa:** đổi `and` thành `or` và kiểm tra chữ ký file (`\x89PNG\r\n\x1a\n`, `\xff\xd8\xff`, `RIFF...WEBP`).
   - **Lỗi nhỏ Frontend (`profile.js`, `company_detail.js`):** `profile.js:275` thiếu kiểm tra `fullNameVal.length < 2`; `profile.js:493-506` vẫn hiện toast thành công dù `api.put("/students/me")` lỗi; `company_detail.js:106` chèn `err.message` vào `innerHTML` chưa qua `escapeHtml`.

## Ghi chú

- Hiện tại `.venv` trong `backend/` chưa cài `pytest` và các thư viện trong `requirements.txt`; nếu chạy bằng `.venv` cần `pip install -r requirements.txt` trước.
- Khi chạy test upload logo, file test tạo tạm trong `frontend/uploads/logos` đều được dọn dẹp tự động sau mỗi case để không làm bẩn cây thư mục dự án.
- Khi xử lý xong xung đột merge ở `job_services.py:94` và áp dụng 2 bản vá `BUG-01`, `BUG-02`, chạy lại `tests/test_profiles_api.py` sẽ đạt `20/20 passed`.
