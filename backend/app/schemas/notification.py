from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class NotificationResponse(BaseModel):
    id: int
    title: str
    content: str
    is_read: bool
    notification_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)