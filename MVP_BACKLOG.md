## 1. Phạm Vi MVP Theo 3 Vai Trò
- **Sinh viên:** Đăng nhập JWT, cập nhật hồ sơ/CV cá nhân, tìm kiếm & ứng tuyển việc làm, sử dụng tính năng AI (Chatbot, Job Matching, CV Analysis).
- **Nhà tuyển dụng:** Quản lý thông tin công ty, CRUD tin tuyển dụng, quản lý danh sách ứng viên và cập nhật trạng thái ứng tuyển.
- **Quản trị viên:** Quản lý tài khoản người dùng, kiểm duyệt/ẩn tin tuyển dụng, xem thống kê hệ thống trên Dashboard.

---

## 2. User Stories Module AI Của Tôi
- **US-AI-01:** Là Sinh viên, tôi muốn trò chuyện với AI Chatbot để nhận tư vấn định hướng nghề nghiệp và giải đáp thắc mắc 24/7.
- **US-AI-02:** Là Sinh viên, tôi muốn nhập câu lệnh bằng ngôn ngữ tự nhiên để hệ thống tìm việc làm phù hợp kèm theo tỷ lệ match (%).
- **US-AI-03:** Là Sinh viên, tôi muốn tải file CV lên để AI phân tích, chấm điểm và gợi ý cải thiện hồ sơ.

---

## 3. Quy Ước Nhánh & Commit (Git Conventions)
- **Cấu trúc nhánh:**
  - `main`: Nhánh production ổn định.
  - `dev`: Nhánh tích hợp chung của nhóm.
  - `feature/<ma_task>-<ten_ngan>` (Ví dụ: `feature/ai-chatbot`): Nhánh làm việc cá nhân.
- **Quy ước Commit Message:**
  - Cú pháp: `<Ma_Task>: <type>: <mô tả ngắn gọn>`
  - Các loại `type` chuẩn: `feat`, `fix`, `docs`, `refactor`.