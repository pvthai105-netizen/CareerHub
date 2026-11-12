import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Date, DateTime, DECIMAL, ForeignKey, Enum
from app.database import Base
from sqlalchemy.orm import relationship


class JobStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    CLOSED = "CLOSED"
    EXPIRED = "EXPIRED"


class JobType(str, enum.Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    INTERNSHIP = "INTERNSHIP"
    REMOTE = "REMOTE"
    CONTRACT = "CONTRACT"


class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    industry = Column(String(100), nullable=False)
    location = Column(String(255), nullable=False)

    salary_min = Column(DECIMAL(15, 2), nullable=True)
    salary_max = Column(DECIMAL(15, 2), nullable=True)

    job_type = Column(String(50), nullable=False)
    deadline = Column(Date, nullable=False)
    status = Column(String(30), default=JobStatus.DRAFT, nullable=False)

    employer_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    employer = relationship("User", back_populates="jobs")
    saved_jobs = relationship("SavedJob", back_populates="job")
    applications = relationship(
        "Application", 
        back_populates="job", 
        cascade="all, delete-orphan"
    )