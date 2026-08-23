from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token

def test_password_hashing():
    password = "SuperSecretPassword123!"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False

def test_jwt_generation_and_decode():
    token = create_access_token(subject=42, role="ADMIN")
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "42"
    assert payload["role"] == "ADMIN"
    assert "exp" in payload

def test_register_and_login_flow(client):
    reg_resp = client.post("/api/v1/auth/register", json={
        "name": "FinOps Engineer",
        "email": "engineer_finops_mvp@cloudguard.io",
        "password": "Password123!"
    })
    assert reg_resp.status_code == 200
    reg_data = reg_resp.json()
    assert reg_data["success"] is True
    assert "access_token" in reg_data["data"]
    assert reg_data["data"]["user"]["email"] == "engineer_finops_mvp@cloudguard.io"

    login_resp = client.post("/api/v1/auth/login", json={
        "email": "engineer_finops_mvp@cloudguard.io",
        "password": "Password123!"
    })
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert login_data["success"] is True
    assert login_data["data"]["token_type"] == "bearer"
