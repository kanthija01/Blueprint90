"""Auth routes — Emergent Google sign-in.

Flow (matches the integration playbook):
  Frontend opens Emergent auth UI -> receives one-time session_id ->
  POSTs it here -> we exchange with Emergent for the persistent
  session_token -> we upsert user + persist session -> we return the
  token + sanitised user to the client, which stores the token in
  expo-secure-store (mobile) / localStorage (web).

Subsequent calls hit GET /api/auth/me with `Authorization: Bearer <token>`.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, ConfigDict

from auth.dependencies import get_current_user, get_db_dep
from auth.service import (
    AuthError,
    create_session,
    delete_session,
    fetch_emergent_session,
    upsert_user,
)
from models.user import User, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])


class SessionExchangeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    session_id: str


class SessionExchangeResponse(BaseModel):
    session_token: str
    user: UserPublic


class LogoutResponse(BaseModel):
    success: bool = True


@router.post(
    "/session",
    response_model=SessionExchangeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def exchange_session(
    body: SessionExchangeRequest,
    db: AsyncIOMotorDatabase = Depends(get_db_dep),
):
    """Exchange a one-time Emergent session_id for our persistent session_token."""
    try:
        payload = await fetch_emergent_session(body.session_id)
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc

    user = await upsert_user(db, payload)
    await create_session(db, user.user_id, payload["session_token"])

    return SessionExchangeResponse(
        session_token=payload["session_token"],
        user=UserPublic(
            user_id=user.user_id,
            email=user.email,
            name=user.name,
            picture=user.picture,
        ),
    )


@router.get("/me", response_model=UserPublic)
async def get_me(current: User = Depends(get_current_user)):
    return UserPublic(
        user_id=current.user_id,
        email=current.email,
        name=current.name,
        picture=current.picture,
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current: User = Depends(get_current_user),  # noqa: ARG001 — gate
    db: AsyncIOMotorDatabase = Depends(get_db_dep),
    authorization: str = Header(default=""),
):
    """Delete the caller's specific session row. get_current_user already
    validated the bearer token, so we can safely re-extract it here."""
    token = ""
    if authorization:
        parts = authorization.split(None, 1)
        if len(parts) == 2:
            token = parts[1].strip()
    if token:
        await delete_session(db, token)
    return LogoutResponse(success=True)
