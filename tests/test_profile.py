def test_get_profile_404_when_not_created_yet(client, auth_headers):
    resp = client.get("/profile/", headers=auth_headers)
    assert resp.status_code == 404


def test_update_profile_upserts_on_first_call(client, auth_headers):
    payload = {
        "full_name": "Maria Banda",
        "title": "Lawyer",
        "tagline": "Clear, honest legal counsel",
        "headline": "Civil and labor litigation",
        "email": "maria@example.com",
    }

    resp = client.patch("/profile/", json=payload, headers=auth_headers)

    assert resp.status_code == 200
    body = resp.json()
    assert body["full_name"] == "Maria Banda"
    assert body["languages"] == []

    # Now it exists, GET should find it.
    get_resp = client.get("/profile/", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["full_name"] == "Maria Banda"


def test_update_profile_partial_update_keeps_other_fields(client, auth_headers):
    base_payload = {
        "full_name": "Maria Banda",
        "title": "Lawyer",
        "tagline": "Clear, honest legal counsel",
        "headline": "Civil and labor litigation",
        "email": "maria@example.com",
        "languages": ["Spanish"],
    }
    client.patch("/profile/", json=base_payload, headers=auth_headers)

    resp = client.patch(
        "/profile/", json={**base_payload, "title": "Senior Lawyer"}, headers=auth_headers
    )

    assert resp.status_code == 200
    assert resp.json()["title"] == "Senior Lawyer"
    assert resp.json()["languages"] == ["Spanish"]


def test_profile_requires_auth(client):
    resp = client.get("/profile/")
    assert resp.status_code == 401
