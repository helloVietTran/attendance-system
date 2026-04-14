from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.core.dependency import get_current_user, role_required
from app.schemas.base import ResponseSchema, PaginationResponse
from app.db.session import get_db
from app.schemas.overtime_request import OvertimeApprove, OvertimeCreate, OvertimeResponse
from app.services.overtime_service import overtime_service
from app.models.employee import UserRole

router = APIRouter(prefix="/overtimes", tags=["Quản lý làm thêm giờ"])

@router.post("/", response_model=ResponseSchema[OvertimeResponse])
def request_ot(
    obj_in: OvertimeCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = overtime_service.create_request(db, obj_in, current_user["id"])
    return ResponseSchema(data=result)

@router.get("/all", response_model=PaginationResponse[OvertimeResponse])
def get_all_ot_requests(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _ = Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))
):
    data, metadata = overtime_service.get_all_requests_admin(
        db=db,
        month=month or datetime.now().month,
        year=year or datetime.now().year,
        status=status,
        search=search,
        page=page,
        limit=limit
    )
    return PaginationResponse(data=data, pagination=metadata)

@router.get("/me", response_model=ResponseSchema[List[OvertimeResponse]])
def get_my_ot_requests(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Lấy danh sách đơn OT của chính nhân viên.
    """
    now = datetime.now()
    
    search_month = month if month is not None else now.month
    search_year = year if year is not None else now.year
    
    result = overtime_service.get_my_requests(
        db=db, 
        emp_id=current_user["id"], 
        month=search_month, 
        year=search_year
    )
    return ResponseSchema(data=result)

@router.delete("/{ot_id}")
def cancel_ot(
    ot_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    overtime_service.delete_pending_request(db, ot_id, current_user["id"])
    return ResponseSchema(message="Đã hủy đơn OT thành công")

@router.get("/export")
def export_ot_requests(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    db: Session = Depends(get_db),
    current_admin = Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))
):
    """[Admin/HR] Xuất file excel danh sách OT"""
    output, file_name = overtime_service.export_overtime_excel(db, month, year)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
    )
    
@router.patch("/{ot_id}/status", response_model=ResponseSchema[OvertimeResponse])
def approve_overtime_request(
    ot_id: int,
    obj_in: OvertimeApprove,
    db: Session = Depends(get_db),
    current_admin = Depends(role_required([UserRole.ADMIN.value, UserRole.HR.value]))
):
    """Admin duyệt hoặc từ chối đơn OT"""
    result = overtime_service.approve_request(
        db, 
        ot_id=ot_id, 
        admin_id=current_admin["id"], 
        obj_in=obj_in
    )
    return ResponseSchema(data=result)

