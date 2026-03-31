import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import date, time
from decimal import Decimal

from app.main import app
from app.db.session import Base, get_db
from app.core.dependencies import get_current_user

from app.models.employee import Employee, UserRole
from app.models.shift import Shift
from app.models.absence import AbsenceType


# ========================
# DATABASE (SQLite memory)
# ========================
SQLALCHEMY_DATABASE_URL = "sqlite+pysqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(bind=engine)


# ========================
# OVERRIDE DB
# ========================
@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# ========================
# OVERRIDE AUTH (QUAN TRỌNG)
# ========================
@pytest.fixture
def auth_client(client):
    def override_user():
        return {"id": 1, "role": "EMPLOYEE"}

    app.dependency_overrides[get_current_user] = override_user

    yield client

    app.dependency_overrides.clear()


# ========================
# TEST DATA FACTORIES
# ========================
@pytest.fixture
def create_shifts(db):
    def _create():
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
        return shifts

    return _create


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
def create_absence_types(db):
    def _create():
        types = [
            AbsenceType(
                id=1,
                name="Nghỉ phép năm",
                code="VAC",
                is_paid=1
            ),
            AbsenceType(
                id=2,
                name="Nghỉ ốm",
                code="SICK",
                is_paid=1
            ),
        ]
        db.add_all(types)
        db.commit()
        return types

    return _create