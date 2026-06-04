from datetime import date, timedelta

from sqlalchemy import func, and_, or_
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.vacation import Vacation
from app.schemas.vacation import VacationCreate, VacationUpdate
from app.models.work_compensation import WorkCompensation
from app.schemas.work_compensation import WorkCompensationCreate, WorkCompensationUpdate

class CalendarService:
    def create_vacation(self, db: Session, obj_in: VacationCreate):
        
        overlap_check = db.query(Vacation).filter(
            and_(
                Vacation.start_date <= obj_in.end_date,
                Vacation.end_date >= obj_in.start_date
            )
        ).first()

        if overlap_check:
            raise HTTPException(
                status_code=400, 
                detail=f"Thời gian này bị trùng với ngày nghỉ lễ: {overlap_check.title} ({overlap_check.start_date} -> {overlap_check.end_date})"
            )

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
        
        new_start = update_data.get("start_date", db_obj.start_date)
        new_end = update_data.get("end_date", db_obj.end_date)

        if new_end < new_start:
            raise HTTPException(status_code=400, detail="Ngày kết thúc không được trước ngày bắt đầu")

        overlap_check = db.query(Vacation).filter(
            and_(
                Vacation.id != vacation_id,
                Vacation.start_date <= new_end,
                Vacation.end_date >= new_start
            )
        ).first()

        if overlap_check:
            raise HTTPException(
                status_code=400, 
                detail=f"Cập nhật thất bại! Thời gian bị trùng với: {overlap_check.name}"
            )

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
        if obj_in.compensate_date.weekday() < 5:
            raise HTTPException(
                status_code=400, 
                detail="Ngày làm bù phải được ấn định vào Thứ Bảy hoặc Chủ Nhật."
            )

        # 2. Kiểm tra ngày làm bù không được nằm trong danh sách ngày nghỉ (Vacation)
        holiday_conflict = db.query(Vacation).filter(
            and_(
                Vacation.start_date <= obj_in.compensate_date,
                Vacation.end_date >= obj_in.compensate_date
            )
        ).first()

        if holiday_conflict:
            raise HTTPException(
                status_code=400, 
                detail=f"Không thể làm bù vào ngày này vì đang trùng với lịch nghỉ: {holiday_conflict.title}"
            )

        existing = db.query(WorkCompensation).filter(
            WorkCompensation.compensate_date == obj_in.compensate_date
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="Ngày làm bù này đã có trong hệ thống.")
        
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
        
        if "compensate_date" in update_data:
            new_date = update_data["compensate_date"]
            
            if new_date.weekday() < 5:
                raise HTTPException(status_code=400, detail="Ngày làm bù mới phải là Thứ Bảy hoặc Chủ Nhật.")
                
            holiday_conflict = db.query(Vacation).filter(
                and_(
                    Vacation.start_date <= new_date,
                    Vacation.end_date >= new_date
                )
            ).first()
            if holiday_conflict:
                raise HTTPException(status_code=400, detail=f"Ngày mới trùng lịch nghỉ: {holiday_conflict.title}")

            existing = db.query(WorkCompensation).filter(
                and_(
                    WorkCompensation.compensate_date == new_date,
                    WorkCompensation.id != comp_id
                )
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail="Ngày làm bù này đã tồn tại.")

        # Tiến hành cập nhật
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