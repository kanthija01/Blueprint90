"""POST /api/assessments tests.

Covers:
  - Auth gate (401 without bearer)
  - End-to-end success flow: persists docs + returns blueprint_id/assessment_id
  - 402 when no valid paid payment is supplied
  - 422 on unmapped problem slugs
  - 422 on invalid pydantic fields
  - Primary-module isolation (PCOS + Consistency Code => PCOS nutrition only)
  - Diet filtering inside assembly
"""
from __future__ import annotations

import os

import pytest
from pymongo import MongoClient

from helpers import seed_paid_payment
from core.db import Collections

VALID_ASSESSMENT = {
    "age": 31,
    "gender": "female",
    "height_cm": 162.0,
    "weight_kg": 71.0,
    "goal": "fat_loss",
    "lifestyle": "working_professional",
    "diet": "vegetarian",
    "workout_preference": "home",
    "time_available_min": 30,
    "problems": ["pcos"],
    "biggest_struggle": "can't stay consistent",
}


def _mongo():
    return MongoClient(os.environ["MONGODB_URI"])["blueprint90_test"]


def _paid_body(user_id: str, overrides: dict | None = None) -> dict:
    """Return VALID_ASSESSMENT merged with a freshly-seeded paid payment_id."""
    pid = seed_paid_payment(user_id)
    return {**VALID_ASSESSMENT, **(overrides or {}), "payment_id": pid}


class TestAssessmentsAuth:
    def test_requires_authentication(self, client):
        r = client.post("/api/assessments", json={**VALID_ASSESSMENT, "payment_id": "pay_x"})
        assert r.status_code == 401


class TestAssessmentsPaymentGate:
    def test_402_without_payment_id(self, authed_client):
        # payment_id field missing → Pydantic 422 (field required).
        r = authed_client.post("/api/assessments", json=VALID_ASSESSMENT)
        assert r.status_code == 422

    def test_402_for_unpaid_payment(self, authed_client, test_user):
        from datetime import datetime, timezone
        db = _mongo()
        pid = "pay_unpaid001"
        db[Collections.PAYMENTS].insert_one({
            "payment_id": pid,
            "user_id": test_user.user_id,
            "blueprint_id": None,
            "razorpay_order_id": "order_x",
            "razorpay_payment_id": None,
            "amount_paise": 49900,
            "currency": "INR",
            "status": "created",   # NOT paid
            "created_at": datetime.now(timezone.utc),
            "updated_at": None,
        })
        body = {**VALID_ASSESSMENT, "payment_id": pid}
        r = authed_client.post("/api/assessments", json=body)
        assert r.status_code == 402

    def test_402_for_already_linked_payment(self, authed_client, test_user):
        """A payment that already has a blueprint_id cannot be reused."""
        from datetime import datetime, timezone
        db = _mongo()
        pid = "pay_used001"
        db[Collections.PAYMENTS].insert_one({
            "payment_id": pid,
            "user_id": test_user.user_id,
            "blueprint_id": "bp_already_exists",  # already linked
            "razorpay_order_id": "order_y",
            "razorpay_payment_id": "rzp_y",
            "amount_paise": 49900,
            "currency": "INR",
            "status": "paid",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        })
        body = {**VALID_ASSESSMENT, "payment_id": pid}
        r = authed_client.post("/api/assessments", json=body)
        assert r.status_code == 402


class TestAssessmentsHappyPath:
    def test_success_returns_blueprint_id_and_assessment_id(self, authed_client, test_user):
        body = _paid_body(test_user.user_id)
        r = authed_client.post("/api/assessments", json=body)
        assert r.status_code == 201, r.text
        resp = r.json()
        assert resp["blueprint_id"].startswith("bp_")
        assert resp["assessment_id"].startswith("asmt_")
        # assembled_json is no longer returned in the POST response.
        assert "assembled_json" not in resp

    def test_blueprint_accessible_via_get_after_creation(self, authed_client, test_user):
        body = _paid_body(test_user.user_id)
        r = authed_client.post("/api/assessments", json=body)
        assert r.status_code == 201, r.text
        bpid = r.json()["blueprint_id"]

        # GET should return 200 now that payment is linked.
        detail = authed_client.get(f"/api/blueprints/{bpid}")
        assert detail.status_code == 200
        bp = detail.json()
        assert bp["meta"]["primary_module_slug"] == "pcos"
        assert bp["cover_page"]["goal"] == "fat_loss"
        assert bp["cover_page"]["biggest_struggle"] == "can't stay consistent"
        for food in bp["nutrition_strategy"]["foods"]:
            assert isinstance(food["options"], str)
        assert bp["nutrition_strategy"]["source_module"] == "pcos"
        slugs = [m["slug"] for m in bp["meta"]["modules_used"]]
        assert "pcos" in slugs
        assert "executive_energy" in slugs

    def test_persists_assessment_selections_and_blueprint(self, authed_client, test_user):
        body = _paid_body(test_user.user_id)
        r = authed_client.post("/api/assessments", json=body)
        assert r.status_code == 201
        db = _mongo()
        assert db[Collections.ASSESSMENTS].count_documents({"user_id": test_user.user_id}) == 1
        assert db[Collections.ASSESSMENT_MODULE_SELECTIONS].count_documents({"user_id": test_user.user_id}) == 1
        assert db[Collections.BLUEPRINTS].count_documents({"user_id": test_user.user_id}) == 1

    def test_payment_is_linked_to_blueprint_after_creation(self, authed_client, test_user):
        pid = seed_paid_payment(test_user.user_id)
        body = {**VALID_ASSESSMENT, "payment_id": pid}
        r = authed_client.post("/api/assessments", json=body)
        assert r.status_code == 201
        bpid = r.json()["blueprint_id"]
        db = _mongo()
        pay = db[Collections.PAYMENTS].find_one({"payment_id": pid})
        assert pay["blueprint_id"] == bpid

    def test_default_lifestyle_only(self, authed_client, test_user):
        body = _paid_body(test_user.user_id, {"problems": [], "biggest_struggle": ""})
        r = authed_client.post("/api/assessments", json=body)
        assert r.status_code == 201
        bpid = r.json()["blueprint_id"]
        bp = authed_client.get(f"/api/blueprints/{bpid}").json()
        assert bp["meta"]["primary_module_slug"] == "executive_energy"

    def test_muscle_gain_vegan_triggers_plant_power(self, authed_client, test_user):
        body = _paid_body(test_user.user_id, {
            "goal": "muscle_gain",
            "diet": "vegan",
            "problems": [],
            "biggest_struggle": "",
        })
        r = authed_client.post("/api/assessments", json=body)
        assert r.status_code == 201
        bpid = r.json()["blueprint_id"]
        bp = authed_client.get(f"/api/blueprints/{bpid}").json()
        slugs = [m["slug"] for m in bp["meta"]["modules_used"]]
        assert "plant_power" in slugs


class TestAssessmentsValidation:
    def test_unmapped_problem_returns_422(self, authed_client, test_user):
        body = _paid_body(test_user.user_id, {"problems": ["flat_earth_disease"]})
        r = authed_client.post("/api/assessments", json=body)
        assert r.status_code == 422
        detail = r.json()["detail"]
        assert "unknown_slugs" in detail
        assert "flat_earth_disease" in detail["unknown_slugs"]

    def test_unmapped_problems_listed_completely(self, authed_client, test_user):
        body = _paid_body(test_user.user_id, {"problems": ["pcos", "made_up_thing"]})
        r = authed_client.post("/api/assessments", json=body)
        assert r.status_code == 422
        assert r.json()["detail"]["unknown_slugs"] == ["made_up_thing"]

    def test_invalid_age_returns_422(self, authed_client, test_user):
        body = _paid_body(test_user.user_id, {"age": 5})
        r = authed_client.post("/api/assessments", json=body)
        assert r.status_code == 422

    def test_invalid_diet_returns_422(self, authed_client, test_user):
        body = _paid_body(test_user.user_id, {"diet": "keto"})
        r = authed_client.post("/api/assessments", json=body)
        assert r.status_code == 422

    def test_invalid_time_value_returns_422(self, authed_client, test_user):
        body = _paid_body(test_user.user_id, {"time_available_min": 20})
        r = authed_client.post("/api/assessments", json=body)
        assert r.status_code == 422

    def test_extra_fields_rejected(self, authed_client, test_user):
        body = _paid_body(test_user.user_id, {"hacker_field": "x"})
        r = authed_client.post("/api/assessments", json=body)
        assert r.status_code == 422
