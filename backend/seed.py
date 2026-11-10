from passlib.context import CryptContext

from app.database import SessionLocal, engine
from app.models.user import Role, User
import app.models  # đảm bảo create_all chạy trước

# Tạo bảng nếu chưa có
from app.database import Base
Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SAMPLE_USERS = [
    {
        "email": "admin@careerhub.vn",
        "password": "Admin@123",
        "role": Role.admin,
    },
    {
        "email": "employer@careerhub.vn",
        "password": "Employer@123",
        "role": Role.employer,
    },
    {
        "email": "student@careerhub.vn",
        "password": "Student@123",
        "role": Role.student,
    },
]


def seed():
    db = SessionLocal()
    try:
        for data in SAMPLE_USERS:
            exists = db.query(User).filter(User.email == data["email"]).first()
            if exists:
                print(f"[SKIP] {data['email']} đã tồn tại")
                continue
            user = User(
                email=data["email"],
                password_hash=pwd_context.hash(data["password"]),
                role=data["role"],
                is_active=True, 
            )
            db.add(user)
            print(f"[ADD]  {data['email']} ({data['role']})")
        db.commit()
        print("\n✅ Seed hoàn tất!")
    finally:
        db.close()


if __name__ == "__main__":
    seed()