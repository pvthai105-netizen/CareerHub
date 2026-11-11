import bcrypt


def hash_password(password: str) -> str:
    """Băm mật khẩu, trả về chuỗi để lưu vào cột password_hash."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Kiểm tra mật khẩu người dùng nhập có khớp bản băm đã lưu không."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))