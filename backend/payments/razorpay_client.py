"""Razorpay test-mode client helpers.

Webhook HMAC verification is the source of truth for payment status — never
trust client-side success callbacks.
"""
from __future__ import annotations

import hashlib
import hmac
import os
from pathlib import Path
from typing import Any, Dict

import razorpay
from dotenv import load_dotenv

BACKEND_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_ROOT / ".env")

# ₹499 — blueprint PDF unlock price (test mode).
BLUEPRINT_PRICE_PAISE = 49900
CURRENCY = "INR"


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable {name!r}. "
            f"Check {BACKEND_ROOT / '.env'}."
        )
    return value


def key_id() -> str:
    return _require("RAZORPAY_KEY_ID")


def key_secret() -> str:
    return _require("RAZORPAY_KEY_SECRET")


def webhook_secret() -> str:
    return _require("RAZORPAY_WEBHOOK_SECRET")


def get_client() -> razorpay.Client:
    return razorpay.Client(auth=(key_id(), key_secret()))


def create_order(*, receipt: str, notes: Dict[str, str]) -> Dict[str, Any]:
    """Create a Razorpay order in test mode."""
    return get_client().order.create(
        {
            "amount": BLUEPRINT_PRICE_PAISE,
            "currency": CURRENCY,
            "receipt": receipt,
            "notes": notes,
        }
    )


def verify_webhook_signature(body: bytes, signature: str) -> bool:
    """Verify Razorpay webhook `X-Razorpay-Signature` header."""
    if not signature:
        return False
    expected = hmac.new(
        webhook_secret().encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
