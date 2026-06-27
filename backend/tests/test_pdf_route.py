"""GET /api/blueprints/{id}/pdf — cached ReportLab PDF generation."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest
from pymongo import MongoClient

from helpers import seed_paid_payment, insert_stub_blueprint
from core.db import Collections
from pdf.generate import STORAGE_DIR

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

_DEFAULT_USER = "user_test000001"
_OTHER_USER = "user_other00002"


def _create_blueprint(client, user_id=_DEFAULT_USER, body=None):
    pid = seed_paid_payment(user_id)
    r = client.post("/api/assessments", json={**(body or VALID_ASSESSMENT), "payment_id": pid})
    assert r.status_code == 201, r.text
    return r.json()


def _insert_paid_payment(blueprint_id: str, user_id: str = _DEFAULT_USER):
    """Insert a standalone paid payment record for PDF unlock (legacy flow)."""
    db = MongoClient(os.environ["MONGODB_URI"])["blueprint90_test"]
    db[Collections.PAYMENTS].insert_one(
        {
            "payment_id": f"pay_pdf_{blueprint_id[-8:]}",
            "user_id": user_id,
            "blueprint_id": blueprint_id,
            "razorpay_order_id": f"order_{blueprint_id[-8:]}",
            "razorpay_payment_id": "pay_test_pdf",
            "amount_paise": 49900,
            "currency": "INR",
            "status": "paid",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )


@pytest.fixture(autouse=True)
def _wipe_cached_pdfs():
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    for pdf in STORAGE_DIR.glob("*.pdf"):
        pdf.unlink()
    yield
    for pdf in STORAGE_DIR.glob("*.pdf"):
        pdf.unlink()


class TestBlueprintPdfAuth:
    def test_pdf_requires_auth(self, client):
        r = client.get("/api/blueprints/bp_anything/pdf")
        assert r.status_code == 401


class TestBlueprintPdf:
    def test_pdf_402_without_payment(self, authed_client):
        """A blueprint with no paid payment record returns 402."""
        insert_stub_blueprint("bp_nopay_pdf", _DEFAULT_USER)
        r = authed_client.get("/api/blueprints/bp_nopay_pdf/pdf")
        assert r.status_code == 402

    def test_returns_pdf_for_owner(self, authed_client):
        created = _create_blueprint(authed_client)
        bpid = created["blueprint_id"]
        # Mock PDF generation to avoid ReportLab layout constraints in tests.
        with patch("api.blueprints.generate_blueprint_pdf") as gen_mock:
            def _write_pdf(bp, output_path=None, blueprint_id=None):
                Path(output_path).write_bytes(b"%PDF-1.4 test")
                return Path(output_path)
            gen_mock.side_effect = _write_pdf
            r = authed_client.get(f"/api/blueprints/{bpid}/pdf")
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/pdf"
        assert r.content[:4] == b"%PDF"

    def test_pdf_uses_cached_file_on_second_request(self, authed_client):
        created = _create_blueprint(authed_client)
        bpid = created["blueprint_id"]
        pdf_path = STORAGE_DIR / f"{bpid}.pdf"

        with patch("api.blueprints.generate_blueprint_pdf") as gen_mock:
            def _write_pdf(bp, output_path=None, blueprint_id=None):
                Path(output_path).write_bytes(b"%PDF-1.4 cached")
                return Path(output_path)

            gen_mock.side_effect = _write_pdf
            r1 = authed_client.get(f"/api/blueprints/{bpid}/pdf")
            assert r1.status_code == 200
            assert gen_mock.call_count == 1

            r2 = authed_client.get(f"/api/blueprints/{bpid}/pdf")
            assert r2.status_code == 200
            assert gen_mock.call_count == 1
            assert r2.content == r1.content

        assert pdf_path.is_file()

    def test_pdf_never_reruns_assembly(self, authed_client):
        created = _create_blueprint(authed_client)
        bpid = created["blueprint_id"]
        with patch(
            "api.assessments.assemble_blueprint",
            side_effect=AssertionError("assembly was rerun on pdf!"),
        ), patch(
            "assembly.assemble_blueprint.assemble_blueprint",
            side_effect=AssertionError("assembly was rerun on pdf!"),
        ), patch("api.blueprints.generate_blueprint_pdf") as gen_mock:
            def _write_pdf(bp, output_path=None, blueprint_id=None):
                Path(output_path).write_bytes(b"%PDF-1.4 noregen")
                return Path(output_path)
            gen_mock.side_effect = _write_pdf
            r = authed_client.get(f"/api/blueprints/{bpid}/pdf")
        assert r.status_code == 200
        assert r.content[:4] == b"%PDF"

    def test_pdf_404_for_other_users_blueprint(
        self, authed_client, other_authed_client
    ):
        with other_authed_client() as other_client:
            owned_by_other = _create_blueprint(other_client, user_id=_OTHER_USER)
        r = authed_client.get(
            f"/api/blueprints/{owned_by_other['blueprint_id']}/pdf"
        )
        assert r.status_code == 404

    def test_pdf_404_for_unknown_id(self, authed_client):
        r = authed_client.get("/api/blueprints/bp_nope/pdf")
        assert r.status_code == 404
