from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.dependency import get_current_user, role_required
from app.db.session import get_db
from app.services.fix_attendance_service import fix_attendance_service
from app.schemas.attendance_correction import CorrectionCreate, CorrectionResponse
from app.schemas.base import ResponseSchema
from app.models.employee import UserRole
from app.models.absence import ApprovalStatus

router = APIRouter(prefix="/fix-attendance-requests", tags=["Yêu cầu sửa công"])

@router.post("/", response_model=ResponseSchema[CorrectionResponse])
def request_fix_attendance(
    obj_in: CorrectionCreate, 
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    result = fix_attendance_service.create_correction_request(db, current_user["id"], obj_in)
    return ResponseSchema(data=result)


from datetime import datetime
from app.schemas.base import PaginationResponse # Đảm bảo đã import đúng schema phân trang

@router.get("/all", response_model=PaginationResponse[CorrectionResponse])
def get_all_fix_attendance_admin(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _ = Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))
):
    """API dành cho Admin/HR quản lý toàn bộ yêu cầu sửa công"""
    data, metadata = fix_attendance_service.get_all_corrections_admin(
        db=db,
        month=month or datetime.now().month,
        year=year or datetime.now().year,
        status=status,
        search=search,
        page=page,
        limit=limit
    )
    return PaginationResponse(data=data, pagination=metadata)

@router.get("/my-requests", response_model=ResponseSchema[List[CorrectionResponse]])
def get_my_fix_attendance(
    month: Optional[int] = None,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user_id = current_user["id"]
    
    result = fix_attendance_service.get_my_corrections(
        db, 
        employee_id=user_id, 
        month=month, 
        year=year
    )
    return ResponseSchema(data=result)

@router.put("/{fix_id}/status", response_model=ResponseSchema[CorrectionResponse])
def update_fix_request_status(
    fix_id: int, 
    status: ApprovalStatus,
    db: Session = Depends(get_db),
    current_admin = Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))
):
    result = fix_attendance_service.update_correction_status(
        db, 
        correction_id=fix_id, 
        admin_id=current_admin["id"],
        status=status
    )
    return ResponseSchema(data=result)