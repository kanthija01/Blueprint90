"""Phase 5 contract tests.

The preview UI depends on GET /api/blueprints/{id} returning the cached
`assembled_json` without ever invoking the rules engine or assembly engine.
We re-assert that here plus we verify the fields the preview screen reads.

GET /api/blueprints/{id} now requires a paid payment record (returns 402
otherwise). All tests that read blueprint detail go through _create_blueprint
which seeds a paid pre-assessment payment before submission.
"""
from unittest.mock import patch

from helpers import seed_paid_payment

VALID = {
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

_DEFAULT_USER = "user_test000001"


def _create_blueprint(client, user_id=_DEFAULT_USER, overrides=None):
    pid = seed_paid_payment(user_id)
    body = {**VALID, **(overrides or {}), "payment_id": pid}
    r = client.post("/api/assessments", json=body)
    assert r.status_code == 201, r.text
    return r.json()


class TestPreviewContract:
    def test_detail_reads_cache_not_pipeline(self, authed_client):
        created = _create_blueprint(authed_client)
        bpid = created["blueprint_id"]

        # Patch everything in the assembly pipeline — none should be called
        # on a detail read.
        with patch(
            "api.assessments.assemble_blueprint",
            side_effect=AssertionError("assembly engine called on GET"),
        ), patch(
            "api.assessments.select_modules",
            side_effect=AssertionError("rules engine called on GET"),
        ), patch(
            "api.assessments.validate_module_slugs",
            side_effect=AssertionError("validator called on GET"),
        ):
            r = authed_client.get(f"/api/blueprints/{bpid}")
        assert r.status_code == 200
        body = r.json()
        for key in (
            "cover_page",
            "why_previous_attempts_failed",
            "root_causes",
            "nutrition_strategy",
            "workout_plan",
            "habit_system",
            "psychology_system",
            "faqs",
            "weekly_milestones",
            "progress_tracker",
            "meta",
        ):
            assert key in body, f"cached blueprint missing {key}"
        assert len(body["weekly_milestones"]) == 12
        assert body["progress_tracker"]["weeks"] == list(range(1, 13))

    def test_fallback_module_is_marked_for_ui(self, authed_client):
        created = _create_blueprint(
            authed_client, overrides={"lifestyle": "student", "problems": []}
        )
        bpid = created["blueprint_id"]
        bp = authed_client.get(f"/api/blueprints/{bpid}").json()
        modules = bp["meta"]["modules_used"]
        student_mod = next(m for m in modules if m["slug"] == "dorm_fit")
        assert student_mod["is_fallback"] is True
        assert student_mod["fallback_note"]

    def test_gym_anxiety_attaches_gym_confidence_secondary(self, authed_client):
        created = _create_blueprint(authed_client, overrides={
            "workout_preference": "gym",
            "biggest_struggle": "I'm nervous about going to the gym",
            "problems": [],
        })
        bpid = created["blueprint_id"]
        bp = authed_client.get(f"/api/blueprints/{bpid}").json()
        assert "workout_plan" in bp
        slugs = [m["slug"] for m in bp["meta"]["modules_used"]]
        assert "gym_confidence" in slugs

    def test_detail_returns_consistent_cached_payload_across_reads(
        self, authed_client
    ):
        created = _create_blueprint(authed_client)
        bpid = created["blueprint_id"]
        r1 = authed_client.get(f"/api/blueprints/{bpid}")
        r2 = authed_client.get(f"/api/blueprints/{bpid}")
        assert r1.status_code == 200 and r2.status_code == 200
        assert r1.json() == r2.json()
