"""FastAPI application factory.

Separating construction from the module-level `app` object lets tests build
independent instances and lets uvicorn import the singleton. The existing
playful `server.py` still exposes `app` for backwards compatibility.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorDatabase
from starlette.middleware.cors import CORSMiddleware

from api.assessments import router as assessments_router
from api.blueprints import router as blueprints_router
from api.modules import router as modules_router
from api.payments import router as payments_router
from auth.routes import router as auth_router
from core.db import Collections, get_async_client, get_db

logger = logging.getLogger(__name__)


async def _ensure_payments_compound_index(db: AsyncIOMotorDatabase) -> None:
    """Idempotently ensure (user_id, blueprint_id, status) is a sparse index.

    Why this needs special handling
    --------------------------------
    The original code created this index WITHOUT sparse=True.  In the new flow
    blueprint_id is NULL for pre-assessment payments, so the index must be
    sparse (MongoDB only indexes documents where every key is present; a non-
    sparse index on a nullable field blocks bulk inserts when blueprint_id=None
    and more critically cannot be recreated from create_index() once it exists
    under the same auto-generated name with different options — that raises
    IndexKeySpecsConflict code 86 on every restart).

    Strategy
    ---------
    1. Call index_information() to get what MongoDB actually has.
    2. Find the index by key spec (not by name, which is fragile).
    3. If it already has sparse=True → nothing to do (idempotent).
    4. If it exists WITHOUT sparse=True → drop by name, then recreate.
    5. If it does not exist at all → create it.

    Dropping an index never touches documents — it is always safe.
    """
    TARGET_KEY = [("user_id", 1), ("blueprint_id", 1), ("status", 1)]

    existing = await db[Collections.PAYMENTS].index_information()

    matched_name: str | None = None
    matched_is_sparse: bool = False

    for name, info in existing.items():
        if name == "_id_":
            continue
        # Motor returns info["key"] as a list of (field, direction) tuples.
        if list(info["key"]) == TARGET_KEY:
            matched_name = name
            matched_is_sparse = bool(info.get("sparse", False))
            break

    if matched_name is not None and matched_is_sparse:
        # Already correct — nothing to do.
        return

    if matched_name is not None and not matched_is_sparse:
        # Exists with wrong options — drop it so we can recreate correctly.
        logger.info(
            "payments index %r has wrong options (missing sparse=True); "
            "dropping to recreate safely.",
            matched_name,
        )
        await db[Collections.PAYMENTS].drop_index(matched_name)

    await db[Collections.PAYMENTS].create_index(TARGET_KEY, sparse=True)
    logger.info(
        "payments compound index (user_id, blueprint_id, status) "
        "ensured with sparse=True."
    )


def create_app() -> FastAPI:
    app = FastAPI(title="Blueprint90 API", version="0.3.0")

    # Single /api prefix — all routes are scoped here so Kubernetes ingress
    # can route the whole surface to port 8001.
    from fastapi import APIRouter

    api_router = APIRouter(prefix="/api")
    api_router.include_router(auth_router)
    api_router.include_router(assessments_router)
    api_router.include_router(blueprints_router)
    api_router.include_router(modules_router)
    api_router.include_router(payments_router)

    @api_router.get("/health", tags=["meta"])
    async def health():
        return {"status": "ok"}

    app.include_router(api_router)

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def _ensure_indexes():
        db = get_db()

        # Auth indexes.
        await db[Collections.USERS].create_index("email", unique=True)
        await db[Collections.USERS].create_index("user_id", unique=True)
        await db[Collections.USER_SESSIONS].create_index(
            "session_token", unique=True
        )
        await db[Collections.USER_SESSIONS].create_index("user_id")
        await db[Collections.USER_SESSIONS].create_index(
            "expires_at", expireAfterSeconds=0
        )

        # Domain indexes.
        await db[Collections.ASSESSMENTS].create_index("assessment_id", unique=True)
        await db[Collections.ASSESSMENTS].create_index("user_id")
        await db[Collections.ASSESSMENT_MODULE_SELECTIONS].create_index(
            "selections_id", unique=True
        )
        await db[Collections.ASSESSMENT_MODULE_SELECTIONS].create_index(
            "assessment_id"
        )
        await db[Collections.BLUEPRINTS].create_index("blueprint_id", unique=True)
        await db[Collections.BLUEPRINTS].create_index(
            [("user_id", 1), ("created_at", -1)]
        )

        # Payment indexes.
        await db[Collections.PAYMENTS].create_index("payment_id", unique=True)
        await db[Collections.PAYMENTS].create_index(
            "razorpay_order_id", unique=True, sparse=True
        )
        # Handled separately because the old version created this without
        # sparse=True; direct create_index would raise IndexKeySpecsConflict.
        await _ensure_payments_compound_index(db)

        logger.info("Blueprint90 indexes ensured.")

    @app.on_event("shutdown")
    async def _close_mongo():
        get_async_client().close()

    return app
