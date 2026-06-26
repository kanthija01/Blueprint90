"""POST /api/payments/create-pre-assessment-order  — create a Razorpay order
       BEFORE the assessment is submitted (new flow).
POST /api/payments/verify        — verify payment using Razorpay callback params
                                   (primary path, works without a public webhook URL).
POST /api/payments/create-order  — legacy PDF-unlock for existing blueprints.
POST /api/payments/webhook       — HMAC-verified webhook (secondary path, requires
                                   publicly reachable URL).
GET  /api/payments/status/{payment_id} — poll payment status from client.

How payment verification works
--------------------------------
Razorpay sends three values to the client-side success handler:
  razorpay_payment_id, razorpay_order_id, razorpay_signature

The signature is HMAC-SHA256 of "{order_id}|{payment_id}" using the
KEY SECRET (not the webhook secret).  We re-compute and compare — if they
match the payment is authentic and we mark it as paid in MongoDB.

This lets the flow work in local dev without needing a publicly reachable
webhook URL.  The webhook endpoint is kept as a secondary path for production.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel

from auth.dependencies import get_current_user, get_db_dep
from core.db import Collections
from models.api import (
    CreateOrderRequest,
    CreateOrderResponse,
    CreatePreAssessmentOrderResponse,
    PaymentRecord,
)
from models.user import User
from payments import razorpay_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["payments"])


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Request model for the verify endpoint
# ---------------------------------------------------------------------------
class VerifyPaymentRequest(BaseModel):
    payment_id: str           # our internal payment_id (from create-pre-assessment-order)
    razorpay_payment_id: str  # from Razorpay checkout success handler
    razorpay_order_id: str    # from Razorpay checkout success handler
    razorpay_signature: str   # from Razorpay checkout success handler


@router.post(
    "/create-pre-assessment-order",
    response_model=CreatePreAssessmentOrderResponse,
)
async def create_pre_assessment_order(
    current: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db_dep),
):
    """Create a Razorpay order BEFORE blueprint generation.

    The payment record is persisted with blueprint_id=None.  After the user
    pays and verify is called, status flips to "paid".  The client then calls
    POST /api/assessments with this payment_id.
    """
    record = PaymentRecord(
        user_id=current.user_id,
        blueprint_id=None,
        amount_paise=razorpay_client.BLUEPRINT_PRICE_PAISE,
        currency=razorpay_client.CURRENCY,
        status="created",
    )

    order = razorpay_client.create_order(
        receipt=record.payment_id,
        notes={
            "user_id": current.user_id,
            "payment_id": record.payment_id,
            "type": "pre_assessment",
        },
    )
    record.razorpay_order_id = order["id"]

    await db[Collections.PAYMENTS].insert_one(
        record.model_dump(mode="json")
    )

    logger.info(
        "[payment] order created: payment_id=%s razorpay_order_id=%s user=%s",
        record.payment_id,
        record.razorpay_order_id,
        current.user_id,
    )

    return CreatePreAssessmentOrderResponse(
        payment_id=record.payment_id,
        razorpay_order_id=record.razorpay_order_id,
        amount=record.amount_paise,
        currency=record.currency,
        key_id=razorpay_client.key_id(),
    )


@router.post("/verify")
async def verify_payment(
    body: VerifyPaymentRequest,
    current: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db_dep),
):
    """Verify a Razorpay payment using the client-side callback parameters.

    Razorpay's checkout.js calls the handler with:
        { razorpay_payment_id, razorpay_order_id, razorpay_signature }

    The signature is HMAC-SHA256("{order_id}|{payment_id}", key_secret).
    We recompute it and compare.  On success we mark the payment as paid.

    This endpoint is the PRIMARY verification path and works in any
    environment — it does not require a publicly reachable webhook URL.
    """
    logger.info(
        "[payment] verify called: payment_id=%s razorpay_payment_id=%s user=%s",
        body.payment_id,
        body.razorpay_payment_id,
        current.user_id,
    )

    # 1. Look up our payment record — must be owned by this user.
    record = await db[Collections.PAYMENTS].find_one(
        {
            "payment_id": body.payment_id,
            "user_id": current.user_id,
        },
        {"_id": 0, "status": 1, "razorpay_order_id": 1},
    )
    if not record:
        logger.warning(
            "[payment] verify: payment_id=%s not found for user=%s",
            body.payment_id,
            current.user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    # 2. If already paid, return success immediately (idempotent).
    if record["status"] == "paid":
        logger.info(
            "[payment] verify: payment_id=%s already paid, skipping",
            body.payment_id,
        )
        return {"status": "paid"}

    # 3. Verify the order_id matches what we stored (prevents substitution attacks).
    if record.get("razorpay_order_id") != body.razorpay_order_id:
        logger.warning(
            "[payment] verify: order_id mismatch for payment_id=%s "
            "stored=%s received=%s",
            body.payment_id,
            record.get("razorpay_order_id"),
            body.razorpay_order_id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order ID mismatch",
        )

    # 4. Verify Razorpay signature.
    # Razorpay signs: "{razorpay_order_id}|{razorpay_payment_id}" with key_secret.
    message = f"{body.razorpay_order_id}|{body.razorpay_payment_id}"
    expected = hmac.new(
        razorpay_client.key_secret().encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, body.razorpay_signature):
        logger.warning(
            "[payment] verify: signature mismatch for payment_id=%s",
            body.payment_id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid payment signature",
        )

    logger.info(
        "[payment] verify: signature valid for payment_id=%s",
        body.payment_id,
    )

    # 5. Mark payment as paid in MongoDB.
    result = await db[Collections.PAYMENTS].update_one(
        {"payment_id": body.payment_id, "user_id": current.user_id, "status": "created"},
        {
            "$set": {
                "status": "paid",
                "razorpay_payment_id": body.razorpay_payment_id,
                "updated_at": _now(),
            }
        },
    )

    if result.modified_count == 0:
        # Race condition: another request already updated it — still fine.
        logger.info(
            "[payment] verify: no document updated (race or already paid) for payment_id=%s",
            body.payment_id,
        )
    else:
        logger.info(
            "[payment] verify: MongoDB updated to paid for payment_id=%s",
            body.payment_id,
        )

    return {"status": "paid"}


@router.get("/status/{payment_id}")
async def get_payment_status(
    payment_id: str,
    current: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db_dep),
):
    """Poll payment status. Returns { status: 'created' | 'paid' }."""
    record = await db[Collections.PAYMENTS].find_one(
        {"payment_id": payment_id, "user_id": current.user_id},
        {"_id": 0, "status": 1},
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )
    logger.info(
        "[payment] status poll: payment_id=%s status=%s user=%s",
        payment_id,
        record["status"],
        current.user_id,
    )
    return {"status": record["status"]}


@router.post("/create-order", response_model=CreateOrderResponse)
async def create_order(
    body: CreateOrderRequest,
    current: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db_dep),
):
    """Create a Razorpay order for blueprint access / PDF unlock.

    Handles stuck payments: if a previous 'created' order was never completed
    (razorpay_payment_id is null), it is marked 'expired' so a fresh order can
    be issued.  This covers the case where the user closed Razorpay without
    paying, or the old code discarded the callback params.

    Rules:
      - status="paid"     → 409 (already paid, nothing to do)
      - status="created"  → expire it, create a new order
      - no existing record → create a new order
    """
    # Verify the blueprint exists and belongs to this user.
    bp = await db[Collections.BLUEPRINTS].find_one(
        {"blueprint_id": body.blueprint_id, "user_id": current.user_id},
        {"_id": 0, "blueprint_id": 1},
    )
    if not bp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blueprint not found",
        )

    # Check for an already-paid record — nothing more to do.
    existing_paid = await db[Collections.PAYMENTS].find_one(
        {
            "blueprint_id": body.blueprint_id,
            "user_id": current.user_id,
            "status": "paid",
        },
        {"_id": 0, "payment_id": 1},
    )
    if existing_paid:
        logger.info(
            "[payment] create-order: blueprint %s already paid (payment_id=%s), returning 409",
            body.blueprint_id,
            existing_paid["payment_id"],
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Blueprint already paid",
        )

    # Find any stuck 'created' record (never completed).
    existing_stuck = await db[Collections.PAYMENTS].find_one(
        {
            "blueprint_id": body.blueprint_id,
            "user_id": current.user_id,
            "status": "created",
        },
        {"_id": 0, "payment_id": 1, "razorpay_order_id": 1, "razorpay_payment_id": 1},
    )
    if existing_stuck:
        logger.info(
            "[payment] create-order: found stuck payment payment_id=%s "
            "(razorpay_payment_id=%s) for blueprint %s — expiring it",
            existing_stuck["payment_id"],
            existing_stuck.get("razorpay_payment_id"),
            body.blueprint_id,
        )
        # Mark it expired so it no longer interferes, but keep it for audit.
        await db[Collections.PAYMENTS].update_one(
            {"payment_id": existing_stuck["payment_id"]},
            {"$set": {"status": "expired", "updated_at": _now()}},
        )
        logger.info(
            "[payment] create-order: payment_id=%s marked expired",
            existing_stuck["payment_id"],
        )

    # Create a fresh order.
    record = PaymentRecord(
        user_id=current.user_id,
        blueprint_id=body.blueprint_id,
        amount_paise=razorpay_client.BLUEPRINT_PRICE_PAISE,
        currency=razorpay_client.CURRENCY,
        status="created",
    )

    order = razorpay_client.create_order(
        receipt=record.payment_id,
        notes={
            "blueprint_id": body.blueprint_id,
            "user_id": current.user_id,
            "payment_id": record.payment_id,
        },
    )
    record.razorpay_order_id = order["id"]

    await db[Collections.PAYMENTS].insert_one(
        record.model_dump(mode="json")
    )

    logger.info(
        "[payment] create-order: new order created payment_id=%s "
        "razorpay_order_id=%s for blueprint %s",
        record.payment_id,
        record.razorpay_order_id,
        body.blueprint_id,
    )

    return CreateOrderResponse(
        payment_id=record.payment_id,
        razorpay_order_id=record.razorpay_order_id,
        amount=record.amount_paise,
        currency=record.currency,
        key_id=razorpay_client.key_id(),
    )


@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db_dep),
):
    """Razorpay webhook — secondary verification path.

    Requires a publicly reachable URL configured in the Razorpay dashboard.
    The primary path is POST /api/payments/verify which works everywhere.
    """
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    logger.info("[payment] webhook received, event signature present: %s", bool(signature))

    if not razorpay_client.verify_webhook_signature(body, signature):
        logger.warning("[payment] webhook: invalid signature")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature",
        )

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook payload",
        )

    event = payload.get("event")
    logger.info("[payment] webhook event: %s", event)

    if event != "payment.captured":
        return {"status": "ignored", "event": event}

    entity = payload["payload"]["payment"]["entity"]
    order_id = entity["order_id"]
    razorpay_payment_id = entity["id"]

    result = await db[Collections.PAYMENTS].update_one(
        {"razorpay_order_id": order_id, "status": "created"},
        {
            "$set": {
                "status": "paid",
                "razorpay_payment_id": razorpay_payment_id,
                "updated_at": _now(),
            }
        },
    )

    if result.matched_count == 0:
        logger.warning(
            "[payment] webhook: payment.captured for unknown or already-paid order %s",
            order_id,
        )
    else:
        logger.info(
            "[payment] webhook: marked paid via webhook for order %s",
            order_id,
        )

    return {"status": "ok"}
