from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Băm mật khẩu, trả về chuỗi để lưu vào cột password_hash."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Kiểm tra mật khẩu người dùng nhập có khớp bản băm đã lưu không."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(user_id: int, role) -> str:
    """Tạo JWT chứa id người dùng (sub), vai trò (role) và thời điểm hết hạn (exp)."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),                 # PyJWT yêu cầu sub là chuỗi
        "role": getattr(role, "value", role),  # nhận cả Role.student lẫn "student"
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Giải mã JWT. Token hết hạn ném jwt.ExpiredSignatureError,
    token sai ném jwt.InvalidTokenError; nơi gọi tự bắt và đổi thành 401."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])