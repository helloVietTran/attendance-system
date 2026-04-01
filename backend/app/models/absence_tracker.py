from sqlalchemy import Boolean, Column, Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class AbsenceTracker(Base):
    """Quản lý quỹ phép năm và cộng dồn"""
    __tablename__ = "absence_trackers"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), unique=True, nullable=False)

    # nghỉ phép năm nay
    current_year_total = Column(Integer, default=14, nullable=False)
    current_year_used = Column(Integer, default=0, nullable=False)

    # nghỉ phép dư từ năm ngoái
    carried_over_from_last_year = Column(Integer, default=0, nullable=False)
    carried_over_used = Column(Integer, default=0, nullable=False)

    last_reset_year = Column(Integer, default=func.extract('year', func.now()))
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    @property
    def total_remaining_leave(self):
        """Tổng số ngày phép còn lại (Năm ngoái + Năm nay)"""
        remaining_last_year = max(0, self.carried_over_from_last_year - self.carried_over_used)
        remaining_current_year = max(0, self.current_year_total - self.current_year_used)
        return remaining_last_year + remaining_current_year

    def deduct_leave(self, days: int):
        """
        Trừ số ngày nghỉ phép. 
        Đảm bảo không trừ quá số ngày đang có (dừng lại ở mức dùng hết sạch).
        """
        if days <= 0:
            return

        avail_last_year = max(0, self.carried_over_from_last_year - self.carried_over_used)
        
        if avail_last_year >= days:
            self.carried_over_used += days
        else:
            # Nếu không đủ, dùng hết sạch phép cũ của năm ngoái
            self.carried_over_used = self.carried_over_from_last_year
            
            # Tính phần còn thiếu cần trừ vào năm nay
            remaining_needed = days - avail_last_year
            avail_current_year = max(0, self.current_year_total - self.current_year_used)
            
            actual_deduct_current = min(remaining_needed, avail_current_year)
            self.current_year_used += actual_deduct_current


    def reset_for_new_year(self):
        """
        Logic chuyển giao khi sang năm mới:
        Lấy phép dư năm nay chuyển thành carried_over của năm sau.
        """
        remaining_current = self.current_year_total - self.current_year_used
        # Phép cũ của năm kia sẽ bị mất hoàn toàn (chỉ giữ lại phép của năm vừa rồi)
        self.carried_over_from_last_year = max(0, remaining_current)
        self.carried_over_used = 0
        self.current_year_used = 0