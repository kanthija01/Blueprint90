"""FastAPI application factory.

Separating construction from the module-level `app` object lets tests build
independent instances and lets uvicorn import the singleton. The existing
playful `server.py` still exposes `app` for backwards compatibility.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.assessments import router as assessments_router
from api.blueprints import router as blueprints_router
from api.modules import router as modules_router
from auth.routes import router as auth_router
from core.db import Collections, get_async_client, get_db

logger = logging.getLogger(__name__)


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
        # Auth indexes (per integration playbook).
        await db[Collections.USERS].create_index("email", unique=True)
        await db[Collections.USERS].create_index("user_id", unique=True)
        await db[Collections.USER_SESSIONS].create_index(
            "session_token", unique=True
        )
        await db[Collections.USER_SESSIONS].create_index("user_id")
        await db[Collections.USER_SESSIONS].create_index(
            "expires_at", expireAfterSeconds=0
        )
        # Domain indexes for the workflow.
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
        logger.info("Blueprint90 indexes ensured.")

    @app.on_event("shutdown")
    async def _close_mongo():
        get_async_client().close()

    return app
