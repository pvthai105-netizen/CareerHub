from sqlalchemy import Column, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class EmployerProfile(Base):
    __tablename__ = "employers_profile"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    company_name = Column(String(200), nullable=False)
    contact_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    company_website = Column(String(255), nullable=True)
    address = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    logo_url = Column(String(255), nullable=True)
    tax_code = Column(String(50), nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Quan hệ 1 - 1 với User bằng back_populates
    user = relationship("User", back_populates="employer_profile")