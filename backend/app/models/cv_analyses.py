from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class CvAnalysis(Base):
    __tablename__ = "cv_analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Khóa ngoại liên kết tới sinh viên nộp CV
    student_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Đường dẫn hoặc URL file CV
    cv_file_url = Column(String(255), nullable=False)
    
    # Điểm số đánh giá (dùng kiểu Float để linh hoạt thang điểm 10 hoặc 100)
    score = Column(Float, nullable=True)
    
    # Nhận xét, góp ý chi tiết từ AI
    feedback = Column(Text, nullable=True)
    
    created_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        server_default=func.now(), 
        nullable=False
    )

    # Quan hệ N - 1 với User (student)
    student = relationship("User", back_populates="cv_analyses")