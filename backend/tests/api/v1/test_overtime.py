
from datetime import date

def test_create_ot(auth_client, create_employee):
    employee = create_employee()
    # OT ngoài giờ (trước ca)
    payload = {
        "work_date": date.today().isoformat(),
        "start_time": "19:00",
        "end_time": "20:00",
        "ot_type": "normal_day",
        "reason": "OT test"
    }
    response = auth_client.post("/api/v1/overtimes/", json=payload)
    assert response.status_code == 200

    data = response.json()["data"]
    assert data["employee_id"] == employee.id
    assert data["status"] == "pending"
    assert data["multiplier"] == 1.5
    assert data["start_time"] == "19:00:00"
    assert data["end_time"] == "20:00:00"
    assert data["reason"] == "OT test"