from datetime import date
from app.models.absence import ApprovalStatus


def test_read_employee_absences_success(client, create_employee, create_absence_record):
    create_employee(id=1)
    absence = create_absence_record(
        employee_id=1,
        absence_type_id=1,
        start_date=date(2026, 4, 1),
        end_date=date(2026, 4, 2),
        reason="Nghỉ phép năm",
        status=ApprovalStatus.PENDING,
    )

    response = client.get("/api/v1/absences/employees/1/absences")

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == 1000
    assert body["message"] == "OK"

    assert len(body["data"]) == 1
    assert body["data"][0]["id"] == absence.id
    assert body["data"][0]["status"] == "pending"
    assert body["data"][0]["absence_type_id"] == 1


def test_create_absence_success(auth_client, create_employee):
    create_employee(id=1)

    payload = {
        "absence_type_id": 1,
        "start_date": "2026-04-10",
        "end_date": "2026-04-12",
        "reason": "Đi khám bệnh",
    }

    response = auth_client.post("/api/v1/absences/", json=payload)

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == 1000
    assert body["message"] == "OK"
    assert body["data"]["status"] == "pending"
    assert body["data"]["absence_type_id"] == 1


def test_create_absence_employee_not_found(auth_client):
    payload = {
        "absence_type_id": 1,
        "start_date": "2026-04-10",
        "end_date": "2026-04-12",
    }

    response = auth_client.post("/api/v1/absences/", json=payload)

    assert response.status_code == 404
    body = response.json()

    assert body["status"] == 404
    assert body["message"] == "Nhân viên không tồn tại"
    assert body["data"] is None


def test_create_absence_overlap(auth_client, create_employee, create_absence_record):
    create_employee(id=1)

    create_absence_record(
        employee_id=1,
        absence_type_id=1,
        start_date=date(2026, 4, 10),
        end_date=date(2026, 4, 12),
        status=ApprovalStatus.PENDING,
    )

    payload = {
        "absence_type_id": 1,
        "start_date": "2026-04-11",
        "end_date": "2026-04-13",
    }

    response = auth_client.post("/api/v1/absences/", json=payload)

    assert response.status_code == 400
    body = response.json()

    assert body["status"] == 400
    assert "Nhân viên đã có đơn nghỉ phép" in body["message"]
    assert body["data"] is None


def test_delete_pending_absence_success(auth_client, create_employee, create_absence_record):
    create_employee(id=1)

    absence = create_absence_record(employee_id=1)

    response = auth_client.delete(f"/api/v1/absences/{absence.id}")

    assert response.status_code == 200
    body = response.json()

    assert body["id"] == absence.id


def test_delete_absence_not_found(auth_client, create_employee):
    create_employee(id=1)

    response = auth_client.delete("/api/v1/absences/999")

    assert response.status_code == 404
    body = response.json()

    assert body["status"] == 404
    assert "Không tìm thấy đơn nghỉ phép" in body["message"]
    assert body["data"] is None


def test_delete_non_pending_absence_fails(auth_client, create_employee, create_absence_record):
    create_employee(id=1)

    absence = create_absence_record(
        employee_id=1,
        status=ApprovalStatus.APPROVED
    )

    response = auth_client.delete(f"/api/v1/absences/{absence.id}")

    assert response.status_code == 400
    body = response.json()

    assert body["status"] == 400
    assert "Không thể xóa đơn vì trạng thái hiện tại là" in body["message"]
    assert body["data"] is None