import enum
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.database import Base


# Enum cho trạng thái đơn ứng tuyển (tùy chọn: dùng Enum hoặc String thuần)
class ApplicationStatus(str, enum.Enum):
    pending = "pending"        # Đang chờ duyệt
    reviewed = "reviewed"      # Đã xem hồ sơ
    accepted = "accepted"      # Trúng tuyển / Chấp nhận
    rejected = "rejected"      # Từ chối


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    job_id = Column(
        Integer, 
        ForeignKey("jobs.job_id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    student_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Có thể dùng Enum(ApplicationStatus) hoặc String(30)
    status = Column(
        Enum(ApplicationStatus), 
        default=ApplicationStatus.pending,  
        nullable=False
    )
    
    applied_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        server_default=func.now(), 
        nullable=False
    )

    # Ràng buộc UNIQUE tổ hợp (job_id, student_id)
    __table_args__ = (
        UniqueConstraint("job_id", "student_id", name="uq_student_job_application"),
    )

    # Quan hệ ngược về Job và User
    job = relationship("Job", back_populates="applications")
    student = relationship("User", back_populates="applications")