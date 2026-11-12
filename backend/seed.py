import app.models  # noqa: F401  (nạp mọi model để create_all tạo đủ bảng)
from app.database import Base, SessionLocal, engine
from app.models.user import Role, User
from app.security import hash_password

# Mật khẩu DEMO, chỉ dùng để thử trên máy. Không dùng mật khẩu thật.
SAMPLE_USERS = [
    {"email": "admin@careerhub.vn", "password": "Admin@123", "role": Role.admin},
    {"email": "employer@careerhub.vn", "password": "Employer@123", "role": Role.employer},
    {"email": "student@careerhub.vn", "password": "Student@123", "role": Role.student},
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for data in SAMPLE_USERS:
            exists = db.query(User).filter(User.email == data["email"]).first()
            if exists:
                print(f"[SKIP] {data['email']} đã tồn tại")
                continue
            db.add(
                User(
                    email=data["email"],
                    hashed_password=hash_password(data["password"]),
                    role=data["role"],
                    is_locked=False,
                )
            )
            print(f"[ADD] {data['email']} ({data['role'].value})")
        db.commit()
        print("Seed hoàn tất")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()