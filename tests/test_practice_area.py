def _create(client, auth_headers, name="Civil Law"):
    return client.post(
        "/practice-areas/",
        json={
            "name": name,
            "summary": "Summary",
            "description": "Description",
            "fags": [{"q": "Q?", "a": "A."}],
        },
        headers=auth_headers,
    )


def test_create_practice_area_generates_slug_and_order(client, auth_headers):
    resp = _create(client, auth_headers, name="Civil Procedure Law")

    assert resp.status_code == 201
    body = resp.json()
    assert body["slug"] == "civil-procedure-law"
    assert body["name"] == "Civil Procedure Law"


def test_create_practice_area_rejects_duplicate_name(client, auth_headers):
    _create(client, auth_headers, name="Labor Law")
    resp = _create(client, auth_headers, name="Labor Law")

    assert resp.status_code == 400


def test_list_practice_areas_scoped_to_current_user(client, auth_headers):
    _create(client, auth_headers, name="Family Law")

    resp = client.get("/practice-areas/", headers=auth_headers)

    assert resp.status_code == 200
    names = [area["name"] for area in resp.json()]
    assert "Family Law" in names


def test_update_practice_area_regenerates_slug(client, auth_headers):
    created = _create(client, auth_headers, name="Tax Law").json()

    resp = client.patch(
        f"/practice-areas/{created['id']}",
        json={
            "name": "Corporate Tax Law",
            "summary": "Summary",
            "description": "Description",
            "fags": [],
        },
        headers=auth_headers,
    )

    assert resp.status_code == 200
    assert resp.json()["slug"] == "corporate-tax-law"


def test_delete_practice_area(client, auth_headers):
    created = _create(client, auth_headers, name="Criminal Law").json()

    resp = client.delete(f"/practice-areas/{created['id']}", headers=auth_headers)
    assert resp.status_code == 200

    get_resp = client.get(f"/practice-areas/{created['slug']}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_other_users_practice_area_is_forbidden(client, auth_headers):
    import uuid

    created = _create(client, auth_headers, name="Immigration Law").json()

    other_email = f"other_{uuid.uuid4().hex[:12]}@example.com"
    other_register = client.post(
        "/auth/register", json={"email": other_email, "password": "supersecret123"}
    )
    assert other_register.status_code == 201
    other_login = client.post(
        "/auth/login",
        data={"username": other_email, "password": "supersecret123"},
    )
    other_headers = {"Authorization": f"Bearer {other_login.json()['access_token']}"}

    resp = client.get(f"/practice-areas/{created['slug']}", headers=other_headers)
    assert resp.status_code == 403
