"""POST /api/assessments — the workflow endpoint.

Deterministically:
  1. Validate problem slugs (422 on unknown).
  2. Run select_modules() to build the ordered selection.
  3. Persist the assessment + selections.
  4. Fetch module documents from Mongo, in selection order.
  5. Call assemble_blueprint() (pure).
  6. Persist the assembled blueprint.
  7. Return blueprint_id + assembled_json.

The assembled JSON is cached — every subsequent GET reads it back, never
re-runs assembly. That's the contract that lets us regenerate PDFs years
later from the same byte-identical content.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from assembly.assemble_blueprint import assemble_blueprint
from auth.dependencies import get_current_user, get_db_dep
from core.db import Collections
from models.api import (
    AssessmentModuleSelectionsRecord,
    AssessmentRecord,
    AssessmentRequest,
    AssessmentResponse,
    BlueprintRecord,
)
from models.module import Module
from models.user import User
from rules_engine.errors import ModuleMappingError
from rules_engine.select_modules import select_modules
from rules_engine.validate import validate_module_slugs

router = APIRouter(prefix="/assessments", tags=["assessments"])


async def _fetch_modules_in_order(
    db: AsyncIOMotorDatabase, slugs: list[str]
) -> list[Module]:
    """Fetch module docs and return them in the same order as `slugs`."""
    cursor = db[Collections.MODULES].find(
        {"slug": {"$in": slugs}}, {"_id": 0}
    )
    by_slug = {doc["slug"]: doc async for doc in cursor}
    missing = [s for s in slugs if s not in by_slug]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                f"Module(s) selected but not seeded: {missing}. "
                "Re-run scripts/seed_all.py."
            ),
        )
    return [Module(**by_slug[s]) for s in slugs]


@router.post(
    "",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_assessment(
    body: AssessmentRequest,
    current: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db_dep),
):
    # 1. Validate problem slugs (fail-loud).
    try:
        validate_module_slugs(body.problems)
    except ModuleMappingError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": str(exc),
                "unknown_slugs": exc.unknown_slugs,
            },
        ) from exc

    # 2. Deterministic module selection.
    selections = select_modules(body)
    if not selections:
        # Defensive: select_modules always returns at least one selection
        # given valid input. If this ever fires, it's a content/seed bug.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Rules engine returned no module selections.",
        )

    # 3. Persist assessment + selections.
    asmt = AssessmentRecord(user_id=current.user_id, payload=body)
    await db[Collections.ASSESSMENTS].insert_one(
        asmt.model_dump(mode="json")
    )

    sels_record = AssessmentModuleSelectionsRecord(
        assessment_id=asmt.assessment_id,
        user_id=current.user_id,
        selections=selections,
    )
    await db[Collections.ASSESSMENT_MODULE_SELECTIONS].insert_one(
        sels_record.model_dump(mode="json")
    )

    # 4. Fetch modules in selection order.
    modules = await _fetch_modules_in_order(
        db, [s.module_slug for s in selections]
    )

    # 5. Pure assembly.
    assembled = assemble_blueprint(body, selections, modules)

    # 6. Persist the cached blueprint.
    bp = BlueprintRecord(
        user_id=current.user_id,
        assessment_id=asmt.assessment_id,
        selections_id=sels_record.selections_id,
        assembled_json=assembled,
    )
    await db[Collections.BLUEPRINTS].insert_one(bp.model_dump(mode="json"))

    # 7. Return.
    return AssessmentResponse(
        blueprint_id=bp.blueprint_id,
        assessment_id=asmt.assessment_id,
        assembled_json=assembled,
    )
