from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.statistic_service import statistic_service
from app.schemas.statistic import DashboardStatisticResponse
from app.schemas.base import ResponseSchema
from app.core.dependency import role_required
from app.models.employee import UserRole

router = APIRouter(prefix="/statistics", tags=["Thống kê"])

@router.get("/dashboard", response_model=ResponseSchema[DashboardStatisticResponse])
def get_admin_dashboard_stats(
    months: int = Query(1, ge=1, le=12, description="Số tháng thống kê ngược về trước"),
    db: Session = Depends(get_db),
    _ = Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))
):
    """[Admin/HR] Lấy thống kê tổng quan cho Dashboard"""
    stats = statistic_service.get_dashboard_stats(db, months)
    return ResponseSchema(data=stats)