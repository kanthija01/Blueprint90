"""Auth route tests.

Mocks the Emergent session-data HTTP call so tests don't depend on the
external service. Verifies:
  - /api/auth/session creates a user + session and returns the token
  - /api/auth/me requires a valid Bearer token (401 otherwise)
  - Repeat login by email does NOT create a duplicate user
  - /api/auth/logout deletes the session row
"""
from __future__ import annotations

import os
from unittest.mock import AsyncMock, patch

import pytest
from pymongo import MongoClient

from core.db import Collections

EMERGENT_SESSION_FIXTURE = {
    "id": "emergent_user_abc",
    "email": "new.user@example.com",
    "name": "New User",
    "picture": "https://example.com/p.png",
    "session_token": "persistent-session-token-xyz",
}


def _mongo():
    return MongoClient(os.environ["MONGODB_URI"])["blueprint90_test"]


class TestSessionExchange:
    def test_exchange_creates_user_and_session(self, client):
        with patch(
            "auth.routes.fetch_emergent_session",
            new=AsyncMock(return_value=EMERGENT_SESSION_FIXTURE),
        ):
            r = client.post(
                "/api/auth/session", json={"session_id": "one-time-id"}
            )
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["session_token"] == EMERGENT_SESSION_FIXTURE["session_token"]
        assert body["user"]["email"] == EMERGENT_SESSION_FIXTURE["email"]
        assert body["user"]["user_id"].startswith("user_")

        db = _mongo()
        assert db[Collections.USERS].count_documents({}) == 1
        assert (
            db[Collections.USER_SESSIONS].count_documents(
                {"session_token": EMERGENT_SESSION_FIXTURE["session_token"]}
            )
            == 1
        )

    def test_exchange_is_idempotent_per_email(self, client):
        with patch(
            "auth.routes.fetch_emergent_session",
            new=AsyncMock(return_value=EMERGENT_SESSION_FIXTURE),
        ):
            r1 = client.post(
                "/api/auth/session", json={"session_id": "sid1"}
            )
            r2 = client.post(
                "/api/auth/session", json={"session_id": "sid2"}
            )
        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r1.json()["user"]["user_id"] == r2.json()["user"]["user_id"]
        db = _mongo()
        assert db[Collections.USERS].count_documents({}) == 1

    def test_exchange_rejects_when_emergent_returns_error(self, client):
        from auth.service import AuthError

        with patch(
            "auth.routes.fetch_emergent_session",
            new=AsyncMock(side_effect=AuthError("bad session")),
        ):
            r = client.post(
                "/api/auth/session", json={"session_id": "oops"}
            )
        assert r.status_code == 401
        assert "bad session" in r.json()["detail"]

    def test_exchange_validates_body(self, client):
        r = client.post("/api/auth/session", json={})
        assert r.status_code == 422


class TestAuthMe:
    def test_me_requires_authorization_header(self, client):
        r = client.get("/api/auth/me")
        assert r.status_code == 401
        assert r.headers.get("www-authenticate") == "Bearer"

    def test_me_rejects_malformed_authorization(self, client):
        r = client.get(
            "/api/auth/me", headers={"Authorization": "Token abc"}
        )
        assert r.status_code == 401

    def test_me_rejects_unknown_token(self, client):
        r = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer nonexistent-token"},
        )
        assert r.status_code == 401

    def test_me_returns_user_with_valid_token(self, client):
        # Seed a user + session via the real flow (mocked Emergent call).
        with patch(
            "auth.routes.fetch_emergent_session",
            new=AsyncMock(return_value=EMERGENT_SESSION_FIXTURE),
        ):
            login = client.post(
                "/api/auth/session", json={"session_id": "sid"}
            )
        token = login.json()["session_token"]
        r = client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert r.status_code == 200
        assert r.json()["email"] == EMERGENT_SESSION_FIXTURE["email"]


class TestLogout:
    def test_logout_clears_session(self, client):
        with patch(
            "auth.routes.fetch_emergent_session",
            new=AsyncMock(return_value=EMERGENT_SESSION_FIXTURE),
        ):
            login = client.post(
                "/api/auth/session", json={"session_id": "sid"}
            )
        token = login.json()["session_token"]
        r = client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 200
        assert r.json()["success"] is True
        db = _mongo()
        assert (
            db[Collections.USER_SESSIONS].count_documents(
                {"session_token": token}
            )
            == 0
        )
        # /me now fails.
        r2 = client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert r2.status_code == 401

    def test_logout_requires_auth(self, client):
        r = client.post("/api/auth/logout")
        assert r.status_code == 401
