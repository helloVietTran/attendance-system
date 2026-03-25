from pydantic import BaseModel
from typing import Optional

class SettingBase(BaseModel):
    key: str
    value: str
    description: Optional[str] = None

class SettingResponse(SettingBase):
    id: int
    class Config:
        from_attributes = True