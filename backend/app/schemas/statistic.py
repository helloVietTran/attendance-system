from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time
from decimal import Decimal

class HardWorkingEmployee(BaseModel):
    employee_id: int
    full_name: str
    total_offence_minutes: int
    total_absences: int

class LateLeaverEmployee(BaseModel):
    employee_id: int
    full_name: str
    last_check_out: Optional[time]
    on_date: Optional[date]

class AttendanceRatio(BaseModel):
    on_time_percentage: float
    late_early_percentage: float
    absent_percentage: float

class DashboardStatisticResponse(BaseModel):
    top_hard_working: List[HardWorkingEmployee]
    top_late_leavers: List[LateLeaverEmployee]
    ratios: AttendanceRatio