# BÁO CÁO THỰC THI KIỂM THỬ & NHẬT KÝ SỬA LỖI (TEST LOG & BUG REPORT)
**Dự án:** CareerHub - Cổng thông tin việc làm và thực tập cho sinh viên  
**Module kiểm thử:** Dashboard (Sinh viên, Nhà tuyển dụng, Quản trị viên & Việc làm đã lưu)  
**Người thực hiện:** Sinh viên thực tập (OJT)  
**Ngày thực hiện:** 24/11/2026  
**Trạng thái phiên test:** HOÀN THÀNH (100% Passed)  

---

## PHẦN I: THÔNG TIN PHIÊN KIỂM THỬ (TEST EXECUTION SUMMARY)

### 1. Môi trường kiểm thử (Test Environment)
- **Hệ điều hành:** Windows 11 64-bit
- **Trình duyệt kiểm thử:** Google Chrome (v131.0), Microsoft Edge (v131.0)
- **Công nghệ Backend:** Python 3.14.4, FastAPI, SQLAlchemy ORM, Uvicorn Server
- **Cơ sở dữ liệu:** MySQL 8.0 & SQLite in-memory (cho tự động hóa)
- **Công cụ hỗ trợ kiểm thử:** Pytest 9.2.0, HTTPX, Chrome DevTools (Console/Network), Postman

### 2. Thống kê kết quả kiểm thử tổng quan
| Chỉ số | Số lượng | Tỷ lệ (%) |
| :--- | :---: | :---: |
| **Tổng số ca kiểm thử thực thi (Total Test Cases)** | **21** | **100%** |
| Số ca kiểm thử đạt (**PASSED**) | **21** | **100%** |
| Số ca kiểm thử thất bại (**FAILED**) | **0** | **0%** |
| Số lỗi phát hiện trong quá trình phát triển & test | **5** | Đã khắc phục 5/5 (100%) |

---

## PHẦN II: NHẬT KÝ THỰC THI CHI TIẾT (TEST EXECUTION LOG)

| Mã Test Case | Tên chức năng | Phân loại | Kết quả thực tế (Actual Result) | Đánh giá | Thời gian chạy |
| :--- | :--- | :---: | :--- | :---: | :---: |
| **TC_STU_01** | Xem Dashboard Sinh viên có dữ liệu | Đúng | API trả về mã 200, hiển thị đúng số đơn đã nộp và số tin đã lưu trên giao diện. | **PASSED** | 24/11 14:15 |
| **TC_STU_02** | Xem Dashboard Sinh viên mới tạo (Zero State) | Biên | KPI hiển thị `0`, danh sách hiện thông báo trống, giao diện không lỗi NaN. | **PASSED** | 24/11 14:18 |
| **TC_STU_03** | Khách chưa đăng nhập truy cập Dashboard | Sai | API trả về 401 Unauthorized, frontend tự động điều hướng sang `login.html`. | **PASSED** | 24/11 14:20 |
| **TC_STU_04** | Lưu việc làm hợp lệ (Lần đầu) | Đúng | API trả về 200, `saved_count` tăng 1, icon trái tim chuyển sang màu đỏ. | **PASSED** | 24/11 14:23 |
| **TC_STU_05** | Lưu việc làm đã có trong danh sách (Spam click) | Biên | Không sinh bản ghi trùng lặp trong database, số đếm không đổi. | **PASSED** | 24/11 14:25 |
| **TC_STU_06** | Bỏ lưu việc làm thành công | Đúng | API trả về 200, `saved_count` giảm 1, icon chuyển về trái tim rỗng. | **PASSED** | 24/11 14:28 |
| **TC_STU_07** | Bỏ lưu việc làm không tồn tại (ID sai) | Sai | API trả về 404 Not Found kèm thông báo lỗi rõ ràng. | **PASSED** | 24/11 14:30 |
| **TC_STU_08** | Lấy danh sách việc làm đã lưu (Saved Tab) | Đúng | Render đầy đủ thẻ danh sách công việc đã lưu kèm tên công ty, lương, địa điểm. | **PASSED** | 24/11 14:35 |
| **TC_EMP_01** | Xem Dashboard Doanh nghiệp đầy đủ KPI | Đúng | Hiển thị chính xác thẻ KPI tổng tin, tin active, tổng số ứng viên nộp hồ sơ. | **PASSED** | 24/11 14:40 |
| **TC_EMP_02** | Xem Dashboard Doanh nghiệp mới tạo (Zero State) | Biên | Các chỉ số hiển thị 0, biểu đồ hiển thị trục rỗng, không bị lỗi chia cho 0. | **PASSED** | 24/11 14:42 |
| **TC_EMP_03** | Thống kê ứng viên 7 ngày gần nhất (Biên thời gian) | Biên | Đơn nộp ngày thứ 7 được tính, đơn nộp ngày thứ 8 bị loại khỏi thống kê 7 ngày. | **PASSED** | 24/11 14:45 |
| **TC_EMP_04** | Sinh viên cố tình truy cập Dashboard NTD | Sai | Hệ thống chặn với mã 403 Forbidden, không để lộ dữ liệu ứng viên. | **PASSED** | 24/11 14:48 |
| **TC_EMP_05** | Cách ly dữ liệu giữa 2 Nhà tuyển dụng | Biên | Doanh nghiệp A chỉ thấy tin và ứng viên của A, không thấy dữ liệu của B. | **PASSED** | 24/11 14:52 |
| **TC_EMP_06** | Tính toán tỷ lệ % trạng thái ứng viên | Đúng | Tỷ lệ % cộng lại đúng 100%, thanh tiến độ hiển thị đúng màu trạng thái. | **PASSED** | 24/11 14:55 |
| **TC_ADM_01** | Xem Dashboard Admin tổng quan hệ thống | Đúng | Hiển thị tổng số User, phân loại theo Role, tổng tin tuyển dụng và tổng đơn. | **PASSED** | 24/11 15:00 |
| **TC_ADM_02** | Thống kê biểu đồ tăng trưởng người dùng | Đúng | Trả về dữ liệu mảng các tháng và số lượng user tương ứng để vẽ Chart.js. | **PASSED** | 24/11 15:05 |
| **TC_ADM_03** | Người dùng non-admin cố truy cập Dashboard Admin | Sai | Bị chặn với mã 403 Forbidden, Auth Guard đẩy về trang chủ. | **PASSED** | 24/11 15:08 |
| **TC_ADM_04** | Kiểm tra nhật ký hoạt động gần đây | Biên | Giới hạn hiển thị đúng 10 hoạt động mới nhất, sắp xếp giảm dần theo thời gian. | **PASSED** | 24/11 15:12 |
| **TC_NAV_01** | Nút "Trang chủ" trên Dashboard điều hướng đúng | Đúng | Bấm nút chuyển hướng về `home.html`, không còn lỗi 404 của file `index.html`. | **PASSED** | 24/11 15:15 |
| **TC_NAV_02** | Chuyển đổi tab "Ứng tuyển" và "Đã lưu" | Đúng | Chuyển đổi tab mượt mà, nạp đúng dữ liệu của từng tab, không trắng trang. | **PASSED** | 24/11 15:18 |
| **TC_NAV_03** | Truy cập Dashboard bằng Token giả mạo/hết hạn | Sai | Bị chặn 401 Unauthorized, LocalStorage tự xóa token rác và chuyển về login. | **PASSED** | 24/11 15:22 |

---

## PHẦN III: NHẬT KÝ LỖI ĐÃ PHÁT HIỆN & KHẮC PHỤC (BUG REPORT & FIX LOG)

Trong quá trình phát triển và kiểm thử thực tế Module Dashboard, nhóm đã phát hiện và xử lý triệt để **5 lỗi phần mềm (Bugs)**:

---

### BUG 01: [Frontend] Mục "Đã lưu" trong trang Việc làm của tôi bị trống, chưa có giao diện và kết nối JS
- **Mã lỗi:** `BUG_DASH_01`
- **Mức độ nghiêm trọng:** Major (Lớn - Tính năng chưa hoạt động)
- **Mô tả:** Khi sinh viên vào trang *Việc làm của tôi (`my_applications.html`)* và bấm sang tab "Công việc đã lưu", nội dung bên dưới bị trống trơn, không hiển thị thẻ công việc nào và không có file JavaScript xử lý sự kiện.
- **Nguyên nhân gốc rễ (Root Cause):** Trang frontend chỉ mới dựng tab tĩnh HTML nhưng chưa viết logic gọi API `/api/dashboard/saved-jobs` và chưa có file CSS/JS riêng cho tab Đã lưu.
- **Giải pháp khắc phục (Fix):**
  1. Tạo mới file `frontend/js/saved_tab.js` và `frontend/css/saved_tab.css`.
  2. Viết hàm bất đồng bộ `fetchSavedJobs()` gọi API `GET /api/dashboard/saved-jobs` để lấy danh sách.
  3. Render giao diện các thẻ việc làm tương tự như danh sách ứng tuyển (gồm logo công ty, tiêu đề, mức lương, địa điểm và nút bỏ lưu).
- **Kết quả sau sửa:** Sinh viên bấm tab "Đã lưu" hiển thị đầy đủ danh sách công việc đã đánh dấu yêu thích.

---

### BUG 02: [Navigation] Nút "Trang chủ" trên Dashboard dẫn về `index.html` gây lỗi 404
- **Mã lỗi:** `BUG_DASH_02`
- **Mức độ nghiêm trọng:** Medium (Trung bình - Trải nghiệm người dùng)
- **Mô tả:** Khi đang ở các trang Dashboard (hoặc trang chi tiết), người dùng bấm vào nút "Trang chủ" trên thanh menu điều hướng thì trình duyệt chuyển đến đường dẫn `/index.html`, dẫn đến màn hình lỗi 404 Not Found.
- **Nguyên nhân gốc rễ (Root Cause):** Dự án đã đổi trang chủ chính thức thành `home.html`, nhưng một số liên kết `href` trên header của trang Dashboard vẫn còn giữ đường dẫn cũ `href="index.html"`. Đồng thời backend FastAPI chưa cấu hình chuyển hướng cho route gốc `/`.
- **Giải pháp khắc phục (Fix):**
  1. Thay thế toàn bộ liên kết `href="index.html"` thành `href="home.html"` trên các thanh Navbar.
  2. Tại file `backend/app/main.py`, bổ sung endpoint chuyển hướng:
     ```python
     @app.get("/", include_in_schema=False)
     def root_redirect():
         return RedirectResponse(url="/home.html")
     ```
- **Kết quả sau sửa:** Người dùng bấm vào nút "Trang chủ" hoặc truy cập địa chỉ gốc đều được đưa về trang chủ `home.html` chính xác 100%.

---

### BUG 03: [Backend] API danh sách tin tuyển dụng của tôi thiếu các trường phân trang gây lỗi `ResponseValidationError`
- **Mã lỗi:** `BUG_DASH_03`
- **Mức độ nghiêm trọng:** Critical (Nghiêm trọng - Crash API)
- **Mô tả:** Khi nhà tuyển dụng gọi API lấy danh sách tin `GET /jobs/my-jobs` để hiển thị thống kê tin trên Dashboard, hệ thống ném ra lỗi `fastapi.exceptions.ResponseValidationError: 3 validation errors: missing page, limit, total_pages`.
- **Nguyên nhân gốc rễ (Root Cause):** Schema Pydantic `JobListResponse` định nghĩa bắt buộc phải có đủ 5 trường: `total`, `page`, `limit`, `total_pages`, `items`. Tuy nhiên, trong file `backend/app/services/job_services.py`, hàm `get_my_jobs` chỉ trả về từ điển chứa 2 trường: `{"total": total, "items": items}`.
- **Giải pháp khắc phục (Fix):**
  - Cập nhật lại hàm `get_my_jobs` trong `job_services.py`, bổ sung công thức tính toán trang hiện tại và tổng số trang:
    ```python
    page = (skip // limit) + 1 if limit else 1
    total_pages = ceil(total / limit) if total and limit else 0
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "items": items,
    }
    ```
- **Kết quả sau sửa:** API trả về đầy đủ cấu trúc phân trang chuẩn xác, không còn lỗi validation, hiển thị danh sách tin tuyển dụng mượt mà.

---

### BUG 04: [Frontend/Sync] Không đồng bộ icon trái tim khi người dùng nhấp lưu việc làm liên tục (Spam Click)
- **Mã lỗi:** `BUG_DASH_04`
- **Mức độ nghiêm trọng:** Minor (Nhỏ - Đồng bộ dữ liệu)
- **Mô tả:** Khi sinh viên nhấp nhanh nhiều lần vào nút icon trái tim để lưu/bỏ lưu tin tuyển dụng, giao diện bị giật, icon hiển thị sai trạng thái thực tế trong database và số lượng việc làm đã lưu hiển thị trên thanh Header không cập nhật.
- **Nguyên nhân gốc rễ (Root Cause):** Frontend trước đó chỉ đảo cờ cục bộ `savedJobs[id] = !savedJobs[id]` mà không đợi kết quả phản hồi từ backend, đồng thời backend không trả về tổng số lượng tin đã lưu mới nhất sau khi thao tác.
- **Giải pháp khắc phục (Fix):**
  1. Nâng cấp API `POST /api/dashboard/saved-jobs/{id}` và `DELETE /api/dashboard/saved-jobs/{id}` tính toán và trả về trường `saved_count` mới nhất trong database.
  2. Trong hàm `toggleSave(id)` tại `home.js`, sử dụng khối `try/catch` với `await SavedJobs.save(id)` / `await SavedJobs.unsave(id)`, cập nhật lại số lượng huy hiệu trên Header và vẽ lại icon trái tim chuẩn xác theo phản hồi từ server.
- **Kết quả sau sửa:** Dữ liệu trạng thái lưu tin và số lượng trên Dashboard luôn đồng bộ tuyệt đối với Database.

---

### BUG 05: [Backend] Kiểm tra lỗi ngoại lệ bị `KeyError: 'detail'` do định dạng phản hồi tùy chỉnh `BaseResponse`
- **Mã lỗi:** `BUG_DASH_05`
- **Mức độ nghiêm trọng:** Medium (Trung bình - Ảnh hưởng bộ test)
- **Mô tả:** Khi chạy kiểm thử tự động các trường hợp lỗi (Negative Tests như 401, 403, 404, 409), các bài test bị văng lỗi `KeyError: 'detail'`.
- **Nguyên nhân gốc rễ (Root Cause):** Mặc định FastAPI trả về lỗi dạng `{"detail": "..."}`. Tuy nhiên, dự án CareerHub sử dụng middleware xử lý lỗi tùy chỉnh tại `utils/exceptions.py`, chuẩn hóa toàn bộ phản hồi lỗi về mô hình `BaseResponse` với trường thông báo là `"message"` thay vì `"detail"`.
- **Giải pháp khắc phục (Fix):**
  - Xây dựng hàm helper chuẩn `get_error_message(response)` trong bộ kiểm thử:
    ```python
    def get_error_message(response) -> str:
        try:
            data = response.json()
            if isinstance(data, dict):
                return str(data.get("message") or data.get("detail") or "")
            return str(data)
        except Exception:
            return response.text
    ```
- **Kết quả sau sửa:** Toàn bộ các test case kiểm tra thông báo lỗi đều chạy thành công 100%.

---

## PHẦN IV: KẾT LUẬN & ĐÁNH GIÁ
1. **Chất lượng Module Dashboard:**
   - Hoàn thành đầy đủ các chức năng theo đặc tả kỹ thuật cho cả 3 vai trò (Sinh viên, Doanh nghiệp, Admin).
   - Đảm bảo tính bảo mật, phân quyền nghiêm ngặt và cách ly dữ liệu giữa các doanh nghiệp.
   - Xử lý tốt các trường hợp dữ liệu rỗng (Zero State) và tải giao diện nhanh chóng.
2. **Trạng thái sẵn sàng:**
   - Toàn bộ 5 lỗi phát hiện được đã được khắc phục triệt để và kiểm chứng lại (Verified).
   - Module Dashboard đạt chất lượng cao, hoạt động ổn định và sẵn sàng nghiệm thu bàn giao.
