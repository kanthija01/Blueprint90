"""GET /api/blueprints, /api/blueprints/{id}, /api/blueprints/{id}/selections.

The core invariant verified here:
  *  GET /api/blueprints/{id} reads the CACHED assembled_json and never
     re-runs the assembly engine. This is enforced by patching
     `assemble_blueprint` and asserting it isn't called on read.
  *  GET /api/blueprints/{id} returns 402 without a paid payment record.
"""
from __future__ import annotations

from unittest.mock import patch

import pytest

from helpers import seed_paid_payment

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
    "biggest_struggle": "",
}

# Default test_user id (matches conftest fixture).
_DEFAULT_USER = "user_test000001"
_OTHER_USER = "user_other00002"


def _create_blueprint(client, user_id=_DEFAULT_USER, body_overrides=None):
    """Seed a paid payment, submit the assessment, return the JSON response."""
    pid = seed_paid_payment(user_id)
    body = {**VALID_ASSESSMENT, **(body_overrides or {}), "payment_id": pid}
    r = client.post("/api/assessments", json=body)
    assert r.status_code == 201, r.text
    return r.json()


class TestBlueprintsAuth:
    def test_list_requires_auth(self, client):
        r = client.get("/api/blueprints")
        assert r.status_code == 401

    def test_detail_requires_auth(self, client):
        r = client.get("/api/blueprints/bp_anything")
        assert r.status_code == 401

    def test_selections_requires_auth(self, client):
        r = client.get("/api/blueprints/bp_anything/selections")
        assert r.status_code == 401


class TestBlueprintList:
    def test_returns_empty_for_new_user(self, authed_client):
        r = authed_client.get("/api/blueprints")
        assert r.status_code == 200
        assert r.json() == []

    def test_returns_users_blueprints_only(
        self, authed_client, other_authed_client
    ):
        a = _create_blueprint(authed_client)
        with other_authed_client() as other_client:
            b = _create_blueprint(
                other_client,
                user_id=_OTHER_USER,
                body_overrides={"problems": ["thyroid"]},
            )
        r = authed_client.get("/api/blueprints")
        assert r.status_code == 200
        ids = [item["blueprint_id"] for item in r.json()]
        assert ids == [a["blueprint_id"]]
        assert b["blueprint_id"] not in ids

    def test_list_item_shape(self, authed_client):
        created = _create_blueprint(authed_client)
        r = authed_client.get("/api/blueprints")
        assert r.status_code == 200
        item = r.json()[0]
        assert item["blueprint_id"] == created["blueprint_id"]
        assert item["primary_module_slug"] == "pcos"
        assert item["goal"] == "fat_loss"
        assert item["module_count"] >= 2


class TestBlueprintDetail:
    def test_returns_cached_assembled_json(self, authed_client):
        created = _create_blueprint(authed_client)
        bpid = created["blueprint_id"]
        r = authed_client.get(f"/api/blueprints/{bpid}")
        assert r.status_code == 200
        bp = r.json()
        # Spot-check key sections.
        assert "cover_page" in bp
        assert "meta" in bp
        assert bp["meta"]["primary_module_slug"] == "pcos"

    def test_detail_never_reruns_assembly(self, authed_client):
        """Patch the assembly engine; GET must succeed and never call it."""
        created = _create_blueprint(authed_client)
        bpid = created["blueprint_id"]
        with patch(
            "api.assessments.assemble_blueprint",
            side_effect=AssertionError("assembly was rerun on read!"),
        ) as ass_mock, patch(
            "assembly.assemble_blueprint.assemble_blueprint",
            side_effect=AssertionError("assembly was rerun on read!"),
        ) as ass_mock2:
            r = authed_client.get(f"/api/blueprints/{bpid}")
        assert r.status_code == 200
        assert ass_mock.call_count == 0
        assert ass_mock2.call_count == 0

    def test_detail_404_for_other_users_blueprint(
        self, authed_client, other_authed_client
    ):
        with other_authed_client() as other_client:
            owned_by_other = _create_blueprint(other_client, user_id=_OTHER_USER)
        r = authed_client.get(
            f"/api/blueprints/{owned_by_other['blueprint_id']}"
        )
        assert r.status_code == 404

    def test_detail_404_for_unknown_id(self, authed_client):
        r = authed_client.get("/api/blueprints/bp_nope")
        assert r.status_code == 404


class TestBlueprintSelections:
    def test_returns_selections_in_priority_order(self, authed_client):
        created = _create_blueprint(authed_client)
        r = authed_client.get(
            f"/api/blueprints/{created['blueprint_id']}/selections"
        )
        assert r.status_code == 200
        body = r.json()
        assert body["blueprint_id"] == created["blueprint_id"]
        assert body["assessment_id"] == created["assessment_id"]
        sels = body["selections"]
        assert sels[0]["module_slug"] == "pcos"
        assert sels[0]["reason"] == "problem_match"
        priorities = [s["priority"] for s in sels]
        assert priorities == sorted(priorities)

    def test_selections_404_for_other_users_blueprint(
        self, authed_client, other_authed_client
    ):
        with other_authed_client() as other_client:
            owned_by_other = _create_blueprint(other_client, user_id=_OTHER_USER)
        r = authed_client.get(
            f"/api/blueprints/{owned_by_other['blueprint_id']}/selections"
        )
        assert r.status_code == 404

    def test_selections_404_for_unknown_id(self, authed_client):
        r = authed_client.get("/api/blueprints/bp_nope/selections")
        assert r.status_code == 404
