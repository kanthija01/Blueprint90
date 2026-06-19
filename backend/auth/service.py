"""Emergent Google auth — backend helpers.

Responsibilities:
  - Exchange a one-time `session_id` for the persistent session payload
    from Emergent's session-data endpoint.
  - Upsert the user document (no duplicates on repeated logins — key by email).
  - Issue/delete our own `user_sessions` rows keyed by the Emergent
    `session_token`.

Following the integration playbook verbatim:
  - Session token lifetime: 7 days.
  - Custom `user_id` is the only identifier we expose (no Mongo `_id`).
  - All datetimes are timezone-aware UTC.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import httpx
from motor.motor_asyncio import AsyncIOMotorDatabase

from core.db import Collections
from models.user import User, UserSession, _make_user_id, _now

EMERGENT_SESSION_DATA_URL = (
    "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"
)
SESSION_TTL = timedelta(days=7)


class AuthError(Exception):
    """Raised on any auth-flow failure. The route layer maps to HTTP codes."""


async def fetch_emergent_session(session_id: str) -> Dict[str, Any]:
    """Exchange one-time session_id for the persistent payload.

    Returns dict with: id, email, name, picture, session_token.
    Raises AuthError on any non-200 / network failure.
    """
    if not session_id or not session_id.strip():
        raise AuthError("Missing session_id")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                EMERGENT_SESSION_DATA_URL,
                headers={"X-Session-ID": session_id.strip()},
            )
    except httpx.HTTPError as exc:
        raise AuthError(f"Emergent auth unreachable: {exc}") from exc

    if resp.status_code != 200:
        raise AuthError(
            f"Emergent auth rejected session_id (status {resp.status_code})"
        )
    data = resp.json()
    required = {"email", "session_token"}
    missing = required - data.keys()
    if missing:
        raise AuthError(f"Emergent payload missing fields: {sorted(missing)}")
    return data


async def upsert_user(
    db: AsyncIOMotorDatabase, payload: Dict[str, Any]
) -> User:
    """Find user by email or create one. Never mints a duplicate."""
    coll = db[Collections.USERS]
    existing = await coll.find_one({"email": payload["email"]}, {"_id": 0})
    if existing:
        # Refresh display fields, keep the original user_id.
        update = {
            "name": payload.get("name") or existing.get("name"),
            "picture": payload.get("picture") or existing.get("picture"),
            "updated_at": _now(),
        }
        await coll.update_one(
            {"user_id": existing["user_id"]}, {"$set": update}
        )
        existing.update(update)
        return User(**existing)

    user = User(
        user_id=_make_user_id(),
        email=payload["email"],
        name=payload.get("name"),
        picture=payload.get("picture"),
    )
    await coll.insert_one(user.model_dump())
    return user


async def create_session(
    db: AsyncIOMotorDatabase, user_id: str, session_token: str
) -> UserSession:
    """Idempotent-by-token: upsert so re-sending same token doesn't duplicate."""
    expires_at = datetime.now(timezone.utc) + SESSION_TTL
    session = UserSession(
        session_token=session_token,
        user_id=user_id,
        expires_at=expires_at,
    )
    await db[Collections.USER_SESSIONS].update_one(
        {"session_token": session_token},
        {"$set": session.model_dump()},
        upsert=True,
    )
    return session


async def get_user_by_token(
    db: AsyncIOMotorDatabase, token: str
) -> Optional[User]:
    """Look up active session + user. Returns None if missing/expired."""
    if not token:
        return None
    sess = await db[Collections.USER_SESSIONS].find_one(
        {"session_token": token}, {"_id": 0}
    )
    if not sess:
        return None
    expires = sess["expires_at"]
    if isinstance(expires, datetime) and expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        return None
    user_doc = await db[Collections.USERS].find_one(
        {"user_id": sess["user_id"]}, {"_id": 0}
    )
    if not user_doc:
        return None
    return User(**user_doc)


async def delete_session(db: AsyncIOMotorDatabase, token: str) -> int:
    res = await db[Collections.USER_SESSIONS].delete_one(
        {"session_token": token}
    )
    return res.deleted_count
