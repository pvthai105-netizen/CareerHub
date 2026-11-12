from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Khóa ngoại liên kết tới người dùng (chủ cuộc trò chuyện)
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Người gửi tin nhắn: "user" hoặc "bot" / "assistant"
    sender = Column(String(50), nullable=False)
    
    # Nội dung tin nhắn chat
    message = Column(Text, nullable=False)
    
    created_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        server_default=func.now(), 
        nullable=False
    )

    # Quan hệ N - 1 với User
    user = relationship("User", back_populates="chat_messages")