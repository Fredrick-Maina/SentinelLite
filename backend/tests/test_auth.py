def test_register_user(client):
    payload = {
        "email": "analyst@example.com",
        "password": "SecurePassword123!",
        "full_name": "Security Analyst",
        "organization_name": "Cyber Defense Inc"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "analyst@example.com"
    assert data["full_name"] == "Security Analyst"
    assert "id" in data


def test_login_user(client):
    # Register first
    reg_payload = {
        "email": "user@example.com",
        "password": "MySecretPassword123!",
        "full_name": "Test User"
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    # Login
    login_data = {
        "username": "user@example.com",
        "password": "MySecretPassword123!"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    # Test /me endpoint
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_response = client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == "user@example.com"


def test_login_invalid_password(client):
    login_data = {
        "username": "nonexistent@example.com",
        "password": "WrongPassword"
    }
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 400
