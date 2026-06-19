"""Builds the WorkoutPlan section.

  - Routine selected by `resolve_workout_routine` (rules_engine): exact match
    on (time_available_min, workout_preference) or closest-time fallback.
  - Constraint swaps surfaced via `find_matching_constraints` (rules_engine):
    primary module's Constraint Database rows whose name matches one of the
    user's stated Problems.
  - `exercises_to_avoid` passes through from primary module unchanged.
  - Returns None if the primary module has no workout_routines at all
    (sparse modules like `gym_confidence`, `plateau_breaker`). The caller is
    responsible for rendering an empty / "see standalone module" state.

PURE function. No DB. No LLM.
"""
from __future__ import annotations

from typing import Optional

from models.blueprint import (
    ConstraintSwapItem,
    ExerciseAvoidItem,
    WorkoutExerciseItem,
    WorkoutPlan,
)
from models.module import Module
from rules_engine.resolve_constraints import (
    find_matching_constraints,
    resolve_workout_routine,
)
from rules_engine.types import Assessment


def build_workout_plan(
    primary_module: Module,
    assessment: Assessment,
) -> Optional[WorkoutPlan]:
    routine = resolve_workout_routine(primary_module, assessment)
    if routine is None:
        return None

    exercises = [
        WorkoutExerciseItem(
            exercise_name=e.exercise_name,
            reps_or_time=e.reps_or_time,
            sets=e.sets,
            rest=e.rest,
            week_progression=e.week_progression,
        )
        for e in routine.exercises
    ]

    avoid = [
        ExerciseAvoidItem(exercise_type=a.exercise_type, why_avoid=a.why_avoid)
        for a in primary_module.exercises_avoid
    ]

    constraint_swaps = [
        ConstraintSwapItem(
            constraint_name=c.constraint_name,
            solution=c.solution,
            approach=c.approach,
        )
        for c in find_matching_constraints(primary_module, assessment.problems)
    ]

    return WorkoutPlan(
        time_minutes=routine.time_minutes,
        location=routine.location,
        routine_label=routine.routine_label,
        exercises=exercises,
        exercises_to_avoid=avoid,
        constraint_swaps=constraint_swaps,
        source_module=primary_module.slug,
    )
