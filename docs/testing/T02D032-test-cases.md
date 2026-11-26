# Test case — T02D032: Thông báo

Phạm vi gồm API đếm chưa đọc, danh sách/paging, đánh dấu đã đọc, kiểm soát quyền theo người dùng và phát sinh thông báo khi có đơn mới hoặc trạng thái ứng tuyển đổi.

| ID | Loại | Tình huống | Kết quả mong đợi |
|---|---|---|---|
| TC01 | Đúng | Gọi route thông báo | Các route khai báo phụ thuộc người dùng đã xác thực. |
| TC02 | Đúng | Một thông báo chưa đọc của người dùng hiện tại, thêm thông báo đã đọc và thông báo của người khác | Bộ đếm chỉ là `1`. |
| TC03 | Đúng | Lấy danh sách với `limit=1`, `offset=1` | Trả về đúng một thông báo của người dùng hiện tại, sắp xếp mới nhất trước. |
| TC04 | Biên | `limit=1` và `limit=100` | Chấp nhận cận dưới và trên theo khai báo Query. |
| TC05 | Sai | `limit=0` hoặc `limit=101` | API từ chối tham số ngoài khoảng `[1, 100]` với HTTP 422. |
| TC06 | Biên | `offset=0` và `offset=-1` | Cận `0` được chấp nhận; số âm bị từ chối với HTTP 422. |
| TC07 | Đúng | Đánh dấu một thông báo chưa đọc; lặp lại yêu cầu | Cả hai lần thành công; thông báo đã đọc và bộ đếm về `0`. |
| TC08 | Sai | Người dùng hiện tại đánh dấu thông báo thuộc người khác | HTTP 404; trạng thái thông báo không đổi. |
| TC09 | Sai | Đánh dấu ID không tồn tại | HTTP 404. |
| TC10 | Đúng | Sinh viên nộp đơn hợp lệ | Nhà tuyển dụng của tin nhận một thông báo chưa đọc, có tiêu đề/nội dung phù hợp. |
| TC11 | Đúng | Nhà tuyển dụng chuyển đơn từ `pending` sang `interview` | Sinh viên nhận thông báo chưa đọc, nội dung thể hiện trạng thái trước và sau. |
| TC12 | Sai | Chuyển đơn `pending` trực tiếp sang `accepted` | Bị từ chối HTTP 409; không tạo thông báo trạng thái. |
| TC13 | Biên | Lấy trang đầu và item cuối với `limit=1`; offset vượt tổng số item | Trang đầu/cuối trả đúng item; offset vượt dữ liệu trả danh sách rỗng. |
| TC14 | Biên | Hai thông báo có cùng thời điểm tạo | Sắp xếp ổn định theo ID giảm dần. |

## Cách chạy

Từ thư mục `backend`:

```powershell
.venv\Scripts\python.exe -m pytest tests/test_notifications_api.py tests/test_applications_api.py -q
```

Các case được cài thành test tự động tại `backend/tests/test_notifications_api.py`; test ứng tuyển hiện có cũng được chạy để xác nhận luồng phát sinh thông báo không làm hỏng module liên quan.
