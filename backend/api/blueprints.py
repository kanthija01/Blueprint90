"""GET /api/blueprints, GET /api/blueprints/{id}, GET /api/blueprints/{id}/selections.

All routes return ONLY documents owned by the authenticated user. Any other
blueprint id returns 404 — we don't leak existence of someone else's record.

The single-blueprint detail route reads the CACHED `assembled_json` from
Mongo and never re-runs assembly. This is enforced by the test
`test_blueprint_detail_never_reruns_assembly` which patches
`assemble_blueprint` and asserts it's never called.
"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from auth.dependencies import get_current_user, get_db_dep
from core.db import Collections
from models.api import (
    BlueprintListItem,
    BlueprintSelectionsResponse,
)
from models.blueprint import AssembledBlueprint
from models.user import User
from rules_engine.types import ModuleSelection

router = APIRouter(prefix="/blueprints", tags=["blueprints"])


@router.get("", response_model=List[BlueprintListItem])
async def list_blueprints(
    current: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db_dep),
):
    cursor = (
        db[Collections.BLUEPRINTS]
        .find({"user_id": current.user_id}, {"_id": 0})
        .sort("created_at", -1)
    )
    items: List[BlueprintListItem] = []
    async for doc in cursor:
        assembled = doc["assembled_json"]
        meta = assembled["meta"]
        items.append(
            BlueprintListItem(
                blueprint_id=doc["blueprint_id"],
                created_at=doc["created_at"],
                goal=assembled["cover_page"]["goal"],
                primary_module_slug=meta["primary_module_slug"],
                primary_module_display_name=next(
                    (
                        m["display_name"]
                        for m in meta["modules_used"]
                        if m["slug"] == meta["primary_module_slug"]
                    ),
                    meta["primary_module_slug"],
                ),
                module_count=len(meta["modules_used"]),
            )
        )
    return items


@router.get("/{blueprint_id}", response_model=AssembledBlueprint)
async def get_blueprint(
    blueprint_id: str,
    current: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db_dep),
):
    """Return ONLY the cached assembled_json. Never re-runs assembly."""
    doc = await db[Collections.BLUEPRINTS].find_one(
        {"blueprint_id": blueprint_id, "user_id": current.user_id},
        {"_id": 0, "assembled_json": 1},
    )
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blueprint not found",
        )
    return doc["assembled_json"]


@router.get(
    "/{blueprint_id}/selections", response_model=BlueprintSelectionsResponse
)
async def get_blueprint_selections(
    blueprint_id: str,
    current: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db_dep),
):
    bp = await db[Collections.BLUEPRINTS].find_one(
        {"blueprint_id": blueprint_id, "user_id": current.user_id},
        {"_id": 0, "assessment_id": 1, "selections_id": 1},
    )
    if not bp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blueprint not found",
        )
    sels = await db[Collections.ASSESSMENT_MODULE_SELECTIONS].find_one(
        {
            "selections_id": bp["selections_id"],
            "user_id": current.user_id,
        },
        {"_id": 0, "selections": 1},
    )
    if not sels:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Selections record missing for blueprint.",
        )
    return BlueprintSelectionsResponse(
        blueprint_id=blueprint_id,
        assessment_id=bp["assessment_id"],
        selections=[ModuleSelection(**s) for s in sels["selections"]],
    )
