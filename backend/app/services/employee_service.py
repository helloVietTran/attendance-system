from sqlalchemy.orm import Session, joinedload
from app.models.employee import Employee
from fastapi import HTTPException

class EmployeeService:
    def get_employee_with_shift(self, db: Session, employee_id: int):
        """
        Lấy thông tin nhân viên và JOIN với bảng Shift để lấy giờ làm
        """
        employee = db.query(Employee)\
            .options(joinedload(Employee.shift))\
            .filter(Employee.id == employee_id)\
            .first()
            
        if not employee:
            raise HTTPException(status_code=404, detail="Không tìm thấy nhân viên")
            
        return employee

employee_service = EmployeeService()