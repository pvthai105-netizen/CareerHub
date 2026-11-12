from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_roles
from app.models.user import Role, User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Email đã được sử dụng")

    user = User(
        email=email,
        hashed_password=hash_password(data.password),
        role=Role(data.role),
        is_locked=False,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:  # hai yêu cầu đăng ký cùng email cùng lúc
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Email đã được sử dụng")
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email.lower()).first()
    # Dùng một thông báo chung, không tiết lộ email hay mật khẩu bên nào sai
    if user is None or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Email hoặc mật khẩu không đúng",
        )
    if user.is_locked:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Tài khoản đã bị khoá")

    return TokenResponse(access_token=create_access_token(user.id, user.role))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


# Endpoint thử quyền để nghiệm thu mã 403, có thể xoá khi các module khác đã dùng require_roles
@router.get("/admin-only")
def admin_only(user: User = Depends(require_roles(Role.admin))):
    return {"message": f"Xin chào admin {user.email}"}