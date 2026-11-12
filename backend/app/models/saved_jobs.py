from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, ForeignKey
from app.database import Base
from sqlalchemy.orm import relationship


class SavedJob(Base):
    __tablename__ = "saved_jobs"
    saved_job_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.job_id", ondelete="CASCADE"), nullable=False)
    saved_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="saved_jobs")
    job = relationship("Job", back_populates="saved_jobs")