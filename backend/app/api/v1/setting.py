from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.dependency import role_required
from app.models.employee import UserRole
from app.services.setting_service import setting_service
from app.schemas.system_setting import SystemSettingResponse, SystemSettingUpdate, SystemSettingKey
from app.schemas.base import ResponseSchema

router = APIRouter(prefix="/settings", tags=["System Settings"])

@router.get("/", response_model=ResponseSchema[List[SystemSettingResponse]])
def read_settings(db: Session = Depends(get_db)):
    return ResponseSchema(data=setting_service.get_all_settings(db))

@router.put("/", response_model=ResponseSchema[List[SystemSettingResponse]])
def update_multiple_settings(
    configs: List[SystemSettingUpdate],
    db: Session = Depends(get_db),
    _=Depends(role_required([UserRole.ADMIN.value]))
):
    """Cập nhật hàng loạt các thông số cấu hình hệ thống"""
    updated_items = setting_service.update_multiple_settings(db, configs=configs)
    return ResponseSchema(data=updated_items)

@router.patch("/{key}", response_model=ResponseSchema[SystemSettingResponse])
def update_system_config(
    key: SystemSettingKey,
    obj_in: SystemSettingUpdate,
    db: Session = Depends(get_db),
    _=Depends(role_required([UserRole.ADMIN.value]))
):
    """Cập nhật một thông số cấu hình cụ thể"""
    return ResponseSchema(data=setting_service.update_setting(db, key=key, value=obj_in.value))
