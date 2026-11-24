from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import deps
from app.models.user import User
from app.schemas.notification import (
    NotificationReadResponse,
    NotificationResponse,
    UnreadNotificationCount,
)
from app.services.notification_services import (
    count_unread_notifications,
    get_notifications,
    mark_notification_read,
)


router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/unread-count", response_model=UnreadNotificationCount, summary="Đếm thông báo chưa đọc")
def api_unread_notification_count(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return {"unread_count": count_unread_notifications(db, current_user)}


@router.get("", response_model=list[NotificationResponse], summary="Danh sách thông báo của tôi")
def api_get_notifications(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return get_notifications(db, current_user, limit, offset)


@router.patch("/{notification_id}/read", response_model=NotificationReadResponse, summary="Đánh dấu thông báo đã đọc")
def api_mark_notification_read(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return mark_notification_read(db, current_user, notification_id)
