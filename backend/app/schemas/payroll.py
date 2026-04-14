from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date

class PayrollCalculateRequest(BaseModel):
    closing_day: int = Field(20, ge=1, le=31, description="Ngày chốt công (1-31)")
    month: int = Field(..., ge=1, le=12, description="Tháng cần tính (1-12)")
    year: int = Field(..., ge=2000, description="Năm cần tính")
    
    # app/schemas/payroll.py

class MonthlyWorkReportResponse(BaseModel):
    id: int
    employee_id: int
    period_start: date
    period_end: date
    standard_work_minutes: int
    lack_minutes: int
    estimated_minutes: int
    actual_work_days: int
    paid_leave_days: int
    unpaid_leave_days: int
    
    employee_name: Optional[str] = None
    department_id: Optional[int] = None
    email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)