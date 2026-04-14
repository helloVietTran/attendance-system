from pydantic import BaseModel
from datetime import time

class ShiftResponse(BaseModel):
    id: int
    name: str
    start_time: time
    end_time: time
    work_value: int
    is_active: bool

    class Config:
        from_attributes = True