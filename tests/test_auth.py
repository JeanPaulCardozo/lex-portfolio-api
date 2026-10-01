def test_register_creates_user(client, unique_email, password):
    resp = client.post(
        "/auth/register", json={"email": unique_email, "password": password}
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == unique_email
    assert "id" in body
    assert "hashed_password" not in body


def test_register_rejects_duplicate_email(client, unique_email, password):
    client.post("/auth/register", json={"email": unique_email, "password": password})
    resp = client.post(
        "/auth/register", json={"email": unique_email, "password": password}
    )

    assert resp.status_code == 400


def test_register_rejects_short_password(client, unique_email):
    resp = client.post(
        "/auth/register", json={"email": unique_email, "password": "short"}
    )

    assert resp.status_code == 422


def test_login_returns_token(client, unique_email, password):
    client.post("/auth/register", json={"email": unique_email, "password": password})

    resp = client.post(
        "/auth/login", data={"username": unique_email, "password": password}
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_rejects_wrong_password(client, unique_email, password):
    client.post("/auth/register", json={"email": unique_email, "password": password})

    resp = client.post(
        "/auth/login", data={"username": unique_email, "password": "wrongpassword"}
    )

    assert resp.status_code == 401


def test_me_requires_a_valid_token(client, auth_headers):
    resp = client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200

    resp_no_token = client.get("/auth/me")
    assert resp_no_token.status_code == 401

    resp_bad_token = client.get(
        "/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert resp_bad_token.status_code == 401
