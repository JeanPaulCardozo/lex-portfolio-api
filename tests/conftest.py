"""
Shared pytest fixtures.

These tests run against the same Postgres database configured in
DATABASE_URL (there is no SQLite fallback: the models use Postgres-only
types -- ARRAY, JSONB, native ENUM -- that SQLite cannot create). Every
test is wrapped in an outer transaction that is rolled back at the end,
so nothing written during a test is ever actually persisted, even though
the application code calls db.commit() internally.
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from lex_portfolio_api.core.limiter import limiter
from lex_portfolio_api.database import DATABASE_URL, get_db
from lex_portfolio_api.main import app

_engine = create_engine(DATABASE_URL)


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """POST /auth/login is rate-limited (5/minute). Without this, running
    more than 5 tests that log in would start failing with 429s, since the
    test client's "remote address" is the same for every test."""
    limiter.reset()
    yield


@pytest.fixture()
def db_session():
    connection = _engine.connect()
    outer_transaction = connection.begin()
    session_factory = sessionmaker(bind=connection, autoflush=False, autocommit=False)
    session = session_factory()

    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(sess, trans):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    try:
        yield session
    finally:
        session.close()
        outer_transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def unique_email() -> str:
    return f"test_{uuid.uuid4().hex[:12]}@example.com"


@pytest.fixture()
def password() -> str:
    return "supersecret123"


@pytest.fixture()
def auth_headers(client, unique_email, password) -> dict[str, str]:
    """Registers a fresh user and returns the Authorization header for it."""
    register_resp = client.post(
        "/auth/register", json={"email": unique_email, "password": password}
    )
    assert register_resp.status_code == 201, register_resp.text

    login_resp = client.post(
        "/auth/login",
        data={"username": unique_email, "password": password},
    )
    assert login_resp.status_code == 200, login_resp.text
    token = login_resp.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def practice_area(client, auth_headers) -> dict:
    """A practice area created through the API, for tests that need a
    valid practice_area_id to relate a Case to."""
    resp = client.post(
        "/practice-areas/",
        json={
            "name": f"Area {uuid.uuid4().hex[:8]}",
            "summary": "Test summary",
            "description": "Test description",
            "fags": [{"q": "Question?", "a": "Answer."}],
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()
