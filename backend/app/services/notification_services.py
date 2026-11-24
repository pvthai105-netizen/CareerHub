from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.notifications import Notification
from app.models.user import User


def count_unread_notifications(db: Session, user: User) -> int:
    return (
        db.query(Notification)
        .filter(Notification.user_id == user.id, Notification.is_read.is_(False))
        .count()
    )


def get_notifications(db: Session, user: User, limit: int, offset: int) -> list[Notification]:
    return (
        db.query(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc(), Notification.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def mark_notification_read(db: Session, user: User, notification_id: int) -> Notification:
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == user.id)
        .first()
    )
    if notification is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy thông báo")

    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification
