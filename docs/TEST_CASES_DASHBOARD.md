# TÀI LIỆU THIẾT KẾ TEST CASE - MODULE DASHBOARD
**Dự án:** CareerHub - Cổng thông tin việc làm và thực tập cho sinh viên  
**Module:** Dashboard (Sinh viên, Nhà tuyển dụng, Quản trị viên & Việc làm đã lưu)  
**Người thực hiện:** Sinh viên thực tập (OJT)  
**Ngày lập:** 24/11/2026  
**Phiên bản:** 1.0  

---

## I. TỔNG QUAN PHẠM VI KIỂM THỬ (TEST SCOPE)

Module **Dashboard** cung cấp thông tin thống kê, bảng điều khiển và quản lý hoạt động cho 3 nhóm đối tượng người dùng chính:
1. **Phân hệ 1: Dashboard Sinh viên (`Student Dashboard`) & Lưu việc làm (`Saved Jobs`)**
   - Xem tổng quan KPI (Đơn đã ứng tuyển, việc đã lưu, tin đã xem).
   - Biểu đồ / Tỷ lệ đơn ứng tuyển theo 5 trạng thái (`pending`, `reviewed`, `interview`, `accepted`, `rejected`).
   - Danh sách đơn ứng tuyển gần nhất.
   - Tính năng lưu việc làm (`POST /api/dashboard/saved-jobs/{id}`) và bỏ lưu việc làm (`DELETE /api/dashboard/saved-jobs/{id}`).
2. **Phân hệ 2: Dashboard Nhà tuyển dụng (`Employer Dashboard`)**
   - Thống kê KPI tuyển dụng (Tổng tin, tin đang hoạt động, tổng ứng viên, ứng viên mới 7 ngày).
   - Thống kê số lượt ứng tuyển theo từng tin tuyển dụng (`GROUP BY job_id`).
   - Thống kê số lượt nộp hồ sơ theo từng ngày trong 7 ngày gần nhất (biểu đồ Chart.js).
   - Tỷ lệ % trạng thái hồ sơ ứng viên (thanh tiến độ quy trình tuyển dụng).
   - Danh sách các ứng viên mới nộp gần đây.
3. **Phân hệ 3: Dashboard Quản trị viên (`Admin Dashboard`)**
   - Thống kê tài khoản toàn hệ thống (Tổng User, Sinh viên, Nhà tuyển dụng, Admin).
   - Thống kê tin tuyển dụng toàn hệ thống (Tổng tin, Active, Closed, Draft, Paused).
   - Biểu đồ tin tuyển dụng mới 7 ngày và biểu đồ tăng trưởng người dùng theo tháng.
   - Danh sách hoạt động gần nhất của toàn bộ hệ thống.
4. **Phân hệ 4: Bảo mật & Phân quyền (`RBAC & Data Isolation`)**
   - Chặn người dùng chưa đăng nhập.
   - Chặn người dùng sai vai trò truy cập chéo dashboard của nhau.
   - Cách ly dữ liệu độc lập giữa các doanh nghiệp.

---

## II. MA TRẬN TEST CASE CHI TIẾT (ĐÚNG - SAI - BIÊN)

### 1. Phân hệ Dashboard Sinh viên & Lưu việc làm (Student Dashboard)

| Mã Test Case | Tên chức năng | Loại kịch bản | Tiền điều kiện | Các bước thực hiện (Steps) | Dữ liệu đầu vào (Input) | Kết quả kỳ vọng (Expected Result) |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- |
| **TC_STU_01** | Xem Dashboard Sinh viên có dữ liệu | **Đúng** | Sinh viên đã nộp 2 đơn, lưu 3 tin, đã login | 1. Mở trang Sinh viên Dashboard<br>2. Gửi request `GET /api/dashboard/student` | Token Bearer của sinh viên | HTTP 200 OK. Hiển thị đúng `applied_count: 2`, `saved_count: 3`. Bảng trạng thái hiển thị đúng số đơn `pending`. |
| **TC_STU_02** | Xem Dashboard Sinh viên mới tạo (Zero State) | **Biên** | Tài khoản sinh viên mới tinh, chưa từng nộp đơn hay lưu tin | 1. Đăng nhập tài khoản mới<br>2. Xem Dashboard | Token Bearer mới | HTTP 200 OK. Tất cả KPI hiển thị `0`. Danh sách đơn trống, hiển thị thông báo *"Chưa có đơn ứng tuyển nào"*, giao diện không bị lỗi NaN. |
| **TC_STU_03** | Khách chưa đăng nhập truy cập Dashboard | **Sai** | Chưa đăng nhập (không có token) | 1. Gọi trực tiếp `GET /api/dashboard/student`<br>2. Không gửi header Authorization | Không có header Authorization | HTTP 401 Unauthorized. Giao diện frontend tự động chuyển hướng về `login.html`. |
| **TC_STU_04** | Lưu việc làm hợp lệ (Lần đầu) | **Đúng** | Đã login vai trò Sinh viên, tin tuyển dụng ID 1 đang ACTIVE | 1. Tại trang chi tiết tin ID 1, bấm icon "Lưu việc làm"<br>2. Gọi `POST /api/dashboard/saved-jobs/1` | `job_id = 1` | HTTP 200 OK. `success: true`, `saved_count` tăng thêm 1. Icon trái tim chuyển sang màu đỏ (Đã lưu). |
| **TC_STU_05** | Lưu việc làm đã có trong danh sách (Spam click) | **Biên** | Tin tuyển dụng ID 1 đã được lưu trước đó | 1. Nhấp click liên tục vào nút Lưu việc làm<br>2. Gửi request `POST /api/dashboard/saved-jobs/1` lần 2 | `job_id = 1` | HTTP 200 OK. Trả về thông báo *"Công việc đã có trong danh sách lưu"*, không bị sinh 2 bản ghi trùng trong Database, `saved_count` không đổi. |
| **TC_STU_06** | Bỏ lưu việc làm thành công | **Đúng** | Tin ID 1 đang ở trạng thái đã lưu | 1. Bấm lại vào icon trái tim đỏ<br>2. Gọi `DELETE /api/dashboard/saved-jobs/1` | `job_id = 1` | HTTP 200 OK. `success: true`, `saved_count` giảm 1. Icon đổi lại thành trái tim rỗng. |
| **TC_STU_07** | Bỏ lưu việc làm không tồn tại hoặc sai ID | **Sai** | Đã login sinh viên | 1. Gọi `DELETE /api/dashboard/saved-jobs/999999` với ID không tồn tại | `job_id = 999999` | HTTP 404 Not Found. Trả về thông báo *"Không tìm thấy việc làm đã lưu"*. |
| **TC_STU_08** | Lấy danh sách việc làm đã lưu (Saved Tab) | **Đúng** | Đã lưu 2 tin tuyển dụng | 1. Mở trang Việc làm của tôi $\to$ Tab "Đã lưu"<br>2. Gọi `GET /api/dashboard/saved-jobs` | Token Bearer | HTTP 200 OK. Trả về danh sách 2 công việc kèm tên vị trí, công ty, địa điểm, mức lương và ngày lưu. |

---

### 2. Phân hệ Dashboard Nhà tuyển dụng (Employer Dashboard)

| Mã Test Case | Tên chức năng | Loại kịch bản | Tiền điều kiện | Các bước thực hiện (Steps) | Dữ liệu đầu vào (Input) | Kết quả kỳ vọng (Expected Result) |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- |
| **TC_EMP_01** | Xem Dashboard Doanh nghiệp đầy đủ KPI | **Đúng** | NTD đã đăng 3 tin (2 Active, 1 Closed), có 10 ứng viên | 1. Đăng nhập tài khoản NTD<br>2. Gửi `GET /api/dashboard/employer` | Token Bearer của NTD | HTTP 200 OK. `total_jobs: 3`, `active_jobs: 2`, `total_applicants: 10`. Danh sách phân nhóm ứng viên theo từng tin chính xác. |
| **TC_EMP_02** | Xem Dashboard Doanh nghiệp mới tạo (Zero State) | **Biên** | Doanh nghiệp mới đăng ký, chưa đăng tin nào | 1. Đăng nhập doanh nghiệp mới<br>2. Mở Dashboard | Token Bearer mới | HTTP 200 OK. Các thẻ KPI hiển thị `0`. Biểu đồ 7 ngày hiển thị trục 0, thanh tỷ lệ tiến độ không bị lỗi chia cho 0 (`ZeroDivisionError`). |
| **TC_EMP_03** | Thống kê ứng viên 7 ngày gần nhất (Biên thời gian) | **Biên** | Có 1 đơn nộp cách đây đúng 7 ngày, 1 đơn nộp cách đây 8 ngày | 1. Mở Dashboard NTD<br>2. Kiểm tra trường `new_applicants_7d` và biểu đồ | Dữ liệu ứng tuyển có mốc thời gian cụ thể | Đơn nộp cách đây 7 ngày được cộng vào thống kê. Đơn nộp cách 8 ngày KHÔNG được tính vào chỉ số 7 ngày gần nhất. |
| **TC_EMP_04** | Sinh viên cố tình truy cập Dashboard NTD | **Sai** | Đang đăng nhập tài khoản Sinh viên | 1. Gọi `GET /api/dashboard/employer`<br>2. Gửi kèm token của Sinh viên | Token của Student | HTTP 403 Forbidden. Trả về lỗi phân quyền, không để lộ bất kỳ số liệu doanh nghiệp nào. |
| **TC_EMP_05** | Cách ly dữ liệu giữa 2 Nhà tuyển dụng | **Biên** | NTD A có 5 tin, NTD B có 2 tin | 1. Đăng nhập NTD B<br>2. Xem Dashboard NTD B | Token của NTD B | HTTP 200 OK. NTD B chỉ nhìn thấy đúng 2 tin và danh sách ứng viên nộp vào công ty B; tuyệt đối không thấy dữ liệu của công ty A. |
| **TC_EMP_06** | Tính toán tỷ lệ % trạng thái ứng viên | **Đúng** | Có 4 đơn: 2 pending, 1 reviewed, 1 accepted | 1. Xem thanh tiến độ trạng thái tuyển dụng | 4 đơn ứng tuyển | HTTP 200 OK. Tỷ lệ: `pending: 50.0%`, `reviewed: 25.0%`, `accepted: 25.0%`. Tổng cộng tròn 100%. |

---

### 3. Phân hệ Dashboard Quản trị viên (Admin Dashboard)

| Mã Test Case | Tên chức năng | Loại kịch bản | Tiền điều kiện | Các bước thực hiện (Steps) | Dữ liệu đầu vào (Input) | Kết quả kỳ vọng (Expected Result) |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- |
| **TC_ADM_01** | Xem Dashboard Admin tổng quan hệ thống | **Đúng** | Đã đăng nhập tài khoản Admin | 1. Mở trang Admin Dashboard<br>2. Gửi `GET /api/dashboard/admin` | Token Bearer của Admin | HTTP 200 OK. Hiển thị tổng số User, phân loại (Student, Employer, Admin), tổng tin tuyển dụng theo trạng thái và tổng lượt nộp đơn. |
| **TC_ADM_02** | Thống kê biểu đồ tăng trưởng người dùng theo tháng | **Đúng** | Hệ thống hoạt động qua các tháng trong năm | 1. Xem biểu đồ "Tăng trưởng người dùng"<br>2. Kiểm tra trường `user_growth_by_month` | Token Admin | HTTP 200 OK. Dữ liệu trả về danh sách các tháng dạng `YYYY-MM` và số lượng user đăng ký tương ứng tăng dần. |
| **TC_ADM_03** | Người dùng không phải Admin cố truy cập Dashboard Admin | **Sai** | Đang login tài khoản Sinh viên hoặc Nhà tuyển dụng | 1. Gọi `GET /api/dashboard/admin`<br>2. Gửi kèm token của Sinh viên/NTD | Token của Student/Employer | HTTP 403 Forbidden. Thông báo lỗi: *"Bạn không có quyền truy cập"*. Giao diện web chặn hiển thị. |
| **TC_ADM_04** | Kiểm tra nhật ký hoạt động gần đây (Recent Activities) | **Biên** | Hệ thống có hơn 100 hoạt động mới diễn ra | 1. Xem mục "Hoạt động gần đây"<br>2. Kiểm tra số lượng bản ghi trả về | Token Admin | Giới hạn hiển thị đúng Top 5 hoặc Top 10 hoạt động mới nhất, sắp xếp theo thời gian giảm dần, không gây chậm server. |

---

### 4. Phân hệ Phân quyền & Điều hướng Giao diện (Navigation & RBAC)

| Mã Test Case | Tên chức năng | Loại kịch bản | Tiền điều kiện | Các bước thực hiện (Steps) | Dữ liệu đầu vào (Input) | Kết quả kỳ vọng (Expected Result) |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- |
| **TC_NAV_01** | Nút "Trang chủ" trên Dashboard điều hướng đúng | **Đúng** | Đang ở trang bất kỳ của Dashboard | 1. Nhấp chuột vào logo hoặc nút "Trang chủ" trên thanh điều hướng | Click chuột | Trình duyệt chuyển hướng mượt mà về `home.html` (hoặc `/`), không bị trỏ về `index.html` lỗi 404. |
| **TC_NAV_02** | Chuyển đổi qua lại giữa Tab "Ứng tuyển" và Tab "Đã lưu" | **Đúng** | Đang ở trang `my_applications.html` | 1. Nhấp vào tab "Công việc đã lưu"<br>2. Nhấp lại vào tab "Việc làm ứng tuyển" | Click chuyển tab | Dữ liệu chuyển đổi tức thì, kích hoạt đúng file JS tương ứng (`saved_tab.js` và `my_applications.js`), không bị trắng trang. |
| **TC_NAV_03** | Truy cập Dashboard bằng Token hết hạn hoặc Token giả mạo | **Sai** | Giả mạo chuỗi JWT token trong LocalStorage | 1. Gán chuỗi token rác vào LocalStorage<br>2. F5 tải lại trang Dashboard | `access_token = "invalid.token.123"` | HTTP 401 Unauthorized. Hệ thống xóa token rác khỏi LocalStorage và đưa người dùng về trang đăng nhập. |

---

## III. TỔNG KẾT BẢN THIẾT KẾ TEST CASE
- **Tổng số Test Case:** 21 Test Cases.
- **Phân loại kịch bản:**
  - **Trường hợp Đúng (Positive):** 11 Test Cases (52.4%)
  - **Trường hợp Sai (Negative):** 5 Test Cases (23.8%)
  - **Trường hợp Biên (Boundary / Edge):** 5 Test Cases (23.8%)
- **Mức độ bao phủ:** 100% các endpoint API của Dashboard, 100% các vai trò người dùng (Student, Employer, Admin, Guest), và các tương tác giao diện quan trọng.
