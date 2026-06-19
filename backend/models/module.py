"""Pydantic models for the `modules` collection.

A module is one persona/problem blueprint. The schema mirrors the 13-section template
used by every module in `fitness_database.docx` and `new_modules.md`. Sub-section content
is stored embedded (arrays) so a single Mongo read returns a fully-resolved module ready
for the assembly engine.

These models are the single source of truth for module shape. Both the seed pipeline
and the runtime fetch path use them — there is no second, drifting schema.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

DietType = Literal["vegetarian", "non_vegetarian", "vegan"]
TimeMinutes = Literal[15, 30, 45, 60]
WorkoutLocation = Literal["home", "gym", "any"]


# ---------------------------------------------------------------------------
# Section 2 — Emotional Database
# ---------------------------------------------------------------------------
class Emotion(BaseModel):
    emotion: str
    exact_phrase: str
    sort_order: int = 0


# ---------------------------------------------------------------------------
# Section 3 — Failed Solutions
# ---------------------------------------------------------------------------
class FailedSolution(BaseModel):
    solution_tried: str
    why_it_failed: str
    sort_order: int = 0


# ---------------------------------------------------------------------------
# Section 4 — Root Causes
# Note: keeping `category` as a free string (not Literal) because the source
# documents include at least Biological / Lifestyle / Psychological / Knowledge,
# and we should not silently reject a fourth value if a future module adds one.
# ---------------------------------------------------------------------------
class RootCause(BaseModel):
    category: str
    root_cause: str
    sort_order: int = 0


# ---------------------------------------------------------------------------
# Section 5 — Nutrition (targets + diet-specific foods + meals + foods-to-avoid)
# ---------------------------------------------------------------------------
class NutritionTarget(BaseModel):
    field_name: str
    field_value: str
    sort_order: int = 0


class Food(BaseModel):
    diet_type: DietType
    food_type: str  # 'Protein','Carbs','Fats','Anti-inflammatory'...
    options: str  # comma-separated display string, intentionally not normalised
    sort_order: int = 0


class FoodToAvoid(BaseModel):
    food_type: str
    why_avoid: str
    sort_order: int = 0


class MealIdea(BaseModel):
    meal_time: str  # Breakfast / Lunch / Dinner / Snacks / Planned Treat
    diet_type: DietType
    meal_option: str
    sort_order: int = 0


# ---------------------------------------------------------------------------
# Section 6 — Exercise (recommended + to avoid)
# ---------------------------------------------------------------------------
class ExerciseRecommended(BaseModel):
    exercise_type: str
    frequency: Optional[str] = None
    duration: Optional[str] = None
    benefits: Optional[str] = None
    sort_order: int = 0


class ExerciseAvoid(BaseModel):
    exercise_type: str
    why_avoid: str
    sort_order: int = 0


# ---------------------------------------------------------------------------
# Section 7 — Time-based workout routines (the day-by-day plan content)
# ---------------------------------------------------------------------------
class WorkoutExercise(BaseModel):
    exercise_name: str
    reps_or_time: Optional[str] = None
    sets: Optional[str] = None
    rest: Optional[str] = None
    week_progression: Optional[dict] = None  # e.g. {"week1": "2 sets", "week2": "3 sets"}
    sort_order: int = 0


class WorkoutRoutine(BaseModel):
    routine_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    time_minutes: TimeMinutes
    location: WorkoutLocation
    routine_label: Optional[str] = None
    exercises: List[WorkoutExercise] = Field(default_factory=list)
    sort_order: int = 0


# ---------------------------------------------------------------------------
# Section 8 — Constraints (knee pain, no-time, fatigue day, etc.)
# ---------------------------------------------------------------------------
class ModuleConstraint(BaseModel):
    constraint_name: str
    solution: str
    approach: Optional[str] = None
    sort_order: int = 0


# ---------------------------------------------------------------------------
# Section 9 — Habits
# ---------------------------------------------------------------------------
class Habit(BaseModel):
    habit_name: str
    daily_target: Optional[str] = None
    how_to_track: Optional[str] = None
    sort_order: int = 0


# ---------------------------------------------------------------------------
# Section 10 — Psychology (common thoughts + solution techniques)
# ---------------------------------------------------------------------------
class PsychologyThought(BaseModel):
    common_thought: str
    emotional_impact: Optional[str] = None
    solution: str
    sort_order: int = 0


class PsychologyTechnique(BaseModel):
    technique: str
    how_to_apply: str
    sort_order: int = 0


# ---------------------------------------------------------------------------
# Section 11 — Plateau actions
# ---------------------------------------------------------------------------
class PlateauAction(BaseModel):
    trigger_condition: str
    action_to_take: str
    timeframe: Optional[str] = None
    sort_order: int = 0


# ---------------------------------------------------------------------------
# Section 12 — FAQ
# ---------------------------------------------------------------------------
class FAQ(BaseModel):
    question: str
    answer: str
    sort_order: int = 0


# ---------------------------------------------------------------------------
# Section 13 — Progress tracking (tracker columns + key metrics)
# ---------------------------------------------------------------------------
class TrackerColumn(BaseModel):
    column_name: str
    sort_order: int = 0


class KeyMetric(BaseModel):
    metric_name: str
    target: str
    why_important: Optional[str] = None
    sort_order: int = 0


# ---------------------------------------------------------------------------
# Root document
# ---------------------------------------------------------------------------
class Module(BaseModel):
    """A single persona/problem module. One document per slug in the `modules` collection."""

    model_config = ConfigDict(extra="forbid")

    # Section 1 — Problem Profile
    slug: str
    display_name: str
    audience: Optional[str] = None
    primary_goal: Optional[str] = None
    pain_level: Optional[int] = None
    urgency: Optional[int] = None
    main_barrier: Optional[str] = None

    # Provenance flags
    is_authored_extension: bool = False  # True for the 4 Claude-authored new modules
    content_pending: bool = False  # True for stubs awaiting source-document extraction

    # Embedded content sections (all default to empty so stub modules are valid)
    emotions: List[Emotion] = Field(default_factory=list)
    failed_solutions: List[FailedSolution] = Field(default_factory=list)
    root_causes: List[RootCause] = Field(default_factory=list)

    nutrition_targets: List[NutritionTarget] = Field(default_factory=list)
    foods: List[Food] = Field(default_factory=list)
    foods_to_avoid: List[FoodToAvoid] = Field(default_factory=list)
    meal_ideas: List[MealIdea] = Field(default_factory=list)

    exercises_recommended: List[ExerciseRecommended] = Field(default_factory=list)
    exercises_avoid: List[ExerciseAvoid] = Field(default_factory=list)

    workout_routines: List[WorkoutRoutine] = Field(default_factory=list)

    constraints: List[ModuleConstraint] = Field(default_factory=list)
    habits: List[Habit] = Field(default_factory=list)

    psychology_thoughts: List[PsychologyThought] = Field(default_factory=list)
    psychology_techniques: List[PsychologyTechnique] = Field(default_factory=list)

    plateau_actions: List[PlateauAction] = Field(default_factory=list)
    faqs: List[FAQ] = Field(default_factory=list)

    tracker_columns: List[TrackerColumn] = Field(default_factory=list)
    key_metrics: List[KeyMetric] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
