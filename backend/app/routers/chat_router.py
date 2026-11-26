from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_db, require_roles
from app.models.user import Role, User
from app.schemas.chat import ChatHistoryItem, ChatReply, ChatRequest
from app.services.chat_service import get_chat_history, send_chat_message

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatReply, summary="Chat tư vấn nghề nghiệp")
def api_send_chat_message(payload: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(require_roles(Role.student)),):
    """Gửi câu hỏi cho trợ lý AI và lưu lượt chat vào lịch sử sinh viên."""
    # Dùng user lấy từ JWT, không nhận user_id từ request để tránh xem/ghi chéo tài khoản.
    reply = send_chat_message(db, current_user, payload.message)
    return ChatReply(reply=reply)


@router.get("/history", response_model=list[ChatHistoryItem], summary="Xem lịch sử chat")
def api_get_chat_history(db: Session = Depends(get_db), current_user: User = Depends(require_roles(Role.student)),):
    """Trả tối đa 100 tin nhắn mới nhất thuộc sinh viên đang đăng nhập."""
    # Service luôn lọc bằng ID của tài khoản hiện tại.
    return get_chat_history(db, current_user)
