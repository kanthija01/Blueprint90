"""Output schema for the assembled blueprint.

This is what the assembly engine emits, what's persisted in
`blueprints.assembled_json`, and what the PDF generator (Phase 6) consumes.
Every list-of-items carries `source_module` provenance so the final PDF can
attribute content if needed.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------- Cover ---------------------------------------------------------
class CoverPage(BaseModel):
    user_name: Optional[str] = None
    goal: str
    duration_days: int = 90
    generated_at: str
    biggest_struggle: Optional[str] = None  # quoted verbatim if non-empty


# ---------- Why previous attempts failed ---------------------------------
class FailedSolutionItem(BaseModel):
    solution_tried: str
    why_it_failed: str
    source_module: str


# ---------- Root causes ---------------------------------------------------
class RootCauseItem(BaseModel):
    category: str
    root_cause: str
    source_module: str


# ---------- Nutrition -----------------------------------------------------
class NutritionTargetItem(BaseModel):
    field_name: str
    field_value: str


class FoodItem(BaseModel):
    food_type: str
    options: str


class FoodToAvoidItem(BaseModel):
    food_type: str
    why_avoid: str


class MealIdeaItem(BaseModel):
    meal_time: str
    meal_option: str


class NutritionStrategy(BaseModel):
    diet: str
    targets: List[NutritionTargetItem] = Field(default_factory=list)
    foods: List[FoodItem] = Field(default_factory=list)
    foods_to_avoid: List[FoodToAvoidItem] = Field(default_factory=list)
    meal_ideas: List[MealIdeaItem] = Field(default_factory=list)
    source_module: str


# ---------- Workout -------------------------------------------------------
class WorkoutExerciseItem(BaseModel):
    exercise_name: str
    reps_or_time: Optional[str] = None
    sets: Optional[str] = None
    rest: Optional[str] = None
    week_progression: Optional[Dict[str, str]] = None


class ExerciseAvoidItem(BaseModel):
    exercise_type: str
    why_avoid: str


class ConstraintSwapItem(BaseModel):
    """A constraint row from the primary module that matched one of the
    user's problems. Surfaced alongside the workout so the PDF can show
    "Modify X because you mentioned Y" guidance."""

    constraint_name: str
    solution: str
    approach: Optional[str] = None


class WorkoutPlan(BaseModel):
    time_minutes: int
    location: str
    routine_label: Optional[str] = None
    exercises: List[WorkoutExerciseItem] = Field(default_factory=list)
    exercises_to_avoid: List[ExerciseAvoidItem] = Field(default_factory=list)
    constraint_swaps: List[ConstraintSwapItem] = Field(default_factory=list)
    source_module: str


# ---------- Habits --------------------------------------------------------
class HabitItem(BaseModel):
    habit_name: str
    daily_target: Optional[str] = None
    how_to_track: Optional[str] = None
    source_module: str


# ---------- Psychology ----------------------------------------------------
class PsychologyThoughtItem(BaseModel):
    common_thought: str
    emotional_impact: Optional[str] = None
    solution: str
    source_module: str


class PsychologyTechniqueItem(BaseModel):
    technique: str
    how_to_apply: str
    source_module: str


class PsychologySystem(BaseModel):
    common_thoughts: List[PsychologyThoughtItem] = Field(default_factory=list)
    techniques: List[PsychologyTechniqueItem] = Field(default_factory=list)


# ---------- FAQ + Plateau -------------------------------------------------
class FAQItem(BaseModel):
    question: str
    answer: str
    source_module: str


class PlateauActionItem(BaseModel):
    trigger_condition: str
    action_to_take: str
    timeframe: Optional[str] = None
    source_module: str


# ---------- Weekly milestones --------------------------------------------
class WeeklyMilestone(BaseModel):
    week: int
    focus: str
    checklist_items: List[str] = Field(default_factory=list)


# ---------- Progress tracker --------------------------------------------
class ProgressTracker(BaseModel):
    columns: List[str] = Field(default_factory=list)
    weeks: List[int] = Field(default_factory=list)


# ---------- Meta ---------------------------------------------------------
class ModuleUsedMeta(BaseModel):
    slug: str
    display_name: str
    reason: str
    priority: int
    is_fallback: bool
    fallback_note: Optional[str] = None


class AssembledMeta(BaseModel):
    modules_used: List[ModuleUsedMeta]
    assembled_at: str
    primary_module_slug: str


# ---------- Root output --------------------------------------------------
class AssembledBlueprint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cover_page: CoverPage
    why_previous_attempts_failed: List[FailedSolutionItem] = Field(default_factory=list)
    root_causes: List[RootCauseItem] = Field(default_factory=list)

    nutrition_strategy: NutritionStrategy
    workout_plan: Optional[WorkoutPlan] = None

    habit_system: List[HabitItem] = Field(default_factory=list)
    psychology_system: PsychologySystem = Field(default_factory=PsychologySystem)
    faqs: List[FAQItem] = Field(default_factory=list)
    plateau_playbook: List[PlateauActionItem] = Field(default_factory=list)

    weekly_milestones: List[WeeklyMilestone] = Field(default_factory=list)
    progress_tracker: ProgressTracker = Field(default_factory=ProgressTracker)

    meta: AssembledMeta


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
