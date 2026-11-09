# Quy ước Git - Nhóm 4 CareerHub

## Nhánh
- main: bản ổn định, không commit trực tiếp
- feature/<mã-task>-<tên-ngắn>: làm tính năng mới
- fix/<mã-task>-<tên-ngắn>: sửa lỗi
Ví dụ: feature/t02cdb5-dang-nhap

## Commit message
Định dạng: <MÃ-TASK>: <động từ> <nội dung>
Ví dụ: T02CDB5: thêm form đăng nhập

## Pull Request
- Tiêu đề bắt đầu bằng mã task
- Cần ít nhất 1 bạn review trước khi merge
- Không tự merge khi chưa ai xem

## Quy trình mỗi ngày
1. git switch main
2. git pull
3. Tạo nhánh mới từ main
4. Commit nhỏ, thường xuyên
5. Push và mở PR
