from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.database import engine
from app import models
from app.routers import auth
from app.routers import job_router
from utils.exceptions import exception_handlers
from app.routers import student_router
from app.routers import chat_router
from app.routers import dashboard_router
from app.routers import employer_router
from app.routers import admin_router
from app.routers import admin_job_router
from app.routers import application_router
from app.routers import notification_router
from app.routers import save_router
from fastapi.middleware.cors import CORSMiddleware

# Import BackgroundScheduler để tạo bộ lập lịch chạy tự động
from apscheduler.schedulers.background import BackgroundScheduler

# Import hàm xử lý đóng tin tuyển dụng quá hạn từ job_services.py
from app.services.job_services import close_expired_jobs

# Import SessionLocal để tạo kết nối Database
from app.database import SessionLocal

# Import asynccontextmanager để quản lý lúc FastAPI khởi động và tắt
from contextlib import asynccontextmanager

models.Base.metadata.create_all(bind=engine)

# TẠO SCHEDULER
# Tạo một bộ lập lịch chạy ngầm.
# Bộ lập lịch này có nhiệm vụ gọi các hàm theo thời gian đã cài đặt.
scheduler = BackgroundScheduler()


# TẠO HÀM THỰC HIỆN CÔNG VIỆC ĐÓNG TIN QUÁ HẠN
def run_close_expired_jobs():
    # Tạo một phiên kết nối Database mới để thực hiện công việc.
    # Mỗi lần Scheduler gọi hàm này sẽ có một phiên làm việc riêng.
    db = SessionLocal()

    try:
        # Gọi hàm xử lý trong job_services.py.
        # Truyền kết nối Database vào để hàm có thể truy vấn và cập nhật dữ liệu.
        count = close_expired_jobs(db)

        # In ra số lượng tin đã được đóng để dễ kiểm tra trong Terminal.
        print(f"Đã đóng {count} tin tuyển dụng quá hạn.")

    except Exception as errors:
        # Nếu xảy ra lỗi, hoàn tác các thay đổi chưa được lưu.
        db.rollback()

        # In lỗi ra Terminal để kiểm tra
        print(f"Lỗi khi đóng tin tuyển dụng quá hạn: {errors}")

    finally:
        # Đóng phiên kết nối Database sau khi hoàn thành.
        # Dù thành công hay xảy ra lỗi thì dòng này vẫn được thực hiện.
        db.close()


# ĐĂNG KÝ LỊCH CHẠY TỰ ĐỘNG
# Yêu cầu Scheduler gọi hàm run_close_expired_jobs mỗi giờ một lần
# cron là kiểu lập lịch chạy tác vụ theo thời gian cố định
# minute=0 nghĩa là chạy vào phút thứ 0 của mỗi giờ
# Ví dụ: 14:00, 15:00, 16:00...
scheduler.add_job(
    run_close_expired_jobs,
    "cron",                    
    minute=0
)


# QUẢN LÝ SCHEDULER THEO VÒNG ĐỜI FASTAPI
# Context Manager là cơ chế giúp Python quản lý tài nguyên hoặc công việc theo 3 bước:
# 1. Bắt đầu thực hiện công việc
# 2. Thực hiện công việc bên trong
# 3. Kết thúc và giải phóng tài nguyên
@asynccontextmanager         # Đây là một decorator của Python, 
                             # giúp tạo một cơ chế quản lý quá trình bắt đầu và kết thúc của ứng dụng FastAPI bằng async và yield
async def lifespan(app: FastAPI):
    # Khi FastAPI bắt đầu chạy, khởi động Scheduler.
    # Từ thời điểm này Scheduler bắt đầu thực hiện lịch đã đăng ký.
    scheduler.start()

    # Giữ ứng dụng FastAPI tiếp tục hoạt động.
    # Khi ứng dụng tắt, chương trình mới chạy xuống phần bên dưới.
    yield

    # Khi FastAPI tắt, dừng Scheduler để không còn tác vụ chạy ngầm
    if scheduler.running:  # Kiểm tra Scheduler có đang chạy không
        scheduler.shutdown()  # Dừng Scheduler khi ứng dụng tắt


# KHỞI TẠO ỨNG DỤNG FASTAPI
# Gắn lifespan vào FastAPI để Scheduler tự khởi động và dừng
# theo vòng đời của ứng dụng.
app = FastAPI(title="CareerHub API", lifespan=lifespan)


exception_handlers(app)

# ----- CORS configuration -------------------------------------------------
# Cho phép frontend chạy ở http://127.0.0.1:5500 (Live Server) truy cập API.
origins = [
    "http://127.0.0.1:5500",          # Local development
    "http://localhost:5500",          # Ngoại lệ nếu dùng localhost
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Chỉ cho phép các origin ở trên
    allow_credentials=True,           # Nếu có gửi cookie / Authorization header
    allow_methods=["*"],              # Cho phép GET, POST, PUT, DELETE, …
    allow_headers=["*"],              # Cho phép bất kỳ header nào (Authorization, Content-Type,…)
)

@app.get("/api/health")
def health():
    return {"status": "ok"}

app.include_router(auth.router)
app.include_router(job_router.router)
app.include_router(student_router.router)
app.include_router(employer_router.router)
app.include_router(admin_router.router)
app.include_router(admin_job_router.router)
app.include_router(dashboard_router.router)
app.include_router(chat_router.router)
app.include_router(application_router.router)
app.include_router(notification_router.router)
app.include_router(save_router.router)



@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"], include_in_schema=False)
def api_not_found(path: str):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy API endpoint")


@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/home.html")


# Đặt SAU CÙNG: mount "/" khớp mọi đường dẫn còn lại
# Dòng 1: Tìm đường dẫn tới thư mục frontend
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

# Dòng 2: Phát file frontend cho trình duyệt
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
# Vì sao phải đặt ở cuối file:
# FastAPI xét các địa chỉ theo thứ tự từ trên xuống. Địa chỉ "/" khớp với mọi đường dẫn. 
# Nếu mount đứng trước route /api/health, mọi yêu cầu sẽ bị StaticFiles nhận trước, và /api/health sẽ báo 404 vì nó đi tìm file tên api/health. 
# Đặt ở cuối thì các route /api/... được xử lý trước, những gì còn lại mới chuyển cho frontend.
