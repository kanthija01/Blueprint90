"""MongoDB connection — single source of truth for the Mongo client + collection accessors.

No business logic lives here. The rules engine and assembly engine are intentionally
isolated from this module so they remain pure / testable.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient  # sync client used by the seed script only

# Load backend/.env (MONGODB_URI, DB_NAME). Loading here so any importer of this
# module gets a guaranteed-initialised environment.
BACKEND_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_ROOT / ".env")


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable {name!r}. "
            f"Check {BACKEND_ROOT / '.env'}."
        )
    return value


# MONGODB_URI — matches Render's built-in env var name for MongoDB Atlas.
# Set this in your Render dashboard (or .env for local dev).
MONGO_URL = _require("MONGODB_URI")
DB_NAME = _require("DB_NAME")


# ----- Async client (used by FastAPI routes) -----------------------------------
_async_client: Optional[AsyncIOMotorClient] = None


def get_async_client() -> AsyncIOMotorClient:
    global _async_client
    if _async_client is None:
        _async_client = AsyncIOMotorClient(MONGO_URL)
    return _async_client


def get_db() -> AsyncIOMotorDatabase:
    return get_async_client()[DB_NAME]


# ----- Sync client (used ONLY by seed scripts / one-off CLIs) -----------------
def get_sync_db():
    """Sync Mongo handle for seed scripts. Do not call from FastAPI request paths."""
    client = MongoClient(MONGO_URL)
    return client[DB_NAME]


# ----- Collection names (single source of truth, no magic strings elsewhere) ---
class Collections:
    MODULES = "modules"
    MODULE_FALLBACK_MAP = "module_fallback_map"
    USERS = "users"
    USER_SESSIONS = "user_sessions"
    ASSESSMENTS = "assessments"
    ASSESSMENT_MODULE_SELECTIONS = "assessment_module_selections"
    BLUEPRINTS = "blueprints"
    PAYMENTS = "payments"
