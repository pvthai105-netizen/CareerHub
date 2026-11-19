from datetime import datetime
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    # Nội dung sinh viên gửi; giới hạn độ dài để tránh request quá lớn.
    message: str = Field(min_length=1, max_length=4000)

class ChatReply(BaseModel):
    # Phần trả lời do trợ lý AI tạo ra.
    reply: str

class ChatHistoryItem(BaseModel):
    # Các trường lịch sử chat trả về cho giao diện.
    id: int
    sender: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True
