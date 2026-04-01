import math
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from fastapi import HTTPException

from app.models.employee import Employee

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

    def search_employees(self, db: Session, keyword: str, page: int, limit: int):
        """
        Tìm kiếm nhân viên theo Name, Email hoặc ID và phân trang
        """
        query = db.query(Employee).options(joinedload(Employee.shift))

        if keyword:
            is_digit = keyword.isdigit()
            search_filter = or_(
                Employee.full_name.ilike(f"%{keyword}%"),
                Employee.email.ilike(f"%{keyword}%")
            )
            if is_digit:
                search_filter = or_(search_filter, Employee.id == int(keyword))
            
            query = query.filter(search_filter)

        total_elements = query.count()
        total_pages = math.ceil(total_elements / limit) if total_elements > 0 else 0
        offset = (page - 1) * limit

        employees = query.offset(offset).limit(limit).all()

        pagination = {
            "total_elements": total_elements,
            "total_pages": total_pages,
            "page": page,
            "limit": limit
        }

        return employees, pagination

employee_service = EmployeeService()