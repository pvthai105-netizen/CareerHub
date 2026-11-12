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

Yêu cầu: Python 3.10 trở lên và MySQL 8.

### 1. Tạo database

Trong MySQL (Workbench hoặc dòng lệnh):

```sql
CREATE DATABASE careerhub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```


### 2. Cài đặt và chạy backend

Mở terminal tại thư mục gốc dự án:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Mở file `.env` và sửa `DATABASE_URL` theo user, mật khẩu MySQL trên máy bạn:

```env
DATABASE_URL='mysql+pymysql://USER:MẬT_KHẨU@localhost:3306/careerhub?charset=utf8mb4'
```

### 3. Tạo bảng và tài khoản demo

Đảm bảo đã tạo database và cấu hình `.env` thành công.

Chạy lệnh trong thư mục `backend`:

```powershell
python seed.py
```

Lệnh này tạo các bảng cần thiết và thêm 3 tài khoản mẫu nếu chưa tồn tại.

**Tài khoản demo:**

| Vai trò | Email | Mật khẩu |
|---------|-------|----------|
| Admin | admin@careerhub.vn | Admin@123 |
| Employer | employer@careerhub.vn | Employer@123 |
| Student | student@careerhub.vn | Student@123 |

### 4. Khởi động backend

```powershell
uvicorn app.main:app --reload
```

Sau khi chạy, kiểm tra các địa chỉ:

- Giao diện: http://127.0.0.1:8000
- Kiểm tra API: http://127.0.0.1:8000/api/health
- Tài liệu API tự động: http://127.0.0.1:8000/docs

**Lưu ý:**

- Các lệnh trên dành cho Windows PowerShell. Nếu `Activate.ps1` báo lỗi execution policy, chạy một lần `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
- File `.env` chứa mật khẩu riêng của từng máy, không đẩy lên GitHub. Chỉ sửa trong `.env`, không điền mật khẩu thật vào `.env.example`.
- Các tài khoản demo chỉ sử dụng cho môi trường phát triển và kiểm thử.

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

## Thiết kế Giao diện (UI/UX)
- **Figma Design / Prototype:** [Xem bản thiết kế CareerHub trên Figma](https://www.figma.com/design/ZOI0e2EpPElIK4PQvOzZzW/Wireframe-Figma?node-id=0-1&p=f&t=oV3zrzk4q8oNlbAo-0)