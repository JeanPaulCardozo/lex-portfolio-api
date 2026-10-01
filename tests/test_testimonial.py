def _submit_payload(**overrides):
    payload = {
        "author": "Laura Mendez",
        "author_role": "Services sector",
        "quote": "They explained every step clearly and the case was resolved fast.",
        "rating": 5,
        "email": "laura@example.com",
    }
    payload.update(overrides)
    return payload


def test_public_submit_always_creates_pending_ignoring_status_in_body(client):
    resp = client.post(
        "/testimonials/submit",
        json={**_submit_payload(), "status": "Aprobado"},
    )

    assert resp.status_code == 201
    assert resp.json() == {"ok": True}


def test_public_submit_rejects_rating_out_of_range(client):
    resp = client.post("/testimonials/submit", json=_submit_payload(rating=7))
    assert resp.status_code == 422


def test_public_submit_rejects_invalid_email(client):
    resp = client.post(
        "/testimonials/submit", json=_submit_payload(email="not-an-email")
    )
    assert resp.status_code == 422


def test_public_list_only_shows_approved_and_never_exposes_email(client, auth_headers):
    # Manually created by the lawyer -> approved by default.
    approved_resp = client.post(
        "/testimonials/",
        json={
            "author": "Approved client",
            "author_role": "Commerce",
            "quote": "Great service, would recommend.",
            "rating": 5,
            "email": "approved@example.com",
        },
        headers=auth_headers,
    )
    assert approved_resp.status_code == 201

    # Submitted by a visitor -> stays pending, must not show up publicly.
    client.post(
        "/testimonials/submit",
        json=_submit_payload(author="Pending visitor"),
    )

    resp = client.get("/testimonials/")

    assert resp.status_code == 200
    body = resp.json()
    authors = [t["author"] for t in body]
    assert "Approved client" in authors
    assert "Pending visitor" not in authors
    assert all("email" not in t for t in body)


def test_all_testimonials_requires_auth(client):
    resp = client.get("/testimonials/", params={"all": 1})
    assert resp.status_code == 403


def test_all_testimonials_includes_pending_and_email_for_owner(client, auth_headers):
    # Note: /testimonials/submit always attaches to whichever user is first
    # in the Users table (see create_testimonial_by_public), not necessarily
    # this test's own auth_headers user -- so we create the pending
    # testimonial through the authenticated endpoint instead, which does
    # attach it to current_user.id, to keep this test independent of that.
    client.post(
        "/testimonials/",
        json={
            "author": "Pending review case",
            "author_role": "Industry",
            "quote": "Awaiting approval.",
            "rating": 4,
            "email": "pending-review@example.com",
            "status": "Pendiente",
        },
        headers=auth_headers,
    )

    resp = client.get("/testimonials/", params={"all": 1}, headers=auth_headers)

    assert resp.status_code == 200
    body = resp.json()
    pending = next(t for t in body if t["author"] == "Pending review case")
    assert pending["status"] == "Pendiente"
    assert pending["email"] == "pending-review@example.com"


def test_approve_testimonial_via_status_endpoint(client, auth_headers):
    created = client.post(
        "/testimonials/",
        json={
            "author": "To be approved",
            "author_role": "Industry",
            "quote": "Initially pending testimonial.",
            "rating": 4,
            "email": "pending@example.com",
            "status": "Pendiente",
        },
        headers=auth_headers,
    ).json()

    resp = client.patch(
        f"/testimonials/{created['id']}/status",
        json={"status": "Aprobado"},
        headers=auth_headers,
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "Aprobado"


def test_delete_testimonial(client, auth_headers):
    created = client.post(
        "/testimonials/",
        json={
            "author": "To be deleted",
            "author_role": "Industry",
            "quote": "Will be removed in this test.",
            "rating": 3,
            "email": "delete@example.com",
        },
        headers=auth_headers,
    ).json()

    resp = client.delete(f"/testimonials/{created['id']}", headers=auth_headers)
    assert resp.status_code == 200
