from app.schemas.system_setting import SystemSettingKey

def test_read_settings(admin_client):
    response = admin_client.get("/api/v1/settings/")
    assert response.status_code == 200

    json_resp = response.json()
    
    # Kiểm tra ResponseSchema
    assert json_resp["status"] == 1000
    assert json_resp["message"] == "OK"

    data = json_resp["data"]
    assert isinstance(data, list)
    assert len(data) == 5  # có 5 settings được seed

    # Kiểm tra key/value cụ thể
    expected_settings = {
        "lunch_break_start": "12:10",
        "lunch_break_end": "13:40",
        "annual_paid_leave_days": "14",
        "maternity_leave_months": "6",
        "max_attendance_correction_per_month": "3"
    }

    for item in data:
        key = item["key"]
        value = item["value"]
        description = item["description"]
        assert key in expected_settings
        assert value == expected_settings[key]
        assert isinstance(description, str)


def test_update_multiple_settings_api(admin_client):
    payload = [
        {"key": SystemSettingKey.LUNCH_START.value, "value": "12:10"},
        {"key": SystemSettingKey.LUNCH_END.value, "value": "13:40"},
    ]
    response = admin_client.put("/api/v1/settings/", json=payload)
    assert response.status_code == 200
    data = response.json()["data"]

    # kiểm tra từng key đã được cập nhật
    lunch_start = next(item for item in data if item["key"] == "lunch_break_start")
    lunch_end = next(item for item in data if item["key"] == "lunch_break_end")
    assert lunch_start["value"] == "12:10"
    assert lunch_end["value"] == "13:40"
