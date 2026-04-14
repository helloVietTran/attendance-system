from datetime import date
from fastapi import HTTPException
import pytest

from app.schemas.attendance_correction import CorrectionCreate
from app.services.fix_attendance_service import fix_attendance_service
from app.models.absence import ApprovalStatus

def test_create_correction_request_success(db, create_employee, create_daily_report):
    emp = create_employee(id=99)
    
    target_date = date(2024, 3, 20)
    
    create_daily_report(
        employee_id=emp.id,
        work_date=target_date,
        late_arrive=120,
        lack_minutes=120,
        work_time=360 # 6 tiếng
    )
    
    obj_in = CorrectionCreate(
        work_date=target_date,
        requested_check_in="08:00",
        requested_check_out="17:00",
        reason="Quên quẹt thẻ"
    )

    result = fix_attendance_service.create_correction_request(db, employee_id=emp.id, obj_in=obj_in)
    
    assert result.employee_id == emp.id
    assert result.status == ApprovalStatus.PENDING
    assert result.work_date == target_date
    
def test_create_request_exceed_limit(db, create_employee, create_correction_record):
    emp = create_employee(id=10)
    today = date.today()
    
    # Tạo 3 bản ghi (đã đạt giới hạn)
    for i in range(3):
        create_correction_record(employee_id=emp.id, work_date=date(today.year, today.month, i + 1))
    
    obj_in = CorrectionCreate(
        work_date=today,
        requested_check_in="08:00",
        requested_check_out="17:00",
        reason="Đơn thứ 4"
    )
    
    with pytest.raises(HTTPException) as exc:
        fix_attendance_service.create_correction_request(db, employee_id=emp.id, obj_in=obj_in)
    
    assert exc.value.status_code == 400
    assert "hết lượt" in exc.value.detail
    
def test_create_request_no_lack_minutes(db, create_employee, create_daily_report):
    emp = create_employee(id=11)
    target_date = date(2024, 3, 20) # tạo ngày tường minh, tránh lỗi do sql lite xử lý khác mysql
    
    create_daily_report(employee_id=emp.id, work_date=target_date, lack_minutes=0)
    
    obj_in = CorrectionCreate(
        work_date=target_date,
        requested_check_in="08:00",
        requested_check_out="17:00",
        reason="Sửa đủ ngày công"
    )
    
    with pytest.raises(HTTPException) as exc:
        fix_attendance_service.create_correction_request(db, employee_id=emp.id, obj_in=obj_in)
    
    assert exc.value.status_code == 400
    assert "đã đủ công" in exc.value.detail