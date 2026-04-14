from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.dependency import get_current_user
from app.db.session import get_db
from app.services.notification_service import notification_service
from app.schemas.notification import NotificationResponse
from app.schemas.base import PaginationResponse, ResponseSchema, PaginationMetadata

router = APIRouter(prefix="/notifications", tags=["Thông báo"])

@router.get("/me", response_model=PaginationResponse[NotificationResponse])
def get_notifications(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(default=datetime.now().year),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    items, total, pages = notification_service.get_employee_notifications(
        db, current_user["id"], month, year, page, limit
    )

    return PaginationResponse(
        data=items,
        pagination=PaginationMetadata(
            total_elements=total,
            total_pages=pages,
            page=page,
            limit=limit
        )
    )

@router.patch("/mark-read", response_model=ResponseSchema[None])
def mark_notifications_as_read(
    ids: str = Query(..., description="Chuỗi ID thông báo, ví dụ: '1,2,5'"), 
    db: Session = Depends(get_db),
    _ = Depends(get_current_user)
):
    """
    API đánh dấu đã đọc cho nhiều thông báo cùng lúc.
    Truyền vào query param: ?ids=1,2,3
    """
    count = notification_service.mark_as_read_bulk(db, ids)

    return ResponseSchema(message=f"Đã đánh dấu đọc cho {count} thông báo.")