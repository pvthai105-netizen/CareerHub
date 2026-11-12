from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.database import Base


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Khóa ngoại tới người dùng (student)
    student_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Khóa ngoại tới công việc
    job_id = Column(
        Integer, 
        ForeignKey("jobs.job_id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    saved_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        server_default=func.now(), 
        nullable=False
    )

    # Ràng buộc UNIQUE tổ hợp (student_id, job_id)
    __table_args__ = (
        UniqueConstraint("student_id", "job_id", name="uq_student_saved_job"),
    )

    # Quan hệ liên kết ngược
    student = relationship("User", back_populates="saved_jobs")
    job = relationship("Job", back_populates="saved_by_students")