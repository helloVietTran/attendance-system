import math

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.absence_tracker import AbsenceTrackerResponse
from app.services.absence_service import absence_service
from app.schemas.absence import AbsencePlanApprove, AbsencePlanCreate, AbsencePlanResponse, AbsenceResponse
from app.schemas.base import PaginationMetadata, PaginationResponse, ResponseSchema
from app.core.dependency import get_current_user, role_required
from app.models.employee import UserRole

router = APIRouter(prefix="/absences", tags=["Nghỉ phép & Kế hoạch nghỉ phép"])

@router.post("/plans", response_model=ResponseSchema[AbsencePlanResponse])
def create_plan(
    obj_in: AbsencePlanCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    plan = absence_service.create_absence_plan(db=db, obj_in=obj_in, emp_id=current_user["id"])
    return ResponseSchema(data=plan)

@router.get("/tracker", response_model=ResponseSchema[AbsenceTrackerResponse])
def get_employee_leave_balance(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Lấy quỹ phép năm của nhân viên (Public)"""
    balance = absence_service.get_leave_balance(db, emp_id=current_user["id"])
    return ResponseSchema(data=balance)

@router.get("/plans/me", response_model=ResponseSchema[List[AbsencePlanResponse]])
def get_my_absence_plans(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """API lấy danh sách kế hoạch nghỉ của chính tôi"""
    plans = absence_service.get_my_plans(db, emp_id=current_user["id"])
    return ResponseSchema(data=plans)

@router.get("/plans/all", response_model=PaginationResponse[AbsencePlanResponse])
def get_all_absence_plans_for_admin(
    status: str = Query(None),
    search: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    _ = Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))
):
    """API dành cho Admin/HR để lấy danh sách cần duyệt có phân trang"""
    skip = (page - 1) * limit
    
    plans, total_elements = absence_service.get_all_plans_admin(
        db, status=status, skip=skip, limit=limit, search=search
    )

    # Tính toán thông tin phân trang
    total_pages = math.ceil(total_elements / limit) if total_elements > 0 else 0
    
    pagination = PaginationMetadata(
        total_elements=total_elements,
        total_pages=total_pages,
        page=page,
        limit=limit
    )
    
    return PaginationResponse(
        status=1000,
        message="Thành công",
        data=plans,
        pagination=pagination
    )

@router.delete("/plans/{plan_id}")
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Nhân viên tự xóa đơn của mình khi còn ở trạng thái PENDING.
    """
    result = absence_service.delete_absence_plan(
        db, 
        plan_id=plan_id, 
        emp_id=current_user["id"]
    )
    return result

@router.patch("/plans/{plan_id}/status", response_model=ResponseSchema[AbsencePlanResponse])
def approve_absence_plan(
    plan_id: int, 
    obj_in: AbsencePlanApprove, 
    db: Session = Depends(get_db), 
    current_admin = Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))
):
    result = absence_service.approve_absence_plan(db, plan_id=plan_id, obj_in=obj_in, admin_id=current_admin["id"])
    return ResponseSchema(data=result)


@router.get("/employees/{employee_id}", response_model=ResponseSchema[List[AbsenceResponse]])
def read_employee_absences(employee_id: int, db: Session = Depends(get_db)):
    return ResponseSchema(data=absence_service.get_absences_by_employee(db, employee_id=employee_id))