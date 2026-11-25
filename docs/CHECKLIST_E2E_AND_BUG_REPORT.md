# BÁO CÁO KIỂM THỬ E2E THỦ CÔNG & NHẬT KÝ SỬA LỖI (BUG FIX REPORT)
**Dự án:** CareerHub - Cổng thông tin việc làm và thực tập cho sinh viên  
**Đơn vị thực hiện:** Nhóm 4 CareerHub  
**Người thực hiện / Phụ trách:** synnd (Sinh viên OJT)  
**Ngày thực hiện:** 25/11/2026  
**Phiên bản:** 2.0 (Cập nhật nhật ký lỗi thực tế của tác giả)  

---

## MỤC LỤC
1. [TỔNG QUAN PHIÊN KIỂM THỬ E2E](#i-tổng-quan-phiên-kiểm-thử-e2e)
2. [CHECKLIST E2E THỦ CÔNG (30 TEST CASES)](#ii-checklist-e2e-thủ-công-30-test-cases)
   - [1. Luồng Người Dùng: Sinh Viên (Student)](#1-luồng-người-dùng-sinh-viên-student---9-ca)
   - [2. Luồng Người Dùng: Nhà Tuyển Dụng (Employer)](#2-luồng-người-dùng-nhà-tuyển-dụng-employer---9-ca)
   - [3. Luồng Người Dùng: Quản Trị Viên (Admin)](#3-luồng-người-dùng-quản-trị-viên-admin---6-ca)
   - [4. Luồng Kiểm Thử: 3 Tính Năng AI](#4-luồng-kiểm-thử-3-tính-năng-ai---6-ca)
3. [BẢNG THEO DÕI VÀ NHẬT KÝ LỖI ĐÃ SỬA (BUG FIX LOG)](#iii-bảng-theo-dõi-và-nhật-ký-lỗi-đã-sửa-bug-fix-log)
4. [KẾT LUẬN & ĐÁNH GIÁ NGHIỆM THU](#iv-kết-luận--đánh-giá-nghiệm-thu)

---

## I. TỔNG QUAN PHIÊN KIỂM THỬ E2E

### 1. Mục tiêu kiểm thử
Kiểm thử toàn trình thủ công (Manual End-to-End Testing) các luồng thao tác thực tế của người dùng từ giao diện Frontend đến hệ thống Backend và Database, bao gồm:
- **3 vai trò người dùng:** Sinh viên (`Student`), Nhà tuyển dụng (`Employer`), Quản trị viên (`Admin`).
- **3 tính năng AI thông minh:**
  1. *Trợ lý AI Chat tư vấn nghề nghiệp & định hướng thực tập* (Gemini AI Chatbot).
  2. *AI Phân tích, nhận xét & Chấm điểm CV* (`CvAnalysis`).
  3. *AI Gợi ý vị trí thực tập & Khớp kỹ năng tự động* (`Job Matching / AI Recommendation`).
- **Ghi nhận & Báo cáo lỗi:** Chỉ tập trung ghi nhận **các lỗi thực tế do chính tác giả (`synnd`) đã phát hiện và trực tiếp xử lý/sửa chữa** trong quá trình xây dựng module và hệ thống, phân loại mức độ nghiêm trọng (**Cao / Trung bình / Thấp**).

### 2. Môi trường kiểm thử (Test Environment)
- **Hệ điều hành:** Windows 11 Pro 64-bit
- **Trình duyệt:** Google Chrome v131.0, Microsoft Edge v131.0
- **Máy chủ Backend:** FastAPI, Uvicorn Server, Python 3.14.4
- **Cơ sở dữ liệu:** MySQL 8.0 & SQLite Local
- **Dịch vụ AI:** Google GenAI SDK (Gemini API 2.5/Flash-Lite)

### 3. Thống kê kết quả kiểm thử
| Phân loại | Tổng số ca | Đạt (PASSED) | Lỗi phát hiện ban đầu | Trạng thái sau khi sửa (Retest) |
| :--- | :---: | :---: | :---: | :---: |
| **Vai trò 1: Sinh viên (Student)** | 9 | 9 | 2 | 100% PASSED |
| **Vai trò 2: Nhà tuyển dụng (Employer)** | 9 | 9 | 1 | 100% PASSED |
| **Vai trò 3: Quản trị viên (Admin)** | 6 | 6 | 0 | 100% PASSED |
| **3 Tính năng AI** | 6 | 6 | 0 | 100% PASSED |
| **TỔNG CỘNG** | **30** | **30** | **5 lỗi thực tế** | **100% PASSED (Đã sửa xong)** |

*(Ghi chú: Đã bao phủ 30 ca kiểm thử, vượt chỉ tiêu tối thiểu $\ge 25$ ca theo yêu cầu).*

---

## II. CHECKLIST E2E THỦ CÔNG (30 TEST CASES)

### 1. Luồng Người Dùng: Sinh Viên (Student) - 9 ca

| Mã TC | Tên kịch bản E2E | Tiền điều kiện | Các bước thực hiện (Steps) | Dữ liệu kiểm thử | Kết quả kỳ vọng (Expected Result) | Kết quả thực tế (Sau khi sửa) | Đánh giá | Bug liên quan |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **TC_STU_01** | Đăng ký tài khoản Sinh viên mới | Chưa có tài khoản | 1. Mở `register.html`<br>2. Nhập email, mật khẩu<br>3. Chọn vai trò "Sinh viên"<br>4. Bấm "Đăng ký" | Email: `sv_e2e_01@gmail.com`<br>Pass: `Password123@` | Thông báo đăng ký thành công, tự động chuyển về trang đăng nhập. | Đăng ký thành công, chuyển hướng trang mượt mà. | **PASSED** | - |
| **TC_STU_02** | Đăng nhập tài khoản Sinh viên | Đã có tài khoản sinh viên | 1. Mở `login.html`<br>2. Nhập email & pass<br>3. Bấm "Đăng nhập" | `sv_e2e_01@gmail.com`<br>`Password123@` | Đăng nhập thành công, lưu JWT Token vào LocalStorage, điều hướng về `home.html`. | Header đổi thành avatar sinh viên, lưu token đúng. | **PASSED** | - |
| **TC_STU_03** | Tìm kiếm và lọc việc làm | Đang ở trang chủ `home.html` | 1. Nhập từ khóa tìm kiếm<br>2. Chọn địa điểm "Hà Nội"<br>3. Chọn hình thức "Thực tập" | Keyword: "Python"<br>Location: "Hà Nội"<br>Type: "Thực tập" | Danh sách việc làm lọc theo đúng tiêu chí, hiển thị số lượng kết quả phù hợp. | Lọc dữ liệu chuẩn xác, phân trang cập nhật đúng. | **PASSED** | - |
| **TC_STU_04** | Xem chi tiết công việc | Danh sách việc làm hiển thị | 1. Bấm vào một tin tuyển dụng cụ thể | ID tin tuyển dụng | Mở khung chi tiết công việc hiển thị đầy đủ: tên cty, mức lương, hạn nộp, mô tả, yêu cầu. | Chi tiết tải đầy đủ, nút ứng tuyển hiển thị rõ. | **PASSED** | - |
| **TC_STU_05** | Lưu việc làm yêu thích (Click liên tục) | Đã đăng nhập Sinh viên | 1. Bấm icon trái tim để Lưu<br>2. Thử nhấp nhanh liên tục<br>3. Kiểm tra số lượng | Tin ID 1 | Tim đổi màu đỏ, số lượng lưu trên header tăng đúng 1, không bị lỗi duplicate hay sai số lượng. | Hoạt động đồng bộ giữa DB và giao diện nhờ API trả về `saved_count`. | **PASSED** | `BUG_DASH_04` |
| **TC_STU_06** | Xem danh sách việc làm đã lưu (Tab Đã lưu) | Đã lưu ít nhất 1 tin | 1. Mở trang `my_applications.html`<br>2. Nhấp sang tab "Công việc đã lưu" | Tab "Công việc đã lưu" | Hiển thị đầy đủ danh sách các thẻ việc làm đã lưu kèm logo, mức lương, nút bỏ lưu. | Giao diện hiển thị chuẩn xác, nạp đúng API `/api/dashboard/saved-jobs`. | **PASSED** | `BUG_DASH_01` |
| **TC_STU_07** | Nộp hồ sơ ứng tuyển kèm CV PDF | Đã đăng nhập Sinh viên | 1. Bấm "Ứng tuyển ngay"<br>2. Chọn file CV PDF (<5MB)<br>3. Nhập lời giới thiệu<br>4. Bấm "Gửi hồ sơ" | File: `CV_NguyenVanA.pdf`<br>Letter: "Em mong muốn ứng tuyển" | Thông báo nộp hồ sơ thành công, trạng thái chuyển sang `Pending`. | Nộp đơn thành công, file lưu an toàn trên server. | **PASSED** | - |
| **TC_STU_08** | Chặn nộp file CV sai định dạng (.exe) | Đang mở modal ứng tuyển | 1. Chọn file đuôi `.exe` hoặc `.txt`<br>2. Bấm "Gửi hồ sơ" | File: `virus.exe` | Hệ thống báo lỗi: "CV phải có định dạng PDF hoặc DOCX", không cho phép gửi. | Báo lỗi đúng, không cho tải file lạ lên server. | **PASSED** | - |
| **TC_STU_09** | Xem danh sách đơn và Rút đơn đang chờ | Đã có 1 đơn ở trạng thái `Pending` | 1. Vào `my_applications.html`<br>2. Xem danh sách đơn<br>3. Bấm "Rút đơn" | Đơn ứng tuyển đang chờ | Đơn được hủy thành công, trạng thái chuyển sang `Withdrawn`. | Rút đơn thành công, cập nhật giao diện ngay lập tức. | **PASSED** | - |

---

### 2. Luồng Người Dùng: Nhà Tuyển Dụng (Employer) - 9 ca

| Mã TC | Tên kịch bản E2E | Tiền điều kiện | Các bước thực hiện (Steps) | Dữ liệu kiểm thử | Kết quả kỳ vọng (Expected Result) | Kết quả thực tế (Sau khi sửa) | Đánh giá | Bug liên quan |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **TC_EMP_01** | Đăng ký & Đăng nhập Nhà tuyển dụng | Chưa có tài khoản | 1. Mở `register.html`<br>2. Chọn vai trò "Nhà tuyển dụng"<br>3. Đăng nhập tại `login.html` | Email: `hr_techcorp@gmail.com`<br>Pass: `Password123@` | Đăng nhập thành công, điều hướng vào `employer_dashboard.html`. | Điều hướng đúng dashboard nhà tuyển dụng. | **PASSED** | - |
| **TC_EMP_02** | Cập nhật hồ sơ công ty & Upload logo | Đã login Nhà tuyển dụng | 1. Mở `employer_profile.html`<br>2. Nhập tên cty, địa chỉ, website<br>3. Chọn ảnh logo PNG (<2MB)<br>4. Bấm "Lưu thay đổi" | Cty: "TechCorp"<br>Logo: `logo.png` (500KB) | Cập nhật thành công, logo hiển thị trên thanh Header và trang hồ sơ. | Lưu hồ sơ và hiển thị logo công ty thành công. | **PASSED** | - |
| **TC_EMP_03** | Chặn upload logo vượt quá dung lượng 2MB | Đang ở trang hồ sơ công ty | 1. Chọn file ảnh kích thước 4.5MB<br>2. Bấm upload | File ảnh: `banner_large.png` (4.5MB) | Hệ thống chặn và báo lỗi: "Dung lượng ảnh vượt quá giới hạn tối đa 2.0MB". | Báo lỗi chính xác, không lưu ảnh quá lớn. | **PASSED** | - |
| **TC_EMP_04** | Đăng tin tuyển dụng mới thành công | Đã hoàn thiện hồ sơ cty | 1. Mở `job_post.html`<br>2. Điền tiêu đề, mô tả, mức lương, hạn nộp<br>3. Bấm "Đăng tin" | Tiêu đề: "Thực tập sinh Python"<br>Lương: 5tr - 10tr<br>Hạn: 30 ngày tới | Tạo tin thành công, tin xuất hiện trong danh sách quản lý với trạng thái DRAFT/ACTIVE. | Đăng tin thành công, dữ liệu lưu vào DB chuẩn. | **PASSED** | - |
| **TC_EMP_05** | Chặn đăng tin khi mức lương Min > Max | Đang ở form đăng tin | 1. Nhập Lương Min: 15.000.000<br>2. Nhập Lương Max: 8.000.000<br>3. Bấm "Đăng tin" | Min: 15tr<br>Max: 8tr | Báo lỗi xác thực: "Mức lương tối thiểu không được lớn hơn mức lương tối đa". | Hệ thống chặn lưu và hiển thị thông báo lỗi. | **PASSED** | - |
| **TC_EMP_06** | Xem danh sách tin của mình (My Jobs) | Đã đăng 3 tin tuyển dụng | 1. Vào danh sách tin tuyển dụng của tôi<br>2. Kiểm tra thông tin phân trang | API: `/jobs/my-jobs` | Trả về đủ 5 trường phân trang (`total`, `page`, `limit`, `total_pages`, `items`), hiển thị mượt mà. | Không còn lỗi validation phân trang, hiển thị đầy đủ tin. | **PASSED** | `BUG_DASH_03` |
| **TC_EMP_07** | Chỉnh sửa thông tin tin tuyển dụng | Đã có tin tuyển dụng | 1. Bấm nút "Sửa" trên 1 tin<br>2. Đổi tiêu đề và mức lương<br>3. Bấm "Cập nhật" | Tiêu đề mới: "Senior Python"<br>Lương mới: 20tr - 30tr | Cập nhật thành công, thông tin mới hiển thị ngay trên bảng. | Tin được cập nhật mượt mà. | **PASSED** | - |
| **TC_EMP_08** | Xem danh sách ứng viên và hồ sơ CV | Có sinh viên nộp đơn vào tin | 1. Vào `employer_applications.html`<br>2. Bấm xem chi tiết đơn<br>3. Bấm tải/xem file CV | Đơn ứng tuyển của sinh viên | Hiển thị thông tin sinh viên, thư giới thiệu và mở được file CV để xem. | File CV tải về được, thông tin ứng viên rõ ràng. | **PASSED** | - |
| **TC_EMP_09** | Điều hướng nút "Trang chủ" từ Dashboard | Đang ở Employer Dashboard | 1. Bấm nút "Trang chủ" trên menu | Click chuột | Chuyển hướng chính xác về `home.html`, không bị lỗi 404 trang `index.html`. | Điều hướng mượt mà, đúng trang chủ mới. | **PASSED** | `BUG_DASH_02` |

---

### 3. Luồng Người Dùng: Quản Trị Viên (Admin) - 6 ca

| Mã TC | Tên kịch bản E2E | Tiền điều kiện | Các bước thực hiện (Steps) | Dữ liệu kiểm thử | Kết quả kỳ vọng (Expected Result) | Kết quả thực tế (Sau khi sửa) | Đánh giá | Bug liên quan |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **TC_ADM_01** | Đăng nhập Quản trị viên (Admin) | Tài khoản có vai trò `admin` | 1. Đăng nhập tại `login.html`<br>2. Nhập thông tin tài khoản admin | `admin@careerhub.vn`<br>`AdminSecret123@` | Đăng nhập thành công, tự động chuyển hướng vào `admin_dashboard.html`. | Vào đúng trang quản trị admin, hiển thị đầy đủ menu. | **PASSED** | - |
| **TC_ADM_02** | Xem thống kê tổng quan hệ thống (KPI) | Đã vào Admin Dashboard | 1. Quan sát các thẻ thống kê tổng quan trên màn hình | - | Hiển thị chính xác tổng số User, phân loại theo Role, tổng tin đăng và tổng đơn. | Số liệu KPI thống kê chính xác từ Database. | **PASSED** | - |
| **TC_ADM_03** | Tìm kiếm và Lọc danh sách người dùng | Ở tab Quản lý người dùng | 1. Nhập email cần tìm<br>2. Lọc theo vai trò (Sinh viên/NTD)<br>3. Lọc theo trạng thái Khóa | Search: "sv_e2e"<br>Role: "student" | Bảng người dùng lọc đúng các tài khoản thỏa mãn điều kiện. | Tìm kiếm và phân trang hoạt động nhanh chóng. | **PASSED** | - |
| **TC_ADM_04** | Khóa tài khoản vi phạm (Lock Account) | Chọn 1 tài khoản đang hoạt động | 1. Bấm nút "Khóa tài khoản" tại dòng user<br>2. Xác nhận hộp thoại | User ID: 5 | Trạng thái tài khoản chuyển thành "Đã khóa" (`is_locked: true`). | Tài khoản bị khóa lập tức trên hệ thống. | **PASSED** | - |
| **TC_ADM_05** | Kiểm tra tài khoản bị khóa không thể đăng nhập | Tài khoản vừa bị Admin khóa | 1. Dùng tài khoản bị khóa đăng nhập tại `login.html` | Email tài khoản bị khóa | Đăng nhập thất bại, hệ thống báo lỗi 403: "Tài khoản đã bị khoá". | Bị chặn đăng nhập chính xác, bảo vệ hệ thống. | **PASSED** | - |
| **TC_ADM_06** | Mở khóa tài khoản (Unlock Account) | Tài khoản đang ở trạng thái Khóa | 1. Admin bấm "Mở khóa"<br>2. User thử đăng nhập lại | User ID: 5 | Tài khoản chuyển về trạng thái hoạt động, đăng nhập lại thành công. | Mở khóa thành công, đăng nhập bình thường. | **PASSED** | - |

---

### 4. Luồng Kiểm Thử: 3 Tính Năng AI - 6 ca

| Mã TC | Tên kịch bản E2E | Tiền điều kiện | Các bước thực hiện (Steps) | Dữ liệu kiểm thử | Kết quả kỳ vọng (Expected Result) | Kết quả thực tế (Sau khi sửa) | Đánh giá | Bug liên quan |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **TC_AI_01** | **[AI 1]** Gửi câu hỏi tư vấn viết CV cho Trợ lý AI | Đã đăng nhập Sinh viên, mở `chat.html` | 1. Nhập câu hỏi: "Làm thế nào để viết CV cho người chưa có kinh nghiệm?"<br>2. Bấm "Gửi" | Câu hỏi về CV sinh viên | Trợ lý AI phân tích và phản hồi lời khuyên mạch lạc, có cấu trúc bullet point rõ ràng. | AI phản hồi chuẩn xác, nhanh chóng trong ~2-3 giây. | **PASSED** | - |
| **TC_AI_02** | **[AI 1]** Sử dụng các Prompt gợi ý sẵn (Preset Prompts) | Đang ở giao diện `chat.html` | 1. Bấm vào nút gợi ý: "Chuẩn bị cho buổi phỏng vấn"<br>2. Xem câu trả lời tự động | Click prompt button | Câu hỏi tự điền vào khung chat, AI gửi lại câu trả lời hướng dẫn phương pháp STAR. | Prompt hoạt động mượt mà, phản hồi đúng trọng tâm. | **PASSED** | - |
| **TC_AI_03** | **[AI 1]** Lưu và Tải lại lịch sử trò chuyện AI | Đã thực hiện vài lượt chat với AI | 1. Thoát khỏi trang chat<br>2. Quay lại mở lại trang `chat.html` | Lịch sử chat cũ | Đoạn hội thoại cũ được tự động tải lại từ API `/api/chat/history`, tin nhắn hiển thị đúng thứ tự. | Tin nhắn tải lại đúng, lịch sử lưu chuẩn trong DB. | **PASSED** | - |
| **TC_AI_04** | **[AI 2]** AI Phân tích & Chấm điểm CV tải lên | Sinh viên có file CV PDF | 1. Vào tính năng Đánh giá CV<br>2. Upload file CV<br>3. Bấm "Phân tích CV bằng AI" | File: `CV_Backend_Intern.pdf` | AI trả về: Điểm số tổng quan (thang điểm 10/100), Nhận xét điểm mạnh, Điểm yếu và Lời khuyên cải thiện. | AI trích xuất nội dung, chấm điểm và góp ý chi tiết. | **PASSED** | - |
| **TC_AI_05** | **[AI 2]** Chặn phân tích file CV rỗng hoặc hỏng | Đang ở form upload CV AI | 1. Upload file dung lượng 0 bytes<br>2. Bấm phân tích | File: `empty_cv.pdf` (0KB) | Hệ thống báo lỗi: "File tải lên không có nội dung hợp lệ", không gửi request tới Gemini API. | Báo lỗi chính xác, tiết kiệm chi phí gọi API. | **PASSED** | - |
| **TC_AI_06** | **[AI 3]** AI Gợi ý việc làm phù hợp theo kỹ năng (Job Matcher) | Sinh viên đã điền kỹ năng trong hồ sơ | 1. Nhập câu lệnh: "Gợi ý cho em công việc phù hợp với kỹ năng Python, FastAPI, MySQL"<br>2. Xem kết quả | Prompt kỹ năng lập trình | AI đọc danh sách việc làm trên hệ thống và gợi ý 2-3 vị trí thực tập phù hợp nhất kèm link ứng tuyển. | AI đưa ra gợi ý sát với kỹ năng lập trình của sinh viên. | **PASSED** | - |

---

## III. BẢNG THEO DÕI VÀ NHẬT KÝ LỖI ĐÃ SỬA (BUG FIX LOG)

Danh sách toàn bộ các lỗi phần mềm thực tế do chính **`synnd`** đã trực tiếp phát hiện, phân tích nguyên nhân gốc rễ và tiến hành viết mã sửa chữa (fix) thành công trên hệ thống CareerHub:

| Mã Bug | Tên lỗi phát hiện | Module / Vị trí | Mức độ nghiêm trọng | Người phụ trách | Trạng thái |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **BUG_DASH_01** | Mục "Đã lưu" trong trang Việc làm của tôi bị trống, chưa có giao diện và kết nối JS | Frontend (`my_applications.html`) | **Trung bình (TB)** | `synnd` | **Đã sửa (Resolved)** |
| **BUG_DASH_02** | Nút "Trang chủ" trên Navbar Dashboard dẫn về `index.html` gây lỗi 404 | Điều hướng / Navigation | **Trung bình (TB)** | `synnd` | **Đã sửa (Resolved)** |
| **BUG_DASH_03** | API danh sách tin của tôi `get_my_jobs` thiếu phân trang gây lỗi `ResponseValidationError` | Backend (`job_services.py`) | **Cao (High)** | `synnd` | **Đã sửa (Resolved)** |
| **BUG_DASH_04** | Không đồng bộ icon trái tim và số lượng việc làm đã lưu khi click liên tục (Spam Click) | Frontend / Sync (`home.js`) | **Trung bình (TB)** | `synnd` | **Đã sửa (Resolved)** |
| **BUG_DASH_05** | Lỗi kiểm tra thông báo lỗi bị `KeyError: 'detail'` do định dạng `BaseResponse` (`message`) | Backend Testing (`conftest.py`) | **Trung bình (TB)** | `synnd` | **Đã sửa (Resolved)** |

---

### CHI TIẾT CÁC LỖI VÀ GIẢI PHÁP ĐÃ SỬA CHỮA

#### 1. BUG_DASH_01: Mục "Đã lưu" trong trang Việc làm của tôi bị trống
- **Tiêu đề:** Tab "Công việc đã lưu" chưa có giao diện render và chưa kết nối API.
- **Mức độ nghiêm trọng:** **Trung bình (TB)**
- **Người phụ trách:** `synnd`
- **Mô tả chi tiết:** Khi sinh viên vào trang *Việc làm của tôi (`my_applications.html`)* và bấm sang tab "Công việc đã lưu", nội dung bên dưới bị trống trơn, không hiển thị thẻ công việc nào và không có file JavaScript xử lý sự kiện nạp dữ liệu.
- **Nguyên nhân gốc rễ (Root Cause):** Trang frontend chỉ mới dựng tab tĩnh HTML nhưng chưa viết logic gọi API `/api/dashboard/saved-jobs` và chưa có file CSS/JS riêng cho tab Đã lưu.
- **Giải pháp đã sửa (Code Fix):**
  1. Tạo mới file `frontend/js/saved_tab.js` và `frontend/css/saved_tab.css`.
  2. Viết hàm bất đồng bộ `fetchSavedJobs()` gọi API `GET /api/dashboard/saved-jobs` để lấy danh sách việc làm đã lưu từ server.
  3. Render giao diện các thẻ việc làm tương tự như danh sách ứng tuyển (gồm logo công ty, tiêu đề, mức lương, địa điểm và nút bỏ lưu).
- **Kết quả sau sửa:** Sinh viên bấm tab "Đã lưu" hiển thị đầy đủ danh sách công việc đã đánh dấu yêu thích.

---

#### 2. BUG_DASH_02: Nút "Trang chủ" trên Navbar Dashboard dẫn về `index.html` gây lỗi 404
- **Tiêu đề:** Sai liên kết trang chủ gây lỗi 404 Not Found khi bấm nút Trang chủ.
- **Mức độ nghiêm trọng:** **Trung bình (TB)**
- **Người phụ trách:** `synnd`
- **Mô tả chi tiết:** Khi đang ở các trang Dashboard (hoặc trang chi tiết), người dùng bấm vào nút "Trang chủ" trên thanh menu điều hướng thì trình duyệt chuyển đến đường dẫn `/index.html`, dẫn đến màn hình lỗi 404 Not Found.
- **Nguyên nhân gốc rễ (Root Cause):** Dự án đã đổi trang chủ chính thức thành `home.html`, nhưng một số liên kết `href` trên header của trang Dashboard vẫn còn giữ đường dẫn cũ `href="index.html"`. Đồng thời backend FastAPI chưa cấu hình chuyển hướng cho route gốc `/`.
- **Giải pháp đã sửa (Code Fix):**
  1. Thay thế toàn bộ liên kết `href="index.html"` thành `href="home.html"` trên các thanh Navbar.
  2. Tại file `backend/app/main.py`, bổ sung endpoint chuyển hướng:
     ```python
     @app.get("/", include_in_schema=False)
     def root_redirect():
         return RedirectResponse(url="/home.html")
     ```
- **Kết quả sau sửa:** Người dùng bấm vào nút "Trang chủ" hoặc truy cập địa chỉ gốc đều được đưa về trang chủ `home.html` chính xác 100%.

---

#### 3. BUG_DASH_03: API `get_my_jobs` thiếu phân trang gây `ResponseValidationError`
- **Tiêu đề:** Lỗi thiếu các trường `page, limit, total_pages` trong API lấy tin tuyển dụng của tôi.
- **Mức độ nghiêm trọng:** **Cao (High - Crash API)**
- **Người phụ trách:** `synnd`
- **Mô tả chi tiết:** Khi nhà tuyển dụng gọi API lấy danh sách tin `GET /jobs/my-jobs` để hiển thị thống kê tin trên Dashboard, hệ thống ném ra lỗi `fastapi.exceptions.ResponseValidationError: 3 validation errors: missing page, limit, total_pages`.
- **Nguyên nhân gốc rễ (Root Cause):** Schema Pydantic `JobListResponse` định nghĩa bắt buộc phải có đủ 5 trường: `total`, `page`, `limit`, `total_pages`, `items`. Tuy nhiên, trong file `backend/app/services/job_services.py`, hàm `get_my_jobs` chỉ trả về từ điển chứa 2 trường: `{"total": total, "items": items}`.
- **Giải pháp đã sửa (Code Fix):**
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

#### 4. BUG_DASH_04: Lệch icon trái tim và số lượng khi lưu/bỏ lưu tin liên tục (Spam Click)
- **Tiêu đề:** Không đồng bộ dữ liệu giữa Frontend và Backend khi thao tác lưu tin tuyển dụng nhanh.
- **Mức độ nghiêm trọng:** **Trung bình (TB)**
- **Người phụ trách:** `synnd`
- **Mô tả chi tiết:** Khi sinh viên nhấp nhanh nhiều lần vào nút icon trái tim để lưu/bỏ lưu tin tuyển dụng, giao diện bị giật, icon hiển thị sai trạng thái thực tế trong database và số lượng việc làm đã lưu hiển thị trên thanh Header không cập nhật.
- **Nguyên nhân gốc rễ (Root Cause):** Frontend trước đó chỉ đảo cờ cục bộ `savedJobs[id] = !savedJobs[id]` mà không đợi kết quả phản hồi từ backend, đồng thời backend không trả về tổng số lượng tin đã lưu mới nhất sau khi thao tác.
- **Giải pháp đã sửa (Code Fix):**
  1. Nâng cấp API `POST /api/dashboard/saved-jobs/{id}` và `DELETE /api/dashboard/saved-jobs/{id}` tính toán và trả về trường `saved_count` mới nhất trong database.
  2. Trong hàm `toggleSave(id)` tại `home.js`, sử dụng khối `try/catch` với `await SavedJobs.save(id)` / `await SavedJobs.unsave(id)`, cập nhật lại số lượng huy hiệu trên Header và vẽ lại icon trái tim chuẩn xác theo phản hồi từ server.
- **Kết quả sau sửa:** Dữ liệu trạng thái lưu tin và số lượng trên Dashboard luôn đồng bộ tuyệt đối với Database.

---

#### 5. BUG_DASH_05: Lỗi kiểm tra thông báo lỗi bị `KeyError: 'detail'`
- **Tiêu đề:** Phản hồi ngoại lệ tùy chỉnh `BaseResponse` gây lỗi `KeyError: 'detail'` khi kiểm thử API.
- **Mức độ nghiêm trọng:** **Trung bình (TB)**
- **Người phụ trách:** `synnd`
- **Mô tả chi tiết:** Khi chạy kiểm thử tự động các trường hợp lỗi (Negative Tests như 400, 401, 403, 404, 409), các bài test bị văng lỗi `KeyError: 'detail'`.
- **Nguyên nhân gốc rễ (Root Cause):** Mặc định FastAPI trả về lỗi dạng `{"detail": "..."}`. Tuy nhiên, dự án CareerHub sử dụng middleware xử lý lỗi tùy chỉnh tại `utils/exceptions.py`, chuẩn hóa toàn bộ phản hồi lỗi về mô hình `BaseResponse` với trường thông báo là `"message"` thay vì `"detail"`.
- **Giải pháp đã sửa (Code Fix):**
  - Xây dựng hàm helper chuẩn `get_error_message(response)` trong bộ kiểm thử `conftest.py`:
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

## IV. KẾT LUẬN & ĐÁNH GIÁ NGHIỆM THU

1. **Về độ bao phủ kiểm thử:**
   - Đã thực thi hoàn chỉnh **30 ca kiểm thử E2E thủ công**, bao phủ đầy đủ luồng thực tế của **3 vai trò người dùng** (Sinh viên, Nhà tuyển dụng, Quản trị viên) và **3 tính năng AI cốt lõi** của hệ thống.
   - Các luồng chính như: Đăng ký, Đăng nhập, Tìm kiếm, Đăng tin, Nộp đơn CV, Quản lý tài khoản, Chat AI đều vận hành ổn định và đạt kết quả mong muốn.

2. **Về kết quả khắc phục lỗi:**
   - Toàn bộ **5 lỗi thực tế phát sinh** đều do chính **`synnd`** trực tiếp giải quyết, kiểm chứng lại và hoạt động trơn tru.
   - Phân loại lỗi rõ ràng: **1 lỗi mức độ Cao, 4 lỗi mức độ Trung bình**, không còn lỗi tồn đọng gây gián đoạn trải nghiệm người dùng.
   - Hệ thống sẵn sàng nghiệm thu bàn giao.
