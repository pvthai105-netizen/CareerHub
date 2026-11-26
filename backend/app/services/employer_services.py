import os
import re
import uuid
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.employee_profiles import EmployerProfile
from app.models.user import Role, User
from app.schemas.employer_profile import (
    EmployerProfileCreateSchema,
    EmployerProfileUpdateSchema,
    LogoUploadResponse,
)
from utils.validation import ensure_not_empty

# Giới hạn dung lượng logo: Tối đa 2 MB
MAX_LOGO_SIZE_BYTES = 2 * 1024 * 1024  # 2MB
ALLOWED_IMAGE_TYPES = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/webp": ".webp",
}


def ensure_employer(user: User) -> None:
    """Kiểm tra quyền: Bắt buộc tài khoản phải có vai trò Employer."""
    if user.role != Role.employer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ tài khoản Nhà tuyển dụng (employer) mới có quyền thực hiện thao tác này.",
        )


def _attach_user_info(profile: EmployerProfile) -> EmployerProfile:
    """Gắn thêm email tài khoản vào profile trả về."""
    if profile and profile.user:
        profile.email = profile.user.email
    return profile


def get_my_employer_profile(db: Session, current_user: User) -> EmployerProfile:
    """Lấy thông tin hồ sơ của chính Employer đang đăng nhập."""
    ensure_employer(current_user)
    profile = db.query(EmployerProfile).filter(EmployerProfile.user_id == current_user.id).first()
    if not profile:
        default_company_name = f"Công ty của {current_user.email.split('@')[0]}"
        profile = EmployerProfile(
            user_id=current_user.id,
            company_name=default_company_name,
            is_verified=False,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return _attach_user_info(profile)


def create_or_update_my_employer_profile(
    db: Session,
    current_user: User,
    payload: EmployerProfileUpdateSchema,
) -> EmployerProfile:
    """Tạo hoặc cập nhật hồ sơ của chính doanh nghiệp đang đăng nhập."""
    ensure_employer(current_user)
    profile = db.query(EmployerProfile).filter(EmployerProfile.user_id == current_user.id).first()

    if not profile:
        company_name = payload.company_name or f"Công ty của {current_user.email.split('@')[0]}"
        ensure_not_empty("company_name", company_name)
        profile = EmployerProfile(
            user_id=current_user.id,
            company_name=company_name.strip(),
            contact_name=payload.contact_name,
            phone=payload.phone,
            company_website=payload.company_website,
            address=payload.address,
            description=payload.description,
            tax_code=payload.tax_code,
            logo_url=payload.logo_url,
            is_verified=False,
        )
        db.add(profile)
    else:
        if payload.company_name is not None:
            ensure_not_empty("company_name", payload.company_name)
            profile.company_name = payload.company_name.strip()
        if payload.contact_name is not None:
            profile.contact_name = payload.contact_name.strip() if payload.contact_name else None
        if payload.phone is not None:
            profile.phone = payload.phone.strip() if payload.phone else None
        if payload.company_website is not None:
            profile.company_website = payload.company_website.strip() if payload.company_website else None
        if payload.address is not None:
            profile.address = payload.address.strip() if payload.address else None
        if payload.description is not None:
            profile.description = payload.description.strip() if payload.description else None
        if payload.tax_code is not None:
            profile.tax_code = payload.tax_code.strip() if payload.tax_code else None
        if payload.logo_url is not None:
            profile.logo_url = payload.logo_url.strip() if payload.logo_url else None

    db.commit()
    db.refresh(profile)
    return _attach_user_info(profile)


def get_employer_profile_by_id(db: Session, profile_id: int) -> EmployerProfile:
    """Xem thông tin công ty theo ID (dành cho ứng viên & người dùng xem công khai)."""
    profile = db.query(EmployerProfile).filter(EmployerProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hồ sơ công ty.",
        )
    return _attach_user_info(profile)


def update_employer_profile_by_id(
    db: Session,
    current_user: User,
    profile_id: int,
    payload: EmployerProfileUpdateSchema,
) -> EmployerProfile:
    """Cập nhật hồ sơ công ty theo ID.
    RÀNG BUỘC BẮT BUỘC: CHỈ CHỦ CÔNG TY MỚI ĐƯỢC PHÉP SỬA.
    """
    profile = db.query(EmployerProfile).filter(EmployerProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hồ sơ công ty.",
        )

    # Chặn ngay nếu người gửi không phải là chủ sở hữu công ty
    if profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền sửa hồ sơ này (chỉ chủ công ty mới được sửa).",
        )

    if payload.company_name is not None:
        ensure_not_empty("company_name", payload.company_name)
        profile.company_name = payload.company_name.strip()
    if payload.contact_name is not None:
        profile.contact_name = payload.contact_name.strip() if payload.contact_name else None
    if payload.phone is not None:
        profile.phone = payload.phone.strip() if payload.phone else None
    if payload.company_website is not None:
        profile.company_website = payload.company_website.strip() if payload.company_website else None
    if payload.address is not None:
        profile.address = payload.address.strip() if payload.address else None
    if payload.description is not None:
        profile.description = payload.description.strip() if payload.description else None
    if payload.tax_code is not None:
        profile.tax_code = payload.tax_code.strip() if payload.tax_code else None
    if payload.logo_url is not None:
        profile.logo_url = payload.logo_url.strip() if payload.logo_url else None

    db.commit()
    db.refresh(profile)
    return _attach_user_info(profile)


def upload_company_logo(
    db: Session,
    current_user: User,
    file: UploadFile,
    profile_id: Optional[int] = None,
) -> LogoUploadResponse:
    """Upload ảnh logo công ty:
    1. Chỉ nhận file định dạng ảnh (.png, .jpg, .jpeg, .webp)
    2. Giới hạn dung lượng tối đa 2MB
    3. Chỉ chủ công ty mới được upload logo cho công ty mình
    """
    ensure_employer(current_user)

    # 1. Xác định hồ sơ mục tiêu & kiểm tra quyền sở hữu
    if profile_id is not None:
        profile = db.query(EmployerProfile).filter(EmployerProfile.id == profile_id).first()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy hồ sơ công ty.")
        if profile.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền sửa hồ sơ này (chỉ chủ công ty mới được sửa).",
            )
    else:
        profile = db.query(EmployerProfile).filter(EmployerProfile.user_id == current_user.id).first()
        if not profile:
            profile = get_my_employer_profile(db, current_user)

    # 2. KIỂM TRA ĐỊNH DẠNG FILE: Chỉ chấp nhận ảnh (whitelist đuôi file và content-type)
    content_type = (file.content_type or "").lower()
    file_ext = Path(file.filename or "").suffix.lower()

    if content_type not in ALLOWED_IMAGE_TYPES or file_ext not in ALLOWED_IMAGE_TYPES.values():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tệp không hợp lệ. Hệ thống chỉ chấp nhận định dạng ảnh (.png, .jpg, .jpeg, .webp).",
        )

    # 3. KIỂM TRA DUNG LƯỢNG FILE: Giới hạn tối đa 2MB (đọc buffer an toàn chống cạn kiệt RAM)
    try:
        content = file.file.read(MAX_LOGO_SIZE_BYTES + 1)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Không thể đọc nội dung tệp: {str(e)}",
        )

    file_size = len(content)
    if file_size > MAX_LOGO_SIZE_BYTES:
        size_mb = file_size / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dung lượng ảnh ({size_mb:.2f}MB) vượt quá giới hạn tối đa 2.0MB cho phép.",
        )

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tệp tải lên rỗng (0 bytes). Vui lòng chọn tệp ảnh hợp lệ.",
        )

    # 4. KIỂM TRA CHỮ KÝ TỆP (MAGIC BYTES): Chống giả mạo đuôi file
    is_valid_image = False
    if file_ext == ".png" and content.startswith(b"\x89PNG\r\n\x1a\n"):
        is_valid_image = True
    elif file_ext in [".jpg", ".jpeg"] and content.startswith(b"\xff\xd8\xff"):
        is_valid_image = True
    elif file_ext == ".webp" and content.startswith(b"RIFF") and b"WEBP" in content[8:16]:
        is_valid_image = True

    if not is_valid_image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tệp không hợp lệ. Hệ thống chỉ chấp nhận định dạng ảnh (.png, .jpg, .jpeg, .webp).",
        )

    # 4. LƯU ẢNH VÀO THƯ MỤC UPLOADS
    base_dir = Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "uploads" / "logos"
    base_dir.mkdir(parents=True, exist_ok=True)

    ext = file_ext if file_ext in ALLOWED_IMAGE_TYPES.values() else ALLOWED_IMAGE_TYPES.get(content_type, ".png")
    safe_name = f"logo_{profile.id}_{uuid.uuid4().hex[:8]}{ext}"
    target_path = base_dir / safe_name

    with open(target_path, "wb") as f:
        f.write(content)

    # 5. CẬP NHẬT ĐƯỜNG DẪN LOGO VÀO DATABASE
    logo_relative_url = f"/uploads/logos/{safe_name}"
    profile.logo_url = logo_relative_url
    db.commit()
    db.refresh(profile)

    return LogoUploadResponse(
        message="Upload logo công ty thành công",
        logo_url=logo_relative_url,
        file_name=safe_name,
        file_size_kb=round(file_size / 1024, 2),
    )