def _experience_payload(**overrides):
    payload = {
        "org": "Own practice",
        "role": "Lead attorney",
        "start_date": "2018-01",
        "end_date": None,
        "current": True,
        "location": "Cartagena",
        "description": "Independent civil and labor litigation.",
    }
    payload.update(overrides)
    return payload


def test_create_experience(client, auth_headers):
    resp = client.post("/experience/", json=_experience_payload(), headers=auth_headers)

    assert resp.status_code == 201
    assert resp.json()["start_date"] == "2018-01"


def test_create_experience_rejects_bad_date_format(client, auth_headers):
    resp = client.post(
        "/experience/",
        json=_experience_payload(start_date="2018-13"),  # month 13 doesn't exist
        headers=auth_headers,
    )

    assert resp.status_code == 422


def test_create_experience_rejects_future_date(client, auth_headers):
    resp = client.post(
        "/experience/",
        json=_experience_payload(start_date="2099-01"),
        headers=auth_headers,
    )

    assert resp.status_code == 422


def test_list_experience_ordered_most_recent_first(client, auth_headers):
    client.post(
        "/experience/",
        json=_experience_payload(
            org="Old job", start_date="2015-01", current=False, end_date="2017-12"
        ),
        headers=auth_headers,
    )
    client.post(
        "/experience/",
        json=_experience_payload(org="Current job", start_date="2020-01"),
        headers=auth_headers,
    )

    resp = client.get("/experience/", headers=auth_headers)

    assert resp.status_code == 200
    orgs = [e["org"] for e in resp.json()]
    assert orgs == ["Current job", "Old job"]


def test_update_and_delete_experience(client, auth_headers):
    created = client.post(
        "/experience/", json=_experience_payload(), headers=auth_headers
    ).json()

    update_resp = client.patch(
        f"/experience/{created['id']}",
        json=_experience_payload(role="Senior attorney"),
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["role"] == "Senior attorney"

    delete_resp = client.delete(f"/experience/{created['id']}", headers=auth_headers)
    assert delete_resp.status_code == 200


def test_experience_not_owned_by_caller_is_forbidden(client, auth_headers):
    import uuid

    created = client.post(
        "/experience/", json=_experience_payload(), headers=auth_headers
    ).json()

    other_email = f"other_{uuid.uuid4().hex[:12]}@example.com"
    client.post(
        "/auth/register", json={"email": other_email, "password": "supersecret123"}
    )
    other_login = client.post(
        "/auth/login", data={"username": other_email, "password": "supersecret123"}
    )
    other_headers = {"Authorization": f"Bearer {other_login.json()['access_token']}"}

    resp = client.patch(
        f"/experience/{created['id']}",
        json=_experience_payload(role="Hijacked"),
        headers=other_headers,
    )
    assert resp.status_code == 403
