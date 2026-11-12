from sqlalchemy import Column, ForeignKey, Enum,Integer, String, Text
from sqlalchemy.orm import relationship
import enum 
from app.database import Base

class DesiredJobType(str, enum.Enum):
    PART_TIME = "PART_TIME" 
    INTERNSHIP = "INTERNSHIP"
    BOTH = "BOTH"

class StudentProfile(Base):
    __tablename__ = "students_profile"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        unique=True, 
        nullable=False, 
        index=True
    )
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    university = Column(String(150), nullable=True)
    major = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    skills = Column(Text, nullable= True)
    desired_job_type = Column(
        Enum(DesiredJobType),
        nullable=False,
        default=DesiredJobType.BOTH
    )
    avatar_url = Column(String(255), nullable=True)

    user = relationship("User", back_populates="student_profile")
    