def _publication_payload(**overrides):
    payload = {
        "title": "Injunctions in executive proceedings",
        "kind": "articulo",  # the enum's wire VALUE, not its Python name ("article")
        "venue": "Legal blog",
        "date": "2025-03-11",
        "url": "",
        "summary": "A practical look at injunctions.",
    }
    payload.update(overrides)
    return payload


def test_create_publication(client, auth_headers):
    resp = client.post(
        "/publications/", json=_publication_payload(), headers=auth_headers
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["kind"] == "articulo"  # enum wire value, not the Python name ("article")
    assert body["date"] == "2025-03-11"


def test_create_publication_rejects_bad_date_format(client, auth_headers):
    resp = client.post(
        "/publications/",
        json=_publication_payload(date="11-03-2025"),
        headers=auth_headers,
    )

    assert resp.status_code == 422


def test_create_publication_rejects_future_date(client, auth_headers):
    resp = client.post(
        "/publications/",
        json=_publication_payload(date="2099-01-01"),
        headers=auth_headers,
    )

    assert resp.status_code == 422


def test_create_publication_rejects_invalid_kind(client, auth_headers):
    resp = client.post(
        "/publications/",
        json=_publication_payload(kind="not-a-real-kind"),
        headers=auth_headers,
    )

    assert resp.status_code == 422


def test_list_publications_ordered_by_date_desc(client, auth_headers):
    client.post(
        "/publications/",
        json=_publication_payload(title="Older", date="2020-01-01"),
        headers=auth_headers,
    )
    client.post(
        "/publications/",
        json=_publication_payload(title="Newer", date="2024-01-01"),
        headers=auth_headers,
    )

    resp = client.get("/publications/", headers=auth_headers)

    assert resp.status_code == 200
    titles = [p["title"] for p in resp.json()]
    assert titles == ["Newer", "Older"]


def test_update_and_delete_publication(client, auth_headers):
    created = client.post(
        "/publications/", json=_publication_payload(), headers=auth_headers
    ).json()

    update_resp = client.patch(
        f"/publications/{created['id']}",
        json=_publication_payload(title="Updated title"),
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Updated title"

    delete_resp = client.delete(f"/publications/{created['id']}", headers=auth_headers)
    assert delete_resp.status_code == 200
