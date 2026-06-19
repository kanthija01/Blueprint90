"""User + session Pydantic models for Emergent-managed Google auth.

Kept intentionally small. Every record has a stable `user_id` we mint
ourselves — Mongo's `_id` is never exposed to the API surface.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _make_user_id() -> str:
    return f"user_{uuid.uuid4().hex[:12]}"


class User(BaseModel):
    """Persisted Google-authenticated user."""

    model_config = ConfigDict(extra="forbid")

    user_id: str = Field(default_factory=_make_user_id)
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class UserSession(BaseModel):
    """One issued session token. TTL-indexed in Mongo on `expires_at`."""

    model_config = ConfigDict(extra="forbid")

    session_token: str
    user_id: str
    created_at: datetime = Field(default_factory=_now)
    expires_at: datetime


class UserPublic(BaseModel):
    """Sanitised user shape returned by /api/auth/me."""

    user_id: str
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None
