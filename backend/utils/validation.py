import logging  # thư viện ghi nhật ký hoạt động
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, date
logger = logging.getLogger(__name__)  # getLogger(): lấy một đối tượng cần ghi, __name__: trỏ đến tên module hiện tại


def ensure_not_empty(field_name: str, value) -> None:  # hàm không trả về giá trị
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Trường '{field_name}' không được để null.",
        )
    if isinstance(value, str) and not value.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Trường '{field_name}' không được để chuỗi trống.",
        )
    if isinstance(value, (list, dict, set, tuple)) and len(value) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Trường '{field_name}' không được để các dấu ngoặc rỗng.",
        )

def validate_salary_range(min_salary: int | None, max_salary: int | None) -> None:
    if min_salary is not None and max_salary is not None:
        if min_salary > max_salary:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Mức lương tối thiểu không được lớn hơn mức lương tối đa.",
            )


def validate_deadline(deadline: date | datetime) -> None:
    if isinstance(deadline, datetime):
        deadline_date = deadline.date()
    else:
        deadline_date = deadline
    now_date = date.today()
    if deadline_date < now_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Ngày hết hạn không được là quá khứ.",
        )