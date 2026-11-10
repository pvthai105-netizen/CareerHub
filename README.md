# CareerHub

Nền tảng tìm việc làm thêm và thực tập cho sinh viên.

## Vai trò
- Student: tìm và ứng tuyển việc làm
- Employer: đăng tin tuyển dụng
- Admin: quản trị hệ thống

## Thành viên Nhóm 4
- Phạm Văn Thái (B25DTCN298)
- Vũ Nhất Thống (B25DTCN280)
- Vũ Quang Việt (B25DTCN217)
- Đặng Thị Thu Cúc (B25DTCN070)
- Mai Trọng Doanh (B25DTCN075)
- Nguyễn Phạm Hoàng Trung (B25DTCN211)

## Chạy dự án

Yêu cầu: Python 3.10 trở lên.

```
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Sau khi chạy, kiểm tra các địa chỉ:

- Giao diện: http://127.0.0.1:8000
- Kiểm tra API: http://127.0.0.1:8000/api/health
- Tài liệu API tự động: http://127.0.0.1:8000/docs

Lưu ý:
- Các lệnh trên dành cho Windows PowerShell. Nếu `Activate.ps1` báo lỗi execution policy, chạy một lần `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
- File `.env` chứa cấu hình riêng của từng máy, không đẩy lên GitHub. Chỉ sửa trong `.env`, không sửa `.env.example`.

## Cấu trúc thư mục

- `backend/`: FastAPI + SQLAlchemy
  - `app/main.py`: tạo ứng dụng, các route API và phục vụ frontend
  - `app/config.py`: đọc cấu hình từ `.env`
  - `app/database.py`: kết nối cơ sở dữ liệu
  - `.env.example`: file cấu hình mẫu
  - `requirements.txt`: danh sách thư viện
- `frontend/`: HTML, CSS, JS thuần (FastAPI phục vụ bằng StaticFiles)
  - `js/api.js`: hàm gọi API, tự gắn JWT vào mỗi yêu cầu
- `docs/`: tài liệu của nhóm