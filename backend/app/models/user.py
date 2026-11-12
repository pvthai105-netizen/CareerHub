import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Role(str, enum.Enum):
    student = "student"
    employer = "employer"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(Role), nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    employer_profile = relationship(
        "EmployerProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    student_profile = relationship(
        "StudentProfile", 
        back_populates="user", 
        uselist=False, 
        cascade="all, delete-orphan"
    )
    # Kết nối với bảng jobs
    jobs = relationship(
        "Job", 
        back_populates="employer", 
        cascade="all, delete-orphan"
    )                       
    saved_jobs = relationship(
        "SavedJob", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    # Kết nối với bảng đơn dv
    applications = relationship(
        "Application", 
        back_populates="student", 
        cascade="all, delete-orphan"
    )
     # Danh sách thông báo của người dùng này
    notifications = relationship(
        "Notification", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
        # Lịch sử tin nhắn chat của người dùng
    chat_messages = relationship(
        "ChatMessage", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
        # Danh sách các lần chấm điểm / phân tích CV của sinh viên
    cv_analyses = relationship(
        "CvAnalysis", 
        back_populates="student", 
        cascade="all, delete-orphan"
    )
    