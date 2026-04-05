from sqlalchemy.orm import Session
from sqlalchemy import extract, and_
from math import ceil

from app.models.notification import Notification

class NotificationService:
    def get_employee_notifications(
    self, db: Session, employee_id: int, month: int, year: int, page: int = 1, limit: int = 10):
        base_filters = and_(
            Notification.employee_id == employee_id,
            extract('month', Notification.created_at) == month,
            extract('year', Notification.created_at) == year
        )

        total_elements = db.query(Notification).filter(base_filters).count()

        offset = (page - 1) * limit
        total_pages = ceil(total_elements / limit) if total_elements > 0 else 0

        items = db.query(Notification).filter(base_filters)\
            .order_by(Notification.created_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()

        return items, total_elements, total_pages

    def mark_as_read_bulk(self, db: Session, notification_ids_str: str):
        if not notification_ids_str:
            return 0

        # chuyển chuỗi "1,2,3" thành list [1, 2, 3]
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