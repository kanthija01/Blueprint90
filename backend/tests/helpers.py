"""Shared test helpers — imported by individual test modules."""
from __future__ import annotations

import os
from datetime import datetime, timezone

from pymongo import MongoClient

from core.db import Collections
from models.api import _mkid


# Minimal valid assembled_json that satisfies AssembledBlueprint Pydantic validation.
# Used by tests that need a blueprint stub without going through the full
# assessment → assembly pipeline.
MINIMAL_ASSEMBLED_JSON = {
    "cover_page": {
        "goal": "fat_loss",
        "duration_days": 90,
        "generated_at": "2026-01-01T00:00:00+00:00",
    },
    "why_previous_attempts_failed": [],
    "root_causes": [],
    "nutrition_strategy": {
        "diet": "vegetarian",
        "targets": [],
        "foods": [],
        "foods_to_avoid": [],
        "meal_ideas": [],
        "source_module": "stub",
    },
    "workout_plan": None,
    "habit_system": [],
    "psychology_system": {"common_thoughts": [], "techniques": []},
    "faqs": [],
    "plateau_playbook": [],
    "weekly_milestones": [],
    "progress_tracker": {"columns": [], "weeks": []},
    "meta": {
        "modules_used": [],
        "assembled_at": "2026-01-01T00:00:00+00:00",
        "primary_module_slug": "stub",
    },
}


def seed_paid_payment(user_id: str, payment_id: str | None = None) -> str:
    """Insert a paid pre-assessment PaymentRecord (blueprint_id=None) into
    the test DB and return the payment_id.

    This bypasses Razorpay entirely — tests inject a pre-paid record directly
    into Mongo, then pass the payment_id to POST /api/assessments.
    """
    pid = payment_id or _mkid("pay")
    db = MongoClient(os.environ["MONGO_URL"])["blueprint90_test"]
    db[Collections.PAYMENTS].insert_one(
        {
            "payment_id": pid,
            "user_id": user_id,
            "blueprint_id": None,
            "razorpay_order_id": f"order_test_{pid[-6:]}",
            "razorpay_payment_id": f"rzp_test_{pid[-6:]}",
            "amount_paise": 49900,
            "currency": "INR",
            "status": "paid",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )
    return pid


def insert_stub_blueprint(
    blueprint_id: str,
    user_id: str,
    *,
    assembled_json: dict | None = None,
) -> None:
    """Insert a blueprint document directly into the test DB.
    Uses MINIMAL_ASSEMBLED_JSON by default — valid but content-free.
    No payment record is created, so PDF/detail routes will return 402
    unless a payment is separately inserted or linked.
    """
    db = MongoClient(os.environ["MONGO_URL"])["blueprint90_test"]
    db[Collections.BLUEPRINTS].insert_one({
        "blueprint_id": blueprint_id,
        "user_id": user_id,
        "assessment_id": f"asmt_{blueprint_id[-8:]}",
        "selections_id": f"sels_{blueprint_id[-8:]}",
        "assembled_json": assembled_json or MINIMAL_ASSEMBLED_JSON,
        "created_at": datetime.now(timezone.utc),
    })
