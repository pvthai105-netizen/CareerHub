from pathlib import Path

from fastapi import FastAPI
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
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="CareerHub API")
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

app.include_router(auth.router)
app.include_router(job_router.router)
app.include_router(student_router.router)
app.include_router(employer_router.router)
app.include_router(admin_router.router)
app.include_router(admin_job_router.router)
app.include_router(dashboard_router.router)
app.include_router(chat_router.router)
app.include_router(application_router.router)

@app.get("/api/health")
def health():
    return {"status": "ok"}


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