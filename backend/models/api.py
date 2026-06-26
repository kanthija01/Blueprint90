"""Persistence helpers + API request/response models shared across routes.

Kept separate from the rules-engine `types.py` because that file is the
authoritative *decision-time* shape — we don't want HTTP concerns leaking
into pure functions.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from models.blueprint import AssembledBlueprint
from rules_engine.types import Assessment, ModuleSelection


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _mkid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


# ---------- POST /api/assessments ---------------------------------------
class AssessmentRequest(Assessment):
    """Same shape as the rules-engine `Assessment`, used as the FastAPI
    request body so validation is single-sourced.
    `payment_id` must reference a *paid* pre-assessment payment record."""
    payment_id: str


class AssessmentResponse(BaseModel):
    blueprint_id: str
    assessment_id: str


# ---------- Persisted documents ----------------------------------------
class AssessmentRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assessment_id: str = Field(default_factory=lambda: _mkid("asmt"))
    user_id: str
    payload: Assessment
    created_at: datetime = Field(default_factory=_now)


class AssessmentModuleSelectionsRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    selections_id: str = Field(default_factory=lambda: _mkid("sels"))
    assessment_id: str
    user_id: str
    selections: List[ModuleSelection]
    created_at: datetime = Field(default_factory=_now)


class BlueprintRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    blueprint_id: str = Field(default_factory=lambda: _mkid("bp"))
    user_id: str
    assessment_id: str
    selections_id: str
    assembled_json: AssembledBlueprint
    created_at: datetime = Field(default_factory=_now)


# ---------- GET /api/blueprints ----------------------------------------
class BlueprintListItem(BaseModel):
    blueprint_id: str
    created_at: datetime
    goal: str
    primary_module_slug: str
    primary_module_display_name: str
    module_count: int


# ---------- GET /api/blueprints/{id}/selections ------------------------
class BlueprintSelectionsResponse(BaseModel):
    blueprint_id: str
    assessment_id: str
    selections: List[ModuleSelection]


# ---------- POST /api/payments/create-pre-assessment-order --------------
class CreatePreAssessmentOrderResponse(BaseModel):
    payment_id: str
    razorpay_order_id: str
    amount: int
    currency: str
    key_id: str


# ---------- POST /api/payments/create-order (legacy PDF unlock) ----------
class CreateOrderRequest(BaseModel):
    blueprint_id: str


class CreateOrderResponse(BaseModel):
    payment_id: str
    razorpay_order_id: str
    amount: int
    currency: str
    key_id: str


class PaymentRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payment_id: str = Field(default_factory=lambda: _mkid("pay"))
    user_id: str
    # blueprint_id is None for pre-assessment payments; set after generation.
    blueprint_id: Optional[str] = None
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    amount_paise: int
    currency: str = "INR"
    status: str  # "created" | "paid"
    created_at: datetime = Field(default_factory=_now)
    updated_at: Optional[datetime] = None


# ---------- GET /api/modules -------------------------------------------
class ModuleSummary(BaseModel):
    slug: str
    display_name: str
    audience: Optional[str] = None
    primary_goal: Optional[str] = None
    is_authored_extension: bool = False
    content_pending: bool = False
