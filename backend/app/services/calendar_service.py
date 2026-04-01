from datetime import date, timedelta

from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.vacation import Vacation
from app.schemas.vacation import VacationCreate, VacationUpdate
from app.models.work_compensation import WorkCompensation

class CalendarService:
    def create_vacation(self, db: Session, obj_in: VacationCreate):
        if obj_in.end_date < obj_in.start_date:
            raise HTTPException(status_code=400, detail="Ngày kết thúc không được trước ngày bắt đầu")
        
        db_obj = Vacation(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_vacation(self, db: Session, vacation_id: int, obj_in: VacationUpdate):
        db_obj = db.query(Vacation).filter(Vacation.id == vacation_id).first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Không tìm thấy ngày nghỉ")
        
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete_vacation(self, db: Session, vacation_id: int):
        db_obj = db.query(Vacation).filter(Vacation.id == vacation_id).first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Không tìm thấy ngày nghỉ")
        db.delete(db_obj)
        db.commit()
        return {"message": "Xóa thành công"}
        
    def get_vacations(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Vacation).offset(skip).limit(limit).all()
    
    def get_vacation_by_id(self, db: Session, vacation_id: int):
        vacation = db.query(Vacation).filter(Vacation.id == vacation_id).first()
        if not vacation:
            raise HTTPException(status_code=404, detail="Không tìm thấy ngày nghỉ này")
        return vacation
    
    def get_working_days_list(self, db: Session, start: date, end: date):
        ''' Trả về danh sách các ngày làm việc trong khoảng thời gian từ start đến end, 
        đã loại trừ các ngày nghỉ và thêm vào các ngày làm bù '''
        days = []
        curr = start
        
        # danh sách ngày làm bù
        compensation_dates = {
            c.compensate_date for c in db.query(WorkCompensation.compensate_date).filter(
                WorkCompensation.compensate_date >= start,
                WorkCompensation.compensate_date <= end
            ).all()
        }

        while curr <= end:
            if curr.weekday() < 5:
                is_holiday = db.query(Vacation).filter(
                    or_(
                        # Nghỉ cố định theo năm cụ thể vd: nghỉ do mưa lũ
                        and_(
                            Vacation.is_recurring == False,
                            Vacation.start_date <= curr,
                            Vacation.end_date >= curr
                        ),
                        # Nghỉ lễ lặp lại hàng năm
                        and_(
                            Vacation.is_recurring == True,
                            func.date_format(Vacation.start_date, '%m-%d') <= curr.strftime('%m-%d'),
                            func.date_format(Vacation.end_date, '%m-%d') >= curr.strftime('%m-%d')
                        )
                    )
                ).first()

                if not is_holiday:
                    days.append(curr)

            # cuối tuần (T7, CN)
            else:
                if curr in compensation_dates:
                    days.append(curr)

            curr += timedelta(days=1)
            
        return days
    
    def create_compensation(self, db: Session, obj_in: WorkCompensationCreate):
        # Kiểm tra trùng lặp ngày làm bù
        existing = db.query(WorkCompensation).filter(
            WorkCompensation.compensate_date == obj_in.compensate_date
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Ngày làm bù này đã tồn tại.")
        
        db_obj = WorkCompensation(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_compensation(self, db: Session, comp_id: int, obj_in: WorkCompensationUpdate):
        db_obj = db.query(WorkCompensation).filter(WorkCompensation.id == comp_id).first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Không tìm thấy ngày làm bù.")
        
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete_compensation(self, db: Session, comp_id: int):
        db_obj = db.query(WorkCompensation).filter(WorkCompensation.id == comp_id).first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Không tìm thấy ngày làm bù.")
        
        db.delete(db_obj)
        db.commit()
        return {"status": "success", "message": "Đã xóa ngày làm bù."}

    def get_compensations(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(WorkCompensation).offset(skip).limit(limit).all()

calendar_service = CalendarService()