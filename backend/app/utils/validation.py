"""Utility validation helpers used across the CareerHub backend.

All helpers raise ``HTTPException`` with appropriate status codes and
Vietnamese error messages so they integrate directly with the ``ApiResponse``
error handling defined in ``exceptions.py``.
"""

from datetime import date, datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


def ensure_not_empty(field_name: str, value) -> None:
    """Raise 422 if *value* is ``None``, an empty string, or an empty collection.
    """
    if value is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Trường '{field_name}' không được để null.",
        )
    if isinstance(value, str) and not value.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Trường '{field_name}' không được để chuỗi trống.",
        )
    if isinstance(value, (list, dict, set, tuple)) and len(value) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Trường '{field_name}' không được để collection rỗng.",
        )


def ensure_unique(
    db: Session,
    model,
    field_name: str,
    value,
    *,
    exclude_id: int | None = None,
) -> None:
    """Raise 409 if another record of *model* has *field_name* = *value*.

    ``exclude_id`` is used when updating a record so the current row is not
    considered a duplicate.
    """
    column = getattr(model, field_name)
    query = db.query(model).filter(column == value)
    if exclude_id is not None:
        # Determine the primary‑key column name dynamically.
        pk_attr = getattr(model, "id", None)
        if pk_attr is None:
            # Fallback: use the first primary key column defined by SQLAlchemy.
            pk_attr = list(model.__mapper__.primary_key)[0]
        query = query.filter(pk_attr != exclude_id)
    if db.query(query.exists()).scalar():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Giá trị '{value}' cho trường '{field_name}' đã tồn tại.",
        )


def validate_salary_range(min_salary: int | None, max_salary: int | None) -> None:
    """Raise 422 when both salaries are provided and ``min > max``.
    """
    if min_salary is not None and max_salary is not None and min_salary > max_salary:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Mức lương tối thiểu không được lớn hơn mức lương tối đa.",
        )


def validate_deadline(deadline: date | datetime) -> None:
    """Raise 422 when ``deadline`` is earlier than now (UTC).

    Accepts both ``date`` and ``datetime``. If a plain ``date`` is given it is
    converted to a ``datetime`` at midnight UTC for a fair comparison.
    """
    if isinstance(deadline, date) and not isinstance(deadline, datetime):
        deadline_dt = datetime.combine(deadline, datetime.min.time())
    else:
        deadline_dt = deadline
    if deadline_dt < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Ngày hết hạn không được là quá khứ.",
        )
