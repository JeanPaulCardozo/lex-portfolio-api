def _case_payload(practice_area_id, **overrides):
    payload = {
        "title": "Executive process: full payment after injunction",
        "practice_area_id": practice_area_id,
        "year": 2024,
        "role": "Plaintiff's counsel",
        "result_type": "acuerdo",  # the enum's wire VALUE, not its Python name ("settlement")
        "outcome": "Full payment before judgment",
        "situation": "A supplier was not paid despite several demands.",
        "action": "An executive claim was filed with injunctive relief.",
        "result": "The debtor paid in full before the hearing.",
        "skills": ["Executive process", "Injunctions"],
        "featured": True,
        "confidential": False,
        "imageUrl": "",
    }
    payload.update(overrides)
    return payload


def test_create_case_relates_to_practice_area_by_id(client, auth_headers, practice_area):
    resp = client.post(
        "/cases/", json=_case_payload(practice_area["id"]), headers=auth_headers
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["practice_area_id"] == practice_area["id"]
    assert body["result_type"] == "acuerdo"  # enum value on the wire, not the Python name
    assert body["slug"] == "executive-process-full-payment-after-injunction"


def test_create_case_rejects_invalid_result_type(client, auth_headers, practice_area):
    resp = client.post(
        "/cases/",
        json=_case_payload(practice_area["id"], result_type="not-a-real-type"),
        headers=auth_headers,
    )

    assert resp.status_code == 422


def test_create_case_rejects_duplicate_slug(client, auth_headers, practice_area):
    client.post("/cases/", json=_case_payload(practice_area["id"]), headers=auth_headers)
    resp = client.post(
        "/cases/", json=_case_payload(practice_area["id"]), headers=auth_headers
    )

    assert resp.status_code == 400


def test_list_cases_filters_by_practice_area_and_year(client, auth_headers, practice_area):
    client.post(
        "/cases/",
        json=_case_payload(practice_area["id"], title="Case A", year=2023),
        headers=auth_headers,
    )
    client.post(
        "/cases/",
        json=_case_payload(practice_area["id"], title="Case B", year=2024),
        headers=auth_headers,
    )

    resp = client.get(
        "/cases/", params={"year": 2024}, headers=auth_headers
    )

    assert resp.status_code == 200
    titles = [c["title"] for c in resp.json()]
    assert titles == ["Case B"]


def test_list_cases_free_text_search(client, auth_headers, practice_area):
    client.post(
        "/cases/",
        json=_case_payload(practice_area["id"], title="Labor dispute settlement"),
        headers=auth_headers,
    )

    resp = client.get("/cases/", params={"query": "labor"}, headers=auth_headers)

    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_get_case_by_slug_not_found(client, auth_headers):
    resp = client.get("/cases/does-not-exist", headers=auth_headers)
    assert resp.status_code == 404


def test_update_case_renames_slug(client, auth_headers, practice_area):
    created = client.post(
        "/cases/", json=_case_payload(practice_area["id"]), headers=auth_headers
    ).json()

    resp = client.patch(
        f"/cases/{created['id']}",
        json=_case_payload(practice_area["id"], title="Renamed case title"),
        headers=auth_headers,
    )

    assert resp.status_code == 200
    assert resp.json()["slug"] == "renamed-case-title"


def test_delete_case(client, auth_headers, practice_area):
    created = client.post(
        "/cases/", json=_case_payload(practice_area["id"]), headers=auth_headers
    ).json()

    resp = client.delete(f"/cases/{created['id']}", headers=auth_headers)
    assert resp.status_code == 200
