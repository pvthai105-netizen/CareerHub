from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import engine
from app import models
from app.routers import auth
from app.routers import job_router
from utils.exceptions import exception_handlers
from app.routers import student_router
from app.routers import dashboard_router

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="CareerHub API")
exception_handlers(app)
app.include_router(auth.router)
app.include_router(job_router.router)
app.include_router(student_router.router)
app.include_router(dashboard_router.router)

@app.get("/api/health")
def health():
    return {"status": "ok"}


# Đặt SAU CÙNG: mount "/" khớp mọi đường dẫn còn lại
# Dòng 1: Tìm đường dẫn tới thư mục frontend
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

# Dòng 2: Phát file frontend cho trình duyệt
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
