from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="CareerHub API")


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Đặt SAU CÙNG: mount "/" khớp mọi đường dẫn còn lại
# Dòng 1: Tìm đường dẫn tới thư mục frontend
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"
# Vì sao không viết thẳng "D:\Education_IT\..."? 
# Vì đường dẫn đó chỉ đúng trên máy bạn. Các bạn khác clone về sẽ để dự án ở chỗ khác.
# Cách tính từ vị trí của main.py thì máy nào cũng chạy đúng.

# Dòng 2: Phát file frontend cho trình duyệt
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
# Vì sao phải đặt ở cuối file
# FastAPI xét các địa chỉ theo thứ tự từ trên xuống. Địa chỉ "/" khớp với mọi đường dẫn. 
# Nếu mount đứng trước route /api/health, mọi yêu cầu sẽ bị StaticFiles nhận trước, và /api/health sẽ báo 404 vì nó đi tìm file tên api/health. 
# Đặt ở cuối thì các route /api/... được xử lý trước, những gì còn lại mới chuyển cho frontend.
#Hai dòng này cùng làm một việc: chỉ cho FastAPI biết thư mục frontend nằm ở đâu, và bảo nó phát các file trong đó cho trình duyệt.