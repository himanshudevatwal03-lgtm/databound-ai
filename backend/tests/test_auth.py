"""
test_auth.py

Covers the behaviors called out explicitly in the project spec's Testing
section: registration, login, invalid credentials, and unauthorized
access. Also checks the things that would be easy to get subtly wrong:
duplicate emails, wrong passwords, malformed/missing tokens, and that a
registered password is never returned in any response.
"""


def _unique_email(suffix: str) -> str:
    import uuid

    return f"test-{uuid.uuid4().hex[:8]}-{suffix}@example.com"


def test_register_creates_account_and_returns_token(client, cleanup_users):
    email = _unique_email("register")
    cleanup_users.append(email)

    response = client.post(
        "/api/auth/register",
        json={"name": "Rahul Test", "email": email, "password": "supersecret123"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert "access_token" in body and len(body["access_token"]) > 0
    assert body["user"]["email"] == email
    assert body["user"]["name"] == "Rahul Test"
    # The password/hash must never appear in the response.
    assert "password" not in body["user"]
    assert "password_hash" not in body["user"]


def test_register_rejects_duplicate_email(client, cleanup_users):
    email = _unique_email("duplicate")
    cleanup_users.append(email)

    first = client.post(
        "/api/auth/register",
        json={"name": "First", "email": email, "password": "supersecret123"},
    )
    assert first.status_code == 201

    second = client.post(
        "/api/auth/register",
        json={"name": "Second", "email": email, "password": "differentpassword"},
    )
    assert second.status_code == 400


def test_register_rejects_short_password(client):
    response = client.post(
        "/api/auth/register",
        json={"name": "Weak", "email": _unique_email("weak"), "password": "short"},
    )
    assert response.status_code == 422  # Pydantic validation error


def test_login_with_correct_credentials_succeeds(client, cleanup_users):
    email = _unique_email("login-ok")
    cleanup_users.append(email)
    client.post(
        "/api/auth/register",
        json={"name": "Login Test", "email": email, "password": "correcthorse123"},
    )

    response = client.post(
        "/api/auth/login", json={"email": email, "password": "correcthorse123"}
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_with_wrong_password_fails(client, cleanup_users):
    email = _unique_email("login-badpw")
    cleanup_users.append(email)
    client.post(
        "/api/auth/register",
        json={"name": "Login Test", "email": email, "password": "correcthorse123"},
    )

    response = client.post(
        "/api/auth/login", json={"email": email, "password": "wrongpassword"}
    )

    assert response.status_code == 401


def test_login_with_unknown_email_fails(client):
    response = client.post(
        "/api/auth/login",
        json={"email": _unique_email("never-registered"), "password": "whatever123"},
    )
    assert response.status_code == 401


def test_me_requires_authentication(client):
    """No Authorization header at all -> unauthorized."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_rejects_garbage_token(client):
    response = client.get(
        "/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401


def test_me_returns_current_user_with_valid_token(client, cleanup_users):
    email = _unique_email("me")
    cleanup_users.append(email)
    register_response = client.post(
        "/api/auth/register",
        json={"name": "Me Test", "email": email, "password": "correcthorse123"},
    )
    token = register_response.json()["access_token"]

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["email"] == email
