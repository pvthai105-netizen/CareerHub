# Test case — T02D2AE: Hồ sơ Sinh viên & Hồ sơ Công ty

Phạm vi gồm API & giao diện cho 2 module chính do Vũ Nhất Thống phụ trách:
1. **Hồ sơ Sinh viên (`T02D1DA`, `T02D210`):** `/api/students/*` và `frontend/profile.html` (`profile.js`).
2. **Hồ sơ Công ty, Upload Logo & Trang Công ty Công khai (`T02D244`, `T02D27A`):** `/api/employers/*`, `frontend/employer_profile.html` (`employer_profile.js`) và `frontend/company_detail.html` (`company_detail.js`).

## 1. Test Case Backend API

| ID | Loại | Tình huống | Kết quả mong đợi |
|---|---|---|---|
| TC01 | Đúng | Sinh viên gọi `GET /api/students/me` lần đầu khi chưa có hồ sơ | HTTP 200; tự khởi tạo hồ sơ mặc định (`full_name` từ prefix email, `desired_job_type="BOTH"`, kèm `email`). |
| TC02 | Đúng | Sinh viên gọi endpoint alias `GET /api/students/profile` | HTTP 200; trả về đúng hồ sơ của sinh viên đang đăng nhập. |
| TC03 | Đúng | Sinh viên gửi `PUT /api/students/me` với đầy đủ dữ liệu hợp lệ | HTTP 200; cập nhật và trả về đúng các trường đã lưu. |
| TC04 | Đúng | Gửi SĐT đầu `+84` (`" +84912345678 "`) và chuỗi có khoảng trắng thừa | HTTP 200; tự động `strip()` khoảng trắng đầu/cuối và lưu `"+84912345678"`. |
| TC05 | Đúng | Xem hồ sơ sinh viên theo ID (`GET /api/students/{id}`) và chính chủ cập nhật (`PUT /api/students/{id}`) | Cả hai trả về HTTP 200; chỉ chính chủ lưu thành công. |
| TC06 | Sai | Chưa đăng nhập hoặc dùng tài khoản `employer`/`admin` gọi `/api/students/me` | Chưa đăng nhập trả HTTP 401; sai vai trò trả HTTP 403. |
| TC07 | Sai | Sinh viên khác hoặc `employer` gọi `PUT /api/students/{id}` của người khác | Bị từ chối HTTP 403 ("chỉ chủ hồ sơ mới được sửa"). |
| TC08 | Sai | Gọi `GET` hoặc `PUT /api/students/999999` không tồn tại | Trả về HTTP 404. |
| TC09 | Sai | Gửi `full_name` rỗng/`"   "`, SĐT sai định dạng (9 số, 11 số, chứa chữ, sai đầu số), hoặc `desired_job_type="FULL_TIME"` | API từ chối tất cả với HTTP 422. |
| TC10 | Biên | Kiểm tra max_length (`full_name=100`, `university=150`, `major=100`, `avatar_url=255`) và vượt biên `+1` | Đúng biên trả HTTP 200; vượt `+1` ký tự trả HTTP 422. |
| TC11 | Biên | Sinh viên gửi `phone=""`, `bio=""` để xóa trắng trường tùy chọn đã lưu trước đó | HTTP 200; `phone` và `bio` phải về `null`. |
| TC12 | Đúng | Employer mới gọi `GET /api/employers/me` lần đầu | HTTP 200; tự tạo hồ sơ mặc định `"Công ty của <prefix>"`, `is_verified=False`. |
| TC13 | Đúng | Employer gửi `PUT /api/employers/me` hợp lệ và kiểm tra lại qua `GET /api/employers/profile` | HTTP 200; dữ liệu công ty được cập nhật đồng bộ. |
| TC14 | Đúng / Biên | Khách vãng lai (không token) gọi `GET /api/employers/{id}` và `GET /api/employers/{id}/jobs` | HTTP 200; trả về tin `ACTIVE` còn hạn (bao gồm `deadline == hôm nay`), loại tin `DRAFT` và tin quá hạn. |
| TC15 | Đúng | Employer upload logo hợp lệ (`.png`, `.jpg`, `.webp`) qua `/api/employers/logo` và `/api/employers/me/logo` | HTTP 200; lưu file và cập nhật `logo_url` dạng `/uploads/logos/logo_...`. |
| TC16 | Sai | Chưa đăng nhập (401), `student`/`admin` (403) gọi API quản lý công ty; xem ID `999999` | Chặn đúng HTTP 401/403; ID không tồn tại trả HTTP 404. |
| TC17 | Sai | Gửi `company_name` rỗng/khoảng trắng, SĐT công ty sai, upload `.txt` hoặc ảnh `0 bytes` | Validation từ chối HTTP 422; upload sai loại hoặc file rỗng trả HTTP 400. |
| TC18 | Biên | Độ dài tối đa trường công ty (`company_name=200/201`, `tax_code=50/51`) và dung lượng logo đúng `2MB` vs `2MB + 1 byte` | Đúng biên (`200` ký tự / `2MB`) -> HTTP 200; vượt `+1` (`201` ký tự / `2MB+1B`) -> HTTP 422/400. |
| TC19 | Sai / Biên | Upload file `.exe` giả mạo header `Content-Type: image/png` | Bị từ chối HTTP 400 (không cho lưu file giả mạo ảnh). |
| TC20 | Biên | Employer gửi `address=""`, `phone=""` để xóa trắng trường tùy chọn đã lưu | HTTP 200; `address` và `phone` phải về `null`. |

## 2. Test Case Frontend UI & Validation

| ID | Loại | Tình huống | Kết quả mong đợi |
|---|---|---|---|
| TC21 | Đúng | `profile.html`: nhập họ tên, trường, ngành, SĐT, chọn loại công việc | Cột Live Preview bên trái cập nhật tức thì; nhấn Lưu xong bấm F5 vẫn giữ dữ liệu trong `localStorage`. |
| TC22 | Đúng / Biên | `profile.html`: thêm tag kỹ năng `"Python"`, thêm lại `"python"` (trùng hoa/thường), nhấn `Backspace` khi ô trống | Thêm 1 tag `"Python"`; không cho trùng; `Backspace` xóa tag cuối cùng. |
| TC23 | Sai / Biên | `profile.html`: để trống họ tên/trường/ngành, nhập SĐT sai hoặc nhập họ tên chỉ `1` ký tự `"A"` | Chặn submit, focus ô lỗi đầu tiên và hiện thông báo lỗi màu đỏ dưới ô nhập (riêng tên 1 ký tự hiện chưa chặn `< 2`). |
| TC24 | Đúng / Biên | `employer_profile.html`: nhập lần lượt từ `0/7` đến `7/7` trường; chọn file ảnh `.pdf` hoặc `> 2MB` | Thanh tiến độ tăng từ `0%` lên `100%`; chọn file sai loại hoặc quá `2MB` bị toast báo lỗi ở client, không gửi API. |
| TC25 | Đúng / Biên | `company_detail.html?id=1`: công ty có việc làm đang mở vs công ty `0` việc làm; hiển thị lương `(null, null)`, `(10tr, 20tr)` | Hiện đúng danh sách job `ACTIVE` hoặc khối empty state; format lương đúng (`Thỏa thuận`, `10 – 20 triệu / tháng`). |

## Cách chạy

Từ thư mục `backend`:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_profiles_api.py -v
```

*(Hoặc nếu chạy trên Python hệ thống đã cài `pytest`: `python -m pytest tests/test_profiles_api.py -v`.)*

Các case API được cài thành test tự động cô lập tại `backend/tests/test_profiles_api.py` (không phụ thuộc `app.main` hay MySQL).
