from pydantic import BaseModel, Field

class PayrollCalculateRequest(BaseModel):
    closing_day: int = Field(20, ge=1, le=31, description="Ngày chốt công (1-31)")
    month: int = Field(..., ge=1, le=12, description="Tháng cần tính (1-12)")
    year: int = Field(..., ge=2000, description="Năm cần tính")