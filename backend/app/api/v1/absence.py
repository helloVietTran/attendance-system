from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.services.absence_service import absence_service
from app.schemas.absence import AbsencePlanApprove, AbsencePlanCreate, AbsencePlanResponse, AbsenceResponse
from app.schemas.base import ResponseSchema
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

@router.patch("/plans/{plan_id}", response_model=ResponseSchema[AbsencePlanResponse])
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