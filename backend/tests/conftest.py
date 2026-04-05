import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import date, time
from decimal import Decimal

from app.main import app
from app.db.session import Base, get_db
from app.core.dependency import get_current_user

from app.models.shift_change_request import ShiftChangeRequest, RequestStatus
from app.models.employee import Employee, UserRole
from app.models.shift import Shift
from app.models.absence import ApprovalStatus
from app.models.system_setting import SystemSetting
from app.models.daily_work_report import DailyWorkReport
from app.models.attendance_correction import AttendanceCorrection

SQLALCHEMY_DATABASE_URL = "sqlite+pysqlite:///:memory:"

@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine


@pytest.fixture(scope="session")
def setup_database(engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ========================
# SEED CONFIG DATA
# ========================
@pytest.fixture(scope="session")
def seed_system_settings(setup_database, engine):
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    settings = [
        SystemSetting(
            key="lunch_break_start",
            value="12:00",
            description="Giờ bắt đầu nghỉ trưa"
        ),
        SystemSetting(
            key="lunch_break_end",
            value="13:00",
            description="Giờ kết thúc nghỉ trưa"
        ),
        SystemSetting(
            key="annual_paid_leave_days",
            value="14",
            description="Số ngày nghỉ phép hưởng lương định mức hàng năm"
        ),
        SystemSetting(
            key="maternity_leave_months",
            value="6",
            description="Thời gian nghỉ thai sản tính theo tháng"
        ),
        SystemSetting(
            key="max_attendance_correction_per_month",
            value="3",
            description="Số lần tối đa nhân viên được phép gửi yêu cầu chỉnh sửa chấm công trong một tháng"
        ),
    ]

    db.add_all(settings)
    db.commit()
    db.close()
    
@pytest.fixture(scope="session")
def seed_config_data(setup_database, engine):
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    shifts = [
        Shift(
            id=1,
            name="Ca Hành Chính 1",
            start_time=time(8, 30),
            end_time=time(17, 30),
            work_value=1,
            is_active=1
        ),
        Shift(
            id=2,
            name="Ca Hành Chính 2",
            start_time=time(9, 0),
            end_time=time(18, 0),
            work_value=1,
            is_active=1
        ),
    ]

    db.add_all(shifts)
    db.commit()
    db.close()


# ========================
# DB PER TEST (rollback)
# ========================
@pytest.fixture(scope="function")
def db(engine, seed_config_data):
    connection = engine.connect()
    transaction = connection.begin()

    SessionLocal = sessionmaker(bind=connection)
    db = SessionLocal()

    yield db

    db.close()
    transaction.rollback()
    connection.close()


# ========================
# CLIENT
# ========================
@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# ========================
# AUTH OVERRIDE
# ========================
@pytest.fixture
def auth_client(client):
    def override_user():
        return {"id": 1, "role": "employee"}

    app.dependency_overrides[get_current_user] = override_user

    yield client

    app.dependency_overrides.clear()

@pytest.fixture
def admin_client():
    """
    Trả về client giả lập user ADMIN
    """
    # override get_current_user trả về admin
    def override_get_admin_user():
        return {"id": 1, "role": "admin"}

    app.dependency_overrides[get_current_user] = override_get_admin_user

    # **Tạo client sau khi override**
    with TestClient(app) as client:
        yield client

    # Xóa override sau test
    app.dependency_overrides.clear()

# ========================
# TEST DATA (function scope)
# ========================
@pytest.fixture
def create_employee(db):
    def _create(id=1):
        emp = Employee(
            id=id,
            full_name="Test User",
            age=25,
            email=f"user{id}@test.com",
            department_id=1,
            password_hash="hashed",
            dob=date(2000, 1, 1),
            salary=Decimal("1000.00"),
            shift_id=1,
            role=UserRole.EMPLOYEE
        )
        db.add(emp)
        db.commit()
        return emp

    return _create

@pytest.fixture
def create_shift_request(db):
    def _create(
        employee_id=1,
        old_shift_id=1,
        new_shift_id=2,
        target_month=None,
        target_year=None,
        status=RequestStatus.PENDING,
    ):
        today = date.today()

        if not target_month:
            target_month = today.month + 1 if today.month < 12 else 1
        if not target_year:
            target_year = today.year if today.month < 12 else today.year + 1

        req = ShiftChangeRequest(
            employee_id=employee_id,
            old_shift_id=old_shift_id,
            new_shift_id=new_shift_id,
            target_month=target_month,
            target_year=target_year,
            status=status,
        )

        db.add(req)
        db.commit()
        db.refresh(req)
        return req

    return _create

@pytest.fixture
def create_daily_report(db):
    """
    Fixture tạo báo cáo công nhật giả cho nhân viên
    """
    def _create(
        employee_id=1,
        work_date=None,
        check_in=time(9, 15),
        check_out=time(17, 30),
        late_arrive=45,
        lack_minutes=45,
        work_time=435,
        in_office=495
    ):
        if work_date is None:
            work_date = date.today()

        report = DailyWorkReport(
            employee_id=employee_id,
            work_date=work_date,
            check_in=check_in,
            check_out=check_out,
            late_arrive_minutes=late_arrive,
            leave_early_minutes=0,
            lack_minutes=lack_minutes,
            overtime_minutes=0,
            in_office_minutes=in_office,
            work_time_minutes=work_time,
            note="Dữ liệu test"
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    return _create

@pytest.fixture
def create_correction_record(db):
    """
    Fixture tạo yêu cầu chỉnh sửa công giả để phục vụ test tính năng Duyệt hoặc đếm lượt
    """
    def _create(employee_id=1, work_date=None, status=ApprovalStatus.PENDING):
        if not work_date:
            work_date = date.today()
        record = AttendanceCorrection(
            employee_id=employee_id,
            work_date=work_date,
            requested_check_in=time(8, 0),
            requested_check_out=time(17, 0),
            reason="Lỗi quẹt thẻ test",
            status=status
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    return _create