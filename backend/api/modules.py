"""GET /api/modules — lightweight metadata listing for admin/debug.

Returns only top-level metadata, not the heavy section content. Useful for
  - confirming the seed succeeded
  - the admin UI to inspect coverage
  - debugging the rules engine output

Authenticated. Not admin-gated yet (we don't have a roles system).
"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from auth.dependencies import get_current_user, get_db_dep
from core.db import Collections
from models.api import ModuleSummary
from models.user import User

router = APIRouter(prefix="/modules", tags=["modules"])


@router.get("", response_model=List[ModuleSummary])
async def list_modules(
    current: User = Depends(get_current_user),  # noqa: ARG001 — auth gate
    db: AsyncIOMotorDatabase = Depends(get_db_dep),
):
    cursor = (
        db[Collections.MODULES]
        .find(
            {},
            {
                "_id": 0,
                "slug": 1,
                "display_name": 1,
                "audience": 1,
                "primary_goal": 1,
                "is_authored_extension": 1,
                "content_pending": 1,
            },
        )
        .sort("slug", 1)
    )
    return [ModuleSummary(**doc) async for doc in cursor]
