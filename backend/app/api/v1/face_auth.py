from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List
import cv2
import numpy as np
from datetime import datetime

from app.db.session import get_db
from app.models.employee import Employee
from app.models.face_template import FaceTemplate
from app.services.face_recognition_service import face_service
from app.services.attendance_service import attendance_service
from app.schemas.attendance_log import AttendanceCreate, AttendanceLogResponse
from app.schemas.base import ResponseSchema

router = APIRouter(prefix="/face-auth", tags=["Face Recognition"])

@router.post("/register/{employee_id}")
async def register_face_samples(
    employee_id: int, 
    files: List[UploadFile] = File(...), 
    db: Session = Depends(get_db)
):
    """HR đăng ký khuôn mặt cho nhân viên từ 20 ảnh mẫu"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Nhân viên không tồn tại")

    if len(files) < 10:
        raise HTTPException(status_code=400, detail="Cần ít nhất 10-20 ảnh mẫu để đảm bảo độ chính xác.")

    # Kiểm tra xem nhân viên đã có face template chưa
    existing_template = db.query(FaceTemplate).filter(FaceTemplate.employee_id == employee_id).first()
    if existing_template:
        raise HTTPException(status_code=400, detail=f"Nhân viên {employee.full_name} đã có khuôn mặt đăng ký. Không thể đăng ký lại.")

    image_data_list = [await file.read() for file in files]

    centroid_vec = face_service.process_multiple_images(image_data_list)
    
    if not centroid_vec:
        raise HTTPException(status_code=400, detail="Không thể nhận diện khuôn mặt rõ ràng từ các ảnh gửi lên.")

    # Kiểm tra xem khuôn mặt này có giống với template nào đã có không
    similar_employee_id = face_service.check_face_similarity(centroid_vec, db)
    if similar_employee_id:
        similar_employee = db.query(Employee).filter(Employee.id == similar_employee_id).first()
        raise HTTPException(status_code=400, detail=f"Khuôn mặt này đã được đăng ký cho nhân viên {similar_employee.full_name if similar_employee else 'khác'}. Không thể đăng ký trùng lặp.")

    # Tạo template mới
    new_template = FaceTemplate(employee_id=employee_id, face_encoding=centroid_vec)
    db.add(new_template)
    
    db.commit()
    
    face_service.clear_cache()
    
    return {"message": f"Đã đăng ký thành công cho {employee.full_name}"}


@router.post("/attendance", response_model=ResponseSchema[AttendanceLogResponse])
async def face_attendance(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    img_bytes = await file.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    faces = face_service.app.get(img)
    if not faces:
        raise HTTPException(status_code=400, detail="Không nhận diện được khuôn mặt.")
    
    face = max(faces, key=lambda x: (x.bbox[2]-x.bbox[0])*(x.bbox[3]-x.bbox[1]))
    # Chuẩn hóa vector input
    current_vec = face.embedding / np.linalg.norm(face.embedding)

    # Lấy cache (Dạng dict chứa matrix)
    cache_data = face_service.get_known_templates(db)
    
    # So khớp
    matched_emp_id = face_service.verify_face(current_vec, cache_data)
    
    if not matched_emp_id:
        raise HTTPException(status_code=401, detail="Không khớp khuôn mặt.")
    
    # tạo log
    employee = db.query(Employee).options(joinedload(Employee.shift)).filter(
        Employee.id == matched_emp_id
    ).first()

    if not employee or not employee.shift:
        raise HTTPException(status_code=400, detail="Nhân viên chưa được cấu hình ca làm việc.")
    
    now = datetime.now()
    
    attendance_data = AttendanceCreate(
        employee_id=matched_emp_id,
        log_date=now.date(),
        shift_start=employee.shift.start_time,
        shift_end=employee.shift.end_time,
        checked_time=now.time()
    )

    result = attendance_service.ingest_log(db, attendance_data)
    
    return ResponseSchema(data=result)