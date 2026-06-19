"""GET /api/modules tests.
"""
from __future__ import annotations


class TestModulesRoute:
    def test_requires_auth(self, client):
        r = client.get("/api/modules")
        assert r.status_code == 401

    def test_lists_all_seeded_modules(self, authed_client):
        r = authed_client.get("/api/modules")
        assert r.status_code == 200
        body = r.json()
        slugs = {m["slug"] for m in body}
        # The 14 seeded modules we expect from Phase 0.
        expected = {
            "back_strong",
            "beginner_boost",
            "calm_strength",
            "consistency_code",
            "dorm_fit",
            "emotional_eating_reset",
            "executive_energy",
            "gym_confidence",
            "knee_safe_strength",
            "mom_strong",
            "pcos",
            "plant_power",
            "plateau_breaker",
            "thyroid",
        }
        assert expected.issubset(slugs), f"missing: {expected - slugs}"

    def test_item_shape(self, authed_client):
        r = authed_client.get("/api/modules")
        body = r.json()
        pcos = next(m for m in body if m["slug"] == "pcos")
        # Required fields surface.
        assert isinstance(pcos["display_name"], str) and pcos["display_name"]
        assert "is_authored_extension" in pcos
        assert "content_pending" in pcos

    def test_sorted_by_slug(self, authed_client):
        r = authed_client.get("/api/modules")
        slugs = [m["slug"] for m in r.json()]
        assert slugs == sorted(slugs)
