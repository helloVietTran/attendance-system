from pydantic import BaseModel
from datetime import date
from typing import Optional

class MonthlyReportCreate(BaseModel):
    employee_id: int
    period_start: date
    period_end: date
    work_minutes: int
    late_minutes: int
    early_minutes: int
    lack_minutes: int
    over_time_minutes: int
    estimated_minutes: int  # Số phút tạm tính cho những ngày chưa đến