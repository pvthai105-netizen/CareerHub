from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.student_profiles import StudentProfile, DesiredJobType
from app.models.user import Role, User
from app.schemas.student_profile import StudentProfileUpdateSchema
from utils.validation import ensure_not_empty


def ensure_student(user: User) -> None:
    if user.role != Role.student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ tài khoản sinh viên mới có hồ sơ sinh viên.",
        )


def _attach_user_info(profile: StudentProfile) -> StudentProfile:
    if profile and profile.user:
        profile.email = profile.user.email
    return profile


def get_my_student_profile(db: Session, current_user: User) -> StudentProfile:
    ensure_student(current_user)
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        default_name = current_user.email.split("@")[0]
        profile = StudentProfile(
            user_id=current_user.id,
            full_name=default_name,
            desired_job_type=DesiredJobType.BOTH,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return _attach_user_info(profile)


def update_my_student_profile(
    db: Session,
    current_user: User,
    payload: StudentProfileUpdateSchema,
) -> StudentProfile:
    ensure_student(current_user)
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        profile = StudentProfile(
            user_id=current_user.id,
            full_name=payload.full_name or current_user.email.split("@")[0],
            phone=payload.phone,
            university=payload.university,
            major=payload.major,
            bio=payload.bio,
            skills=payload.skills,
            desired_job_type=payload.desired_job_type or DesiredJobType.BOTH,
            avatar_url=payload.avatar_url,
        )
        db.add(profile)
    else:
        if payload.full_name is not None:
            ensure_not_empty("full_name", payload.full_name)
            profile.full_name = payload.full_name.strip()
        if payload.phone is not None:
            profile.phone = payload.phone.strip() if payload.phone else None
        if payload.university is not None:
            profile.university = payload.university.strip() if payload.university else None
        if payload.major is not None:
            profile.major = payload.major.strip() if payload.major else None
        if payload.bio is not None:
            profile.bio = payload.bio.strip() if payload.bio else None
        if payload.skills is not None:
            profile.skills = payload.skills.strip() if payload.skills else None
        if payload.desired_job_type is not None:
            profile.desired_job_type = payload.desired_job_type
        if payload.avatar_url is not None:
            profile.avatar_url = payload.avatar_url.strip() if payload.avatar_url else None

    db.commit()
    db.refresh(profile)
    return _attach_user_info(profile)


def get_student_profile_by_id(db: Session, profile_id: int) -> StudentProfile:
    profile = db.query(StudentProfile).filter(StudentProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hồ sơ sinh viên.",
        )
    return _attach_user_info(profile)


def update_student_profile_by_id(
    db: Session,
    current_user: User,
    profile_id: int,
    payload: StudentProfileUpdateSchema,
) -> StudentProfile:
    profile = db.query(StudentProfile).filter(StudentProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy hồ sơ sinh viên.",
        )

    # RÀNG BUỘC: Chỉ chủ hồ sơ mới được sửa
    if profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền sửa hồ sơ này (chỉ chủ hồ sơ mới được sửa).",
        )

    if payload.full_name is not None:
        ensure_not_empty("full_name", payload.full_name)
        profile.full_name = payload.full_name.strip()
    if payload.phone is not None:
        profile.phone = payload.phone.strip() if payload.phone else None
    if payload.university is not None:
        profile.university = payload.university.strip() if payload.university else None
    if payload.major is not None:
        profile.major = payload.major.strip() if payload.major else None
    if payload.bio is not None:
        profile.bio = payload.bio.strip() if payload.bio else None
    if payload.skills is not None:
        profile.skills = payload.skills.strip() if payload.skills else None
    if payload.desired_job_type is not None:
        profile.desired_job_type = payload.desired_job_type
    if payload.avatar_url is not None:
        profile.avatar_url = payload.avatar_url.strip() if payload.avatar_url else None

    db.commit()
    db.refresh(profile)
    return _attach_user_info(profile)