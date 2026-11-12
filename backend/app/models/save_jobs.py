from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.database import Base


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    saved_job_id = Column(Integer, primary_key=True, index=True, autoincrement=True)    
    # Khóa ngoại tới người dùng (student)
    user_id = Column(
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
    
    saved_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Ràng buộc UNIQUE tổ hợp (student_id, job_id)
    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_student_saved_job"),
    )

    # Quan hệ liên kết ngược
    user = relationship("User", back_populates="saved_jobs")
    job = relationship("Job", back_populates="saved_jobs")