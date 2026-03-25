from sqlalchemy.orm import Session
from app.models.system_setting import SystemSetting
from app.schemas.system_setting import SystemSettingKey
from fastapi import HTTPException

class SettingService:
    def __init__(self):
        self._cache = {}

    def get_setting_value(self, db: Session, key: SystemSettingKey, default=None):
        key_str = key.value if hasattr(key, 'value') else key
        
        # cache hit
        if key_str in self._cache:
            return self._cache[key_str]

        # cache miss
        setting = db.query(SystemSetting).filter(SystemSetting.key == key_str).first()
        if setting:
            self._cache[key_str] = setting.value 
            return setting.value
        
        return default

    def update_setting(self, db: Session, key: SystemSettingKey, value: str):
        key_str = key.value
        db_obj = db.query(SystemSetting).filter(SystemSetting.key == key_str).first()
        
        if not db_obj:
            raise HTTPException(status_code=404, detail=f"Key {key_str} không tồn tại")

        db_obj.value = value
        db.commit()
        
        self._cache[key_str] = value
        
        return db_obj

    def get_all_settings(self, db: Session):

        return db.query(SystemSetting).all()

    def preload_all_settings(self, db: Session):
        """Hàm này gọi khi khởi động Server để nạp toàn bộ vào RAM"""
        settings = db.query(SystemSetting).all()
        for s in settings:
            self._cache[s.key] = s.value

setting_service = SettingService()