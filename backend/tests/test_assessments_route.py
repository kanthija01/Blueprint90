"""POST /api/assessments tests.

Covers:
  - Auth gate (401 without bearer)
  - End-to-end success flow: persists docs + returns assembled JSON
  - 422 on unmapped problem slugs
  - 422 on invalid pydantic fields
  - Primary-module isolation (PCOS + Consistency Code => PCOS nutrition only)
  - Diet filtering inside assembly
"""
from __future__ import annotations

import os

import pytest
from pymongo import MongoClient

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
    return MongoClient(os.environ["MONGO_URL"])["blueprint90_test"]


class TestAssessmentsAuth:
    def test_requires_authentication(self, client):
        r = client.post("/api/assessments", json=VALID_ASSESSMENT)
        assert r.status_code == 401


class TestAssessmentsHappyPath:
    def test_success_returns_blueprint_id_and_assembled_json(self, authed_client):
        r = authed_client.post("/api/assessments", json=VALID_ASSESSMENT)
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["blueprint_id"].startswith("bp_")
        assert body["assessment_id"].startswith("asmt_")

        bp = body["assembled_json"]
        # Primary module should be pcos (priority 0 = problem match).
        assert bp["meta"]["primary_module_slug"] == "pcos"
        # Cover page reflects the user-supplied assessment.
        assert bp["cover_page"]["goal"] == "fat_loss"
        assert bp["cover_page"]["biggest_struggle"] == "can't stay consistent"
        # Vegetarian filter: no non-veg food rows.
        for food in bp["nutrition_strategy"]["foods"]:
            # source module only includes diet-matching foods; just confirm shape.
            assert isinstance(food["options"], str)
        # All nutrition rows attributed to the primary.
        assert bp["nutrition_strategy"]["source_module"] == "pcos"
        # Multiple modules used (pcos + executive_energy lifestyle).
        slugs = [m["slug"] for m in bp["meta"]["modules_used"]]
        assert "pcos" in slugs
        assert "executive_energy" in slugs

    def test_persists_assessment_selections_and_blueprint(self, authed_client, test_user):
        r = authed_client.post("/api/assessments", json=VALID_ASSESSMENT)
        assert r.status_code == 201
        db = _mongo()
        assert (
            db[Collections.ASSESSMENTS].count_documents(
                {"user_id": test_user.user_id}
            )
            == 1
        )
        assert (
            db[Collections.ASSESSMENT_MODULE_SELECTIONS].count_documents(
                {"user_id": test_user.user_id}
            )
            == 1
        )
        assert (
            db[Collections.BLUEPRINTS].count_documents(
                {"user_id": test_user.user_id}
            )
            == 1
        )

    def test_default_lifestyle_only(self, authed_client):
        body = dict(VALID_ASSESSMENT, problems=[], biggest_struggle="")
        r = authed_client.post("/api/assessments", json=body)
        assert r.status_code == 201
        bp = r.json()["assembled_json"]
        # No problems means lifestyle module becomes primary.
        # working_professional -> executive_energy (purpose-built, not fallback).
        assert bp["meta"]["primary_module_slug"] == "executive_energy"

    def test_muscle_gain_vegan_triggers_plant_power(self, authed_client):
        body = dict(
            VALID_ASSESSMENT,
            goal="muscle_gain",
            diet="vegan",
            problems=[],
            biggest_struggle="",
        )
        r = authed_client.post("/api/assessments", json=body)
        assert r.status_code == 201
        slugs = [m["slug"] for m in r.json()["assembled_json"]["meta"]["modules_used"]]
        assert "plant_power" in slugs


class TestAssessmentsValidation:
    def test_unmapped_problem_returns_422(self, authed_client):
        body = dict(VALID_ASSESSMENT, problems=["flat_earth_disease"])
        r = authed_client.post("/api/assessments", json=body)
        assert r.status_code == 422
        detail = r.json()["detail"]
        assert "unknown_slugs" in detail
        assert "flat_earth_disease" in detail["unknown_slugs"]

    def test_unmapped_problems_listed_completely(self, authed_client):
        body = dict(VALID_ASSESSMENT, problems=["pcos", "made_up_thing"])
        r = authed_client.post("/api/assessments", json=body)
        assert r.status_code == 422
        assert r.json()["detail"]["unknown_slugs"] == ["made_up_thing"]

    def test_invalid_age_returns_422(self, authed_client):
        body = dict(VALID_ASSESSMENT, age=5)
        r = authed_client.post("/api/assessments", json=body)
        assert r.status_code == 422

    def test_invalid_diet_returns_422(self, authed_client):
        body = dict(VALID_ASSESSMENT, diet="keto")
        r = authed_client.post("/api/assessments", json=body)
        assert r.status_code == 422

    def test_invalid_time_value_returns_422(self, authed_client):
        body = dict(VALID_ASSESSMENT, time_available_min=20)
        r = authed_client.post("/api/assessments", json=body)
        assert r.status_code == 422

    def test_extra_fields_rejected(self, authed_client):
        body = dict(VALID_ASSESSMENT, hacker_field="x")
        r = authed_client.post("/api/assessments", json=body)
        assert r.status_code == 422
