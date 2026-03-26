from sqlalchemy.orm import Session
from sqlalchemy import extract, and_
from app.models.notification import Notification

class NotificationService:
    def get_employee_notifications(
        self, db: Session, employee_id: int, month: int, year: int
    ):
        base_filters = and_(
            Notification.employee_id == employee_id,
            extract('month', Notification.created_at) == month,
            extract('year', Notification.created_at) == year
        )

        # Đếm tổng số thông báo trong tháng đó
        total_count = db.query(Notification).filter(base_filters).count()

        # Đếm số thông báo CHƯA ĐỌC trong tháng đó
        unread_count = db.query(Notification).filter(
            base_filters, 
            Notification.is_read == False
        ).count()

        items = db.query(Notification).filter(base_filters)\
            .order_by(Notification.created_at.desc()).all()

        return {
            "total_count": total_count,
            "unread_count": unread_count,
            "items": items
        }

    def mark_as_read_bulk(self, db: Session, notification_ids_str: str):
        if not notification_ids_str:
            return 0

        # 1. Chuyển chuỗi "1,2,3" thành list [1, 2, 3]
        try:
            id_list = [int(id.strip()) for id in notification_ids_str.split(",") if id.strip()]
        except ValueError:
            return 0

        updated_count = db.query(Notification).filter(
            Notification.id.in_(id_list)
        ).update({Notification.is_read: True}, synchronize_session=False)

        db.commit()
        return updated_count

notification_service = NotificationService()