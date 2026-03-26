from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class NotificationResponse(BaseModel):
    id: int
    title: str
    content: str
    is_read: bool
    notification_type: str
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationListWithCount(BaseModel):
    total_count: int
    unread_count: int
    items: List[NotificationResponse]