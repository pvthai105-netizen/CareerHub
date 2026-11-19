import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./careerhub.db")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
# Khóa Gemini API, đọc từ .env; để trống thì endpoint chat trả về lỗi chưa cấu hình.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# Model Gemini có thể đổi qua biến GEMINI_MODEL trong .env.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
