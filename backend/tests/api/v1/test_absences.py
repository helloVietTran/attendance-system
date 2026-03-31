        
from datetime import date

def test_create_absence(auth_client, create_employee, create_shifts, create_absence_types):
    create_shifts()
    create_absence_types()
    create_employee()

    payload = {
        "employee_id": 1,
        "absence_type_id": 1,
        "start_date": "2026-04-01",
        "end_date": "2026-04-02",
        "reason": "Test nghỉ phép"
    }

    res = auth_client.post("/api/v1/absences/", json=payload)

    assert res.status_code == 200