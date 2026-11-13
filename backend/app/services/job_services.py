from datetime import date, datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.job import Job, JobStatus, JobType
from app.models.user import Role, User
from app.schemas.job import JobCreateSchema, JobUpdateSchema, JobStatusPatchSchema
from utils.validation import (
    ensure_not_empty,
    # ensure_unique,  # Đã không cần kiểm tra tiêu đề trùng
    validate_salary_range,
    validate_deadline,
)


def ensure_employer(user: User) -> None:
    """Kiểm tra người dùng có phải employer không."""
    if user.role != Role.employer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chỉ nhà tuyển dụng mới được thực hiện thao tác này",
        )


def validate_common_fields(db: Session, employer: User, payload, *, exclude_id: int | None = None) -> None:
    ensure_not_empty("title", payload.title)
    ensure_not_empty("description", payload.description)
    ensure_not_empty("industry", payload.industry)
    ensure_not_empty("location", payload.location)
    ensure_not_empty("job_type", payload.job_type)

    # Salary validation
    validate_salary_range(payload.salary_min, payload.salary_max)

    # Deadline validation (nếu được cung cấp)
    if payload.deadline:
        validate_deadline(payload.deadline)


def create_job(db: Session, employer: User, payload: JobCreateSchema) -> Job:
    ensure_employer(employer)
    validate_common_fields(db, employer, payload)

    job = Job(
        title=payload.title.title().strip(),
        description=payload.description.strip(),
        industry=payload.industry.strip(),
        location=payload.location.strip(),
        salary_min=payload.salary_min,
        salary_max=payload.salary_max,
        job_type=payload.job_type.value,
        deadline=payload.deadline,
        status=JobStatus.DRAFT.value,
        employer_id=employer.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_my_jobs(
    db: Session,                         # Phiên làm việc với Database
    employer: User,                      # Nhà tuyển dụng đang đăng nhập
    skip: int = 0,                       # Số bản ghi bỏ qua khi phân trang
    limit: int = 20,                     # Số bản ghi tối đa trả về
    status: Optional[JobStatus] = None,  # Trạng thái muốn lọc, mặc định không lọc
):

    # Kiểm tra người dùng có phải nhà tuyển dụng không
    ensure_employer(employer)

    # Tạo truy vấn lấy các tin thuộc nhà tuyển dụng hiện tại
    query = db.query(Job).filter(Job.employer_id == employer.id)

    # Nếu người dùng có truyền trạng thái cần lọc
    if status:

        # Chỉ lấy những tin có trạng thái tương ứng
        query = query.filter(Job.status == status.value)

    # Đếm tổng số tin thỏa mãn điều kiện lọc
    total = query.count()

    # Bỏ qua skip bản ghi và chỉ lấy tối đa limit bản ghi
    items = query.offset(skip).limit(limit).all()

    # Trả về tổng số tin và danh sách tin tuyển dụng
    return {"total": total, "items": items}


# Hàm lấy chi tiết một tin tuyển dụng của nhà tuyển dụng
def get_my_job(db: Session, employer: User, job_id: int) -> Job:

    # Kiểm tra người dùng có phải nhà tuyển dụng không
    ensure_employer(employer)

    # Tìm tin tuyển dụng theo job_id
    job = db.query(Job).filter(Job.job_id == job_id).first()

    # Nếu không tìm thấy tin tuyển dụng
    if not job:

        # Trả về lỗi 404 Not Found
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tin không tồn tại"
        )

    # Kiểm tra tin tuyển dụng có thuộc nhà tuyển dụng hiện tại không
    if job.employer_id != employer.id:

        # Nếu không phải chủ tin thì trả về lỗi 403 Forbidden
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền truy cập"
        )

    # Nếu tin tồn tại và đúng chủ sở hữu thì trả về tin
    return job


# Hàm cập nhật thông tin tin tuyển dụng
def update_job(
    db: Session,                    # Phiên làm việc với Database
    employer: User,                 # Nhà tuyển dụng đang đăng nhập
    job_id: int,                    # ID tin cần cập nhật
    payload: JobUpdateSchema        # Dữ liệu mới gửi lên
) -> Job:

    # Lấy tin và kiểm tra quyền sở hữu
    # Nếu không tồn tại hoặc không phải chủ tin thì hàm sẽ trả lỗi
    job = get_my_job(db, employer, job_id)

    # Kiểm tra logic mức lương mới
    validate_common_fields(db, employer, payload)

    # Chuyển dữ liệu Schema thành Dictionary
    # exclude_unset=True giúp bỏ qua những trường không được gửi lên
    data = payload.dict(exclude_unset=True)

    for field, value in data.items():   # Duyệt qua từng cặp key và value trong dữ liệu cập nhật
        if field == "job_type":     # Nếu trường đang cập nhật là job_type
            setattr(job, field, value.value)  # Lấy giá trị chuỗi của loại công việc rồi gán vào Job
        else:  # Với các trường còn lại
            setattr(job, field, value)   # Gán giá trị mới vào thuộc tính tương ứng của Job

    job.updated_at = datetime.utcnow()  # Cập nhật thời gian chỉnh sửa tin
    db.commit()
    db.refresh(job)
    return job


def delete_job(db: Session, employer: User, job_id: int):
    job = get_my_job(db, employer, job_id)
    db.delete(job)
    db.commit()


def change_status(
    db: Session,                         # Phiên làm việc với Database
    employer: User,                      # Nhà tuyển dụng đang đăng nhập
    job_id: int,                         # ID tin cần thay đổi trạng thái
    payload: JobStatusPatchSchema        # Trạng thái mới gửi lên
) -> Job:
    job = get_my_job(db, employer, job_id)

    # Lấy trạng thái mới từ dữ liệu đầu vào
    # Schema đã kiểm tra trạng thái có hợp lệ hay không
    new_status = payload.status

    # Nếu muốn chuyển trạng thái sang ACTIVE
    # nhưng hạn nộp hồ sơ đã qua
    if new_status == JobStatus.ACTIVE and job.deadline < date.today():

        # Trả về lỗi 400 Bad Request
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể đặt ACTIVE khi deadline đã qua. Cập nhật deadline trước.",
        )

    # Gán trạng thái mới vào tin tuyển dụng
    # .value lấy giá trị chuỗi để lưu vào Database
    job.status = new_status.value

    # Cập nhật thời gian chỉnh sửa
    job.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(job)
    return job