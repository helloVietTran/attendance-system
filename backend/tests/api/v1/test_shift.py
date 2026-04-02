def test_create_shift_request_success(auth_client, create_employee):
    create_employee(id=1)

    payload = {
        "current_shift_id": 1,
        "new_shift_id": 2,
        "reason": "Muốn đổi ca"
    }

    res = auth_client.post("/api/v1/shift/shift-change-request", json=payload)

    assert res.status_code == 200
    body = res.json()

    assert body["status"] == 1000
    assert body["message"] == "OK"

    assert body["data"]["employee_id"] == 1
    assert body["data"]["old_shift_id"] == 1
    assert body["data"]["new_shift_id"] == 2
    assert body["data"]["status"] == "pending"


def test_create_shift_request_employee_not_found(auth_client):
    payload = {
        "current_shift_id": 1,
        "new_shift_id": 2
    }

    res = auth_client.post("/api/v1/shift/shift-change-request", json=payload)

    assert res.status_code == 404
    body = res.json()

    assert body["status"] == 404
    assert body["message"] == "Nhân viên không tồn tại"


def test_create_shift_request_duplicate(auth_client, create_employee, create_shift_request):
    create_employee(id=1)
    create_shift_request(employee_id=1)  # đã có pending

    payload = {
        "current_shift_id": 1,
        "new_shift_id": 2
    }

    res = auth_client.post("/api/v1/shift/shift-change-request", json=payload)

    assert res.status_code == 400
    body = res.json()

    assert body["status"] == 400
    assert "đang chờ duyệt" in body["message"]
    
