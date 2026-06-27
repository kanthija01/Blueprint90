"""POST /api/payments — Razorpay order creation and webhook handling."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
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

WEBHOOK_SECRET = os.environ.get(
    "RAZORPAY_WEBHOOK_SECRET", "whsec_test_blueprint90_local"
)

_DEFAULT_USER = "user_test000001"
_OTHER_USER = "user_other00002"


def _create_blueprint(client, user_id=_DEFAULT_USER, body_overrides=None):
    """Seed a paid payment, submit the assessment, return response JSON."""
    pid = seed_paid_payment(user_id)
    body = {**VALID_ASSESSMENT, **(body_overrides or {}), "payment_id": pid}
    r = client.post("/api/assessments", json=body)
    assert r.status_code == 201, r.text
    return r.json()


def _mock_razorpay_order(order_id="order_test001"):
    return {
        "id": order_id,
        "amount": 49900,
        "currency": "INR",
        "receipt": "pay_stub",
    }


def _sign_webhook(body: bytes) -> str:
    return hmac.new(
        WEBHOOK_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()


def _payment_captured_payload(
    order_id: str, razorpay_payment_id: str = "pay_test001"
) -> dict:
    return {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": razorpay_payment_id,
                    "order_id": order_id,
                    "status": "captured",
                }
            }
        },
    }


def _post_webhook(client, payload: dict, signature: str | None = None):
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if signature is not None:
        headers["X-Razorpay-Signature"] = signature
    return client.post("/api/payments/webhook", content=body, headers=headers)


@pytest.fixture(autouse=True)
def _wipe_cached_pdfs():
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    for pdf in STORAGE_DIR.glob("*.pdf"):
        pdf.unlink()
    yield
    for pdf in STORAGE_DIR.glob("*.pdf"):
        pdf.unlink()


class TestPreAssessmentOrder:
    def test_requires_auth(self, client):
        r = client.post("/api/payments/create-pre-assessment-order")
        assert r.status_code == 401

    def test_creates_order(self, authed_client):
        with patch(
            "payments.razorpay_client.create_order",
            return_value=_mock_razorpay_order("order_pre001"),
        ) as mock:
            r = authed_client.post("/api/payments/create-pre-assessment-order")
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["razorpay_order_id"] == "order_pre001"
        assert body["amount"] == 49900
        assert body["key_id"]
        assert body["payment_id"].startswith("pay_")
        mock.assert_called_once()
        # blueprint_id must be NULL in DB for a pre-assessment order.
        db = MongoClient(os.environ["MONGODB_URI"])["blueprint90_test"]
        row = db[Collections.PAYMENTS].find_one({"payment_id": body["payment_id"]})
        assert row["blueprint_id"] is None
        assert row["status"] == "created"


class TestPaymentStatusPoll:
    def test_requires_auth(self, client):
        r = client.get("/api/payments/status/pay_anything")
        assert r.status_code == 401

    def test_returns_status(self, authed_client, test_user):
        pid = seed_paid_payment(test_user.user_id)
        r = authed_client.get(f"/api/payments/status/{pid}")
        assert r.status_code == 200
        assert r.json()["status"] == "paid"

    def test_404_for_unknown_payment(self, authed_client):
        r = authed_client.get("/api/payments/status/pay_nope")
        assert r.status_code == 404


class TestCreateOrder:
    def test_requires_auth(self, client):
        r = client.post(
            "/api/payments/create-order",
            json={"blueprint_id": "bp_anything"},
        )
        assert r.status_code == 401

    def test_creates_order_for_owner(self, authed_client):
        # Insert a blueprint directly — no payment record yet — so create-order works.
        from datetime import datetime, timezone
        from pymongo import MongoClient as MC
        db = MC(os.environ["MONGODB_URI"])["blueprint90_test"]
        bpid = "bp_order_test001"
        db[Collections.BLUEPRINTS].insert_one({
            "blueprint_id": bpid,
            "user_id": _DEFAULT_USER,
            "assessment_id": "asmt_order_test001",
            "selections_id": "sels_order_test001",
            "assembled_json": {"meta": {}, "cover_page": {}},
            "created_at": datetime.now(timezone.utc),
        })

        with patch(
            "payments.razorpay_client.create_order",
            return_value=_mock_razorpay_order("order_abc123"),
        ) as create_mock:
            r = authed_client.post(
                "/api/payments/create-order",
                json={"blueprint_id": bpid},
            )

        assert r.status_code == 200, r.text
        body = r.json()
        assert body["razorpay_order_id"] == "order_abc123"
        assert body["amount"] == 49900
        assert body["currency"] == "INR"
        assert body["key_id"]
        assert body["payment_id"].startswith("pay_")

        create_mock.assert_called_once()
        call_kwargs = create_mock.call_args.kwargs
        assert call_kwargs["receipt"] == body["payment_id"]
        assert call_kwargs["notes"]["blueprint_id"] == bpid

        db2 = MongoClient(os.environ["MONGODB_URI"])["blueprint90_test"]
        row = db2[Collections.PAYMENTS].find_one(
            {"payment_id": body["payment_id"]}, {"_id": 0}
        )
        assert row is not None
        assert row["status"] == "created"
        assert row["razorpay_order_id"] == "order_abc123"
        assert row["blueprint_id"] == bpid
        assert row["user_id"] == _DEFAULT_USER

    def test_409_when_already_paid(self, authed_client):
        """create-order returns 409 when a paid payment already exists for the blueprint."""
        created = _create_blueprint(authed_client)
        bpid = created["blueprint_id"]
        with patch(
            "payments.razorpay_client.create_order",
            return_value=_mock_razorpay_order(),
        ):
            r = authed_client.post(
                "/api/payments/create-order",
                json={"blueprint_id": bpid},
            )
        assert r.status_code == 409

    def test_404_for_unknown_blueprint(self, authed_client):
        with patch(
            "payments.razorpay_client.create_order",
            return_value=_mock_razorpay_order(),
        ):
            r = authed_client.post(
                "/api/payments/create-order",
                json={"blueprint_id": "bp_nope"},
            )
        assert r.status_code == 404

    def test_404_for_other_users_blueprint(
        self, authed_client, other_authed_client
    ):
        with other_authed_client() as other_client:
            owned = _create_blueprint(other_client, user_id=_OTHER_USER)

        with patch(
            "payments.razorpay_client.create_order",
            return_value=_mock_razorpay_order(),
        ):
            r = authed_client.post(
                "/api/payments/create-order",
                json={"blueprint_id": owned["blueprint_id"]},
            )
        assert r.status_code == 404


class TestWebhook:
    def test_invalid_signature_rejected(self, client):
        payload = _payment_captured_payload("order_any")
        r = _post_webhook(client, payload, signature="bad_sig")
        assert r.status_code == 400
        assert "signature" in r.json()["detail"].lower()

    def test_payment_captured_marks_paid(self, authed_client):
        # Insert a raw blueprint without any payment record.
        from datetime import datetime, timezone
        from pymongo import MongoClient as MC
        db = MC(os.environ["MONGODB_URI"])["blueprint90_test"]
        bpid = "bp_webhook_test001"
        db[Collections.BLUEPRINTS].insert_one({
            "blueprint_id": bpid,
            "user_id": _DEFAULT_USER,
            "assessment_id": "asmt_wh001",
            "selections_id": "sels_wh001",
            "assembled_json": {"meta": {}, "cover_page": {}},
            "created_at": datetime.now(timezone.utc),
        })

        with patch(
            "payments.razorpay_client.create_order",
            return_value=_mock_razorpay_order("order_capture01"),
        ):
            order_r = authed_client.post(
                "/api/payments/create-order",
                json={"blueprint_id": bpid},
            )
        assert order_r.status_code == 200, order_r.text
        payment_id = order_r.json()["payment_id"]

        payload = _payment_captured_payload(
            "order_capture01", razorpay_payment_id="pay_captured01"
        )
        body = json.dumps(payload).encode("utf-8")
        r = authed_client.post(
            "/api/payments/webhook",
            content=body,
            headers={
                "Content-Type": "application/json",
                "X-Razorpay-Signature": _sign_webhook(body),
            },
        )
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

        db2 = MongoClient(os.environ["MONGODB_URI"])["blueprint90_test"]
        row = db2[Collections.PAYMENTS].find_one({"payment_id": payment_id})
        assert row["status"] == "paid"
        assert row["razorpay_payment_id"] == "pay_captured01"
        assert row["updated_at"] is not None


class TestPdfGating:
    def test_pdf_402_without_payment(self, authed_client):
        """A blueprint with no payment record returns 402 on the PDF route."""
        insert_stub_blueprint("bp_nopay_gate", _DEFAULT_USER)
        r = authed_client.get("/api/blueprints/bp_nopay_gate/pdf")
        assert r.status_code == 402
        assert r.json()["detail"] == "Payment required"

    def test_pdf_unlocked_after_webhook_capture(self, authed_client):
        """After webhook marks order as paid, PDF route returns 200."""
        insert_stub_blueprint("bp_pdf_gate_unlock", _DEFAULT_USER)

        with patch(
            "payments.razorpay_client.create_order",
            return_value=_mock_razorpay_order("order_pdf_gate"),
        ):
            authed_client.post(
                "/api/payments/create-order",
                json={"blueprint_id": "bp_pdf_gate_unlock"},
            )

        payload = _payment_captured_payload("order_pdf_gate")
        body = json.dumps(payload).encode("utf-8")
        authed_client.post(
            "/api/payments/webhook",
            content=body,
            headers={
                "Content-Type": "application/json",
                "X-Razorpay-Signature": _sign_webhook(body),
            },
        )

        with patch("api.blueprints.generate_blueprint_pdf") as gen_mock:
            def _write_pdf(bp, output_path=None, blueprint_id=None):
                from pathlib import Path
                Path(output_path).write_bytes(b"%PDF-1.4 unlocked")
                return Path(output_path)
            gen_mock.side_effect = _write_pdf
            r = authed_client.get("/api/blueprints/bp_pdf_gate_unlock/pdf")
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/pdf"
        assert r.content[:4] == b"%PDF"

    def test_created_order_does_not_unlock_pdf(self, authed_client):
        """Only webhook-confirmed `paid` status unlocks PDF — not order creation."""
        insert_stub_blueprint("bp_created_only", _DEFAULT_USER)

        with patch(
            "payments.razorpay_client.create_order",
            return_value=_mock_razorpay_order("order_not_paid"),
        ):
            authed_client.post(
                "/api/payments/create-order",
                json={"blueprint_id": "bp_created_only"},
            )

        r = authed_client.get("/api/blueprints/bp_created_only/pdf")
        assert r.status_code == 402
