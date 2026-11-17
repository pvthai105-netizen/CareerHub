from fastapi import HTTPException, status
from google import genai
from google.genai import errors, types
from sqlalchemy.orm import Session

from app.config import GEMINI_API_KEY, GEMINI_MODEL
from app.models.chat_messages import ChatMessage
from app.models.user import User

# Giới hạn số tin gần nhất gửi cho AI để giữ câu trả lời bám sát hội thoại.
HISTORY_CONTEXT_LIMIT = 20

# Vai trò và giới hạn tư vấn của trợ lý CareerHub.
CAREER_COUNSELOR_SYSTEM_PROMPT = """
Bạn là trợ lý tư vấn nghề nghiệp của CareerHub dành cho sinh viên.
Hãy trả lời bằng tiếng Việt, thân thiện, thực tế và có cấu trúc rõ ràng.
Ưu tiên hỗ trợ khám phá nghề nghiệp, kỹ năng, CV, phỏng vấn, thực tập và kế hoạch tìm việc.
Dựa trên thông tin sinh viên đã chia sẻ; nếu thiếu dữ kiện quan trọng, hãy hỏi thêm thay vì tự suy đoán.
Đưa ra các bước tiếp theo cụ thể và phù hợp với hoàn cảnh sinh viên.
Không cam kết việc làm, không bịa thông tin tuyển dụng hoặc mức lương; hãy nói rõ khi thông tin chỉ mang tính tham khảo.
""".strip()


def get_chat_history(db: Session, user: User) -> list[ChatMessage]:
    """Chỉ trả lịch sử thuộc tài khoản đang đăng nhập."""
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user.id)
        .order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())
        .limit(100)
        .all()[::-1]
    )


def send_chat_message(db: Session, user: User, message: str) -> str:
    """Gọi mô hình tư vấn và lưu hai phía của lượt chat theo user_id."""
    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dịch vụ tư vấn Gemini chưa được cấu hình.",
        )

    # Lấy hội thoại cũ theo thứ tự thời gian để mô hình hiểu ngữ cảnh gần nhất.
    previous_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user.id)
        .order_by(ChatMessage.created_at.desc(), ChatMessage.id.desc())
        .limit(HISTORY_CONTEXT_LIMIT)
        .all()[::-1]
    )
    contents = [
        types.Content(
            role="model" if item.sender in ("assistant", "bot") else "user",
            parts=[types.Part.from_text(text=item.message)],
        )
        for item in previous_messages
    ]
    contents.append(
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=message.strip())],
        )
    )

    try:
        # Gửi lịch sử hội thoại và chỉ dẫn vai trò đến Gemini.
        with genai.Client(api_key=GEMINI_API_KEY) as client:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=CAREER_COUNSELOR_SYSTEM_PROMPT,
                ),
            )
        reply = response.text
        if not reply or not reply.strip():
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI chưa tạo được câu trả lời. Vui lòng thử lại.",
            )
    except errors.APIError as exc:
        # Không đưa thông tin lỗi từ nhà cung cấp ra ngoài API.
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Không thể kết nối dịch vụ Gemini. Vui lòng thử lại sau.",
        ) from exc

    # Chỉ ghi lịch sử khi đã nhận được câu trả lời hợp lệ từ AI.
    db.add_all(
        [
            ChatMessage(user_id=user.id, sender="user", message=message.strip()),
            ChatMessage(user_id=user.id, sender="assistant", message=reply.strip()),
        ]
    )
    db.commit()
    return reply.strip()
