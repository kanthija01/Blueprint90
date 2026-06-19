"""FastAPI dependencies for Emergent-managed Google auth.

We intentionally DO NOT use `HTTPBearer` from fastapi.security — per the
integration playbook it returns 403 instead of 401 when the header is
missing, which conflicts with the contract Expo clients expect.
"""
from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from auth.service import get_user_by_token
from core.db import get_db
from models.user import User


def get_db_dep() -> AsyncIOMotorDatabase:
    """Thin wrapper so tests can override the DB handle via
    `app.dependency_overrides[get_db_dep] = ...`.
    """
    return get_db()


def _extract_bearer(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    parts = authorization.split(None, 1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected 'Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return parts[1].strip()


async def get_current_user(
    authorization: str | None = Header(default=None),
    db: AsyncIOMotorDatabase = Depends(get_db_dep),
) -> User:
    token = _extract_bearer(authorization)
    user = await get_user_by_token(db, token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
