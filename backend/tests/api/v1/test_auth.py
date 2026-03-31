
def test_login_success(client, create_employee):
    # tạo user
    create_employee(id=1)

    payload = {
        "email": "user1@test.com",
        "password": "hashed",  # đúng với password_hash
    }

    response = client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == 1000
    assert body["message"] == "OK"

    # check data trả về
    assert body["data"]["id"] == 1
    assert body["data"]["email"] == "user1@test.com"


def test_login_wrong_password(client, create_employee):
    create_employee(id=1)

    payload = {
        "email": "user1@test.com",
        "password": "wrong_password",
    }

    response = client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 401
    body = response.json()

    assert body["status"] == 401
    assert body["message"] == "Email hoặc mật khẩu không đúng"
    assert body["data"] is None


def test_login_user_not_found(client):
    payload = {
        "email": "notfound@test.com",
        "password": "123456",
    }

    response = client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 401
    body = response.json()

    assert body["status"] == 401
    assert body["message"] == "Email hoặc mật khẩu không đúng"
    assert body["data"] is None


def test_login_validation_error(client):
    # thiếu password
    payload = {
        "email": "user@test.com"
    }

    response = client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 422
    body = response.json()

    assert body["status"] == 422
    assert body["message"] == "Dữ liệu đầu vào không hợp lệ"
    assert "errors" in body


def test_logout_success(client, create_employee):
    # login trước để có session
    create_employee(id=1)

    login_payload = {
        "email": "user1@test.com",
        "password": "hashed",
    }

    client.post("/api/v1/auth/login", json=login_payload)

    # logout
    response = client.post("/api/v1/auth/logout")

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == 1000
    assert body["message"] == "Đăng xuất thành công"
    assert body["data"] is None