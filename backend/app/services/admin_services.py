from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.models.user import Role, User
from app.models.student_profiles import StudentProfile
from app.models.employee_profiles import EmployerProfile
from app.schemas.admin import (
    UserDetailResponse,
    UserListResponse,
    UserStatusUpdateSchema,
    UserSummaryResponse,
)


def get_users_list(
    db: Session,
    search: str | None = None,
    role: Role | None = None,
    is_locked: bool | None = None,
    page: int = 1,
    limit: int = 10,
) -> UserListResponse:
    """Tìm kiếm, lọc và phân trang danh sách người dùng cho Admin."""
    query = db.query(User)

    # 1. Tìm kiếm theo email
    if search and search.strip():
        search_kw = f"%{search.strip().lower()}%"
        query = query.filter(User.email.ilike(search_kw))

    # 2. Lọc theo role
    if role is not None:
        query = query.filter(User.role == role)

    # 3. Lọc theo trạng thái khóa
    if is_locked is not None:
        query = query.filter(User.is_locked == is_locked)

    total = query.count()
    users = (
        query.options(
            joinedload(User.student_profile),
            joinedload(User.employer_profile),
        )
        .order_by(User.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    items: list[UserSummaryResponse] = []
    for u in users:
        # Lấy tên hiển thị nếu có profile tương ứng
        name = None
        if u.role == Role.student and u.student_profile:
            name = u.student_profile.full_name
        elif u.role == Role.employer and u.employer_profile:
            name = u.employer_profile.company_name

        items.append(
            UserSummaryResponse(
                id=u.id,
                email=u.email,
                role=u.role,
                is_locked=u.is_locked,
                created_at=u.created_at,
                display_name=name,
            )
        )

    return UserListResponse(
        total=total,
        page=page,
        limit=limit,
        items=items,
    )


def get_user_detail(db: Session, user_id: int) -> UserDetailResponse:
    """Xem thông tin chi tiết một tài khoản kèm hồ sơ liên kết."""
    user = (
        db.query(User)
        .options(
            joinedload(User.student_profile),
            joinedload(User.employer_profile),
        )
        .filter(User.id == user_id)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng với ID này.",
        )

    student_data = None
    if user.student_profile:
        sp = user.student_profile
        student_data = {
            "id": sp.id,
            "full_name": sp.full_name,
            "phone": sp.phone,
            "university": sp.university,
            "major": sp.major,
            "skills": sp.skills,
            "desired_job_type": getattr(sp.desired_job_type, "value", sp.desired_job_type),
            "avatar_url": sp.avatar_url,
        }

    employer_data = None
    if user.employer_profile:
        ep = user.employer_profile
        employer_data = {
            "id": ep.id,
            "company_name": ep.company_name,
            "contact_name": ep.contact_name,
            "phone": ep.phone,
            "company_website": ep.company_website,
            "address": ep.address,
            "logo_url": ep.logo_url,
            "is_verified": ep.is_verified,
        }

    return UserDetailResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        is_locked=user.is_locked,
        created_at=user.created_at,
        student_profile=student_data,
        employer_profile=employer_data,
    )


def update_user_lock_status(
    db: Session,
    current_admin: User,
    user_id: int,
    payload: UserStatusUpdateSchema,
) -> UserDetailResponse:
    """Khóa hoặc mở khóa tài khoản người dùng."""
    # Ràng buộc bảo mật: Admin không được tự khóa chính mình
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin không thể tự khóa tài khoản của chính mình.",
        )

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng với ID này.",
        )

    user.is_locked = payload.is_locked
    db.commit()
    db.refresh(user)

    return get_user_detail(db, user_id)