"""Pytest config + shared fixtures.

The HTTP tests run against a SEPARATE Mongo database (`blueprint90_test`)
so they never touch the dev/prod data. Modules are copied from the main DB
into the test DB once per session because the rules engine + assembly
engine depend on the seeded module content.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Make `backend/` importable from anywhere we run pytest.
BACKEND_ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = Path(__file__).resolve().parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

# ----- Switch to a dedicated test database BEFORE any backend module is imported.
# core/db.py reads DB_NAME at import time; this override only affects the in-process
# test run (does not write back to .env).
from dotenv import load_dotenv  # noqa: E402

load_dotenv(BACKEND_ROOT / ".env")
_SOURCE_DB = os.environ.get("DB_NAME", "test_database")
os.environ["DB_NAME"] = "blueprint90_test"
os.environ.setdefault("RAZORPAY_WEBHOOK_SECRET", "whsec_test_blueprint90_local")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from pymongo import MongoClient  # noqa: E402

from app_factory import create_app  # noqa: E402
from auth.dependencies import get_current_user  # noqa: E402
from core.db import Collections  # noqa: E402
from models.user import User  # noqa: E402


# ---------------------------------------------------------------------------
# Session-scoped: ensure modules exist in the test DB.
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def _seed_modules_into_test_db():
    mongo_url = os.environ["MONGO_URL"]
    client = MongoClient(mongo_url)
    src = client[_SOURCE_DB]
    dst = client["blueprint90_test"]

    src_modules = list(src[Collections.MODULES].find({}, {"_id": 0}))
    if not src_modules:
        raise RuntimeError(
            f"Source DB {_SOURCE_DB!r} has no modules. Run scripts/seed_all.py first."
        )
    dst[Collections.MODULES].delete_many({})
    dst[Collections.MODULES].insert_many(src_modules)
    yield
    # No teardown of modules — leaving them speeds up reruns.


# ---------------------------------------------------------------------------
# Per-test: clear domain + auth collections so tests are independent.
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _wipe_per_test():
    mongo_url = os.environ["MONGO_URL"]
    db = MongoClient(mongo_url)["blueprint90_test"]
    for coll in (
        Collections.USERS,
        Collections.USER_SESSIONS,
        Collections.ASSESSMENTS,
        Collections.ASSESSMENT_MODULE_SELECTIONS,
        Collections.BLUEPRINTS,
        Collections.PAYMENTS,
    ):
        db[coll].delete_many({})
    yield


# ---------------------------------------------------------------------------
# App + client fixtures.
# ---------------------------------------------------------------------------
@pytest.fixture()
def app():
    # Reset the cached Motor client so the new app binds to the current
    # event loop. Without this, Motor caches the first loop and subsequent
    # tests see "Event loop is closed".
    import core.db as _core_db
    _core_db._async_client = None
    return create_app()


@pytest.fixture()
def client(app):
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Auth fixtures.
# ---------------------------------------------------------------------------
@pytest.fixture()
def test_user() -> User:
    return User(
        user_id="user_test000001",
        email="alice@example.com",
        name="Alice Tester",
        picture=None,
    )


@pytest.fixture()
def other_user() -> User:
    return User(
        user_id="user_other00002",
        email="bob@example.com",
        name="Bob Other",
        picture=None,
    )


@pytest.fixture()
def authed_client(app, client, test_user):
    """A TestClient where get_current_user is overridden to return `test_user`."""

    async def _override():
        return test_user

    app.dependency_overrides[get_current_user] = _override
    yield client
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def other_authed_client(app, client, test_user, other_user):
    """Returns a helper to switch the authed user on the *same* TestClient.

    Calling `with other_authed_client():` swaps the current dependency
    override to `other_user` for the duration of the block and restores
    the primary override on exit. This avoids spinning up a second
    TestClient (which would create a new event loop and clash with the
    Motor client bound to the first one).
    """
    from contextlib import contextmanager

    @contextmanager
    def _switch():
        async def _override():
            return other_user

        prev = app.dependency_overrides.get(get_current_user)
        app.dependency_overrides[get_current_user] = _override
        try:
            yield client
        finally:
            if prev is not None:
                app.dependency_overrides[get_current_user] = prev
            else:
                app.dependency_overrides.pop(get_current_user, None)

    return _switch



# ---------------------------------------------------------------------------
# Shared test helper: seed a paid payment record and submit an assessment.
#
# Import `seed_paid_payment` from `tests/helpers.py` in individual test
# modules. It is defined there (not here) so it can be imported as a regular
# module without pytest's conftest magic interfering.
# ---------------------------------------------------------------------------
