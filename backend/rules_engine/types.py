"""Input/output types for the rules engine.

`Assessment` is the canonical decision-time shape — what the form submits and
what the API hands to `select_modules`. Phase 3 will reuse this exact model
as the FastAPI request body, so the validation contract is single-sourced.

`ModuleSelection` is the deterministic output — an ordered list of which
modules apply to an assessment and why. This is what gets persisted to
`assessment_module_selections` so every produced blueprint is auditable.
"""
from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

# Enum-like literals match the form's allowed values exactly. If the form
# ever grows a new value, that change must be made here too — by design.
Gender = Literal["male", "female", "other"]
Goal = Literal["fat_loss", "muscle_gain", "maintenance"]
Lifestyle = Literal["student", "working_professional", "busy_mother", "night_shift_worker"]
Diet = Literal["vegetarian", "non_vegetarian", "vegan"]
WorkoutPreference = Literal["home", "gym"]
TimeMinutes = Literal[15, 30, 45, 60]

SelectionReason = Literal[
    "problem_match",
    "lifestyle_match",
    "goal_diet_match",
    "fallback",
    "default",
]


class Assessment(BaseModel):
    """The validated user assessment that drives module selection.

    NOTE: `problems` is intentionally `List[str]` rather than a Literal of
    known slugs. We rely on `validate_module_slugs()` to raise
    `ModuleMappingError` for unknowns — that gives a clean, content-team-
    facing error message instead of a generic Pydantic validation error.
    """

    model_config = ConfigDict(extra="forbid")

    age: int = Field(ge=13, le=100)
    gender: Gender
    height_cm: float = Field(ge=100, le=250)
    weight_kg: float = Field(ge=30, le=300)

    goal: Goal
    lifestyle: Lifestyle
    diet: Diet
    workout_preference: WorkoutPreference
    time_available_min: TimeMinutes

    problems: List[str] = Field(default_factory=list, max_length=8)
    biggest_struggle: str = Field(default="", max_length=500)


class ModuleSelection(BaseModel):
    """One module chosen by the rules engine, with provenance.

    `priority` is the application order. Lower = higher precedence on
    conflicts during assembly (the highest-priority module's prescriptive
    fields, e.g. nutrition targets, win).
    """

    model_config = ConfigDict(extra="forbid")

    module_slug: str
    reason: SelectionReason
    priority: int
    is_fallback: bool = False
    fallback_note: Optional[str] = None
