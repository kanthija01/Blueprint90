"""Constraint resolution — pure helpers for picking a workout routine inside
an already-selected module and surfacing any constraint rows that apply.

Constraints (knee pain modifying exercises, home vs gym, time-available, etc.)
apply WITHIN selected modules — they don't select new modules. This matches
the source data exactly (e.g., PCOS's own Constraint Database has a "Knee Pain"
row used to substitute exercises inside the PCOS workout, separate from the
standalone Knee-Safe Strength module used when Knee Pain is the user's primary
stated Problem).

PURE function. The caller (assembly engine, Phase 2) supplies the module's
in-memory content — this helper never touches MongoDB.
"""
from __future__ import annotations

from typing import List, Optional

from models.module import Module, ModuleConstraint, WorkoutRoutine
from rules_engine.types import Assessment


def resolve_workout_routine(
    primary_module: Module,
    assessment: Assessment,
) -> Optional[WorkoutRoutine]:
    """Pick the workout routine from `primary_module` that matches the user's
    time + location preference. Falls back to the closest available time
    bracket (same location preference) if no exact match exists, then to any
    `location='any'` routine at that time. Returns `None` only if the module
    has no workout routines at all.
    """
    routines = primary_module.workout_routines
    if not routines:
        return None

    user_time = assessment.time_available_min
    user_loc = assessment.workout_preference

    # 1. Exact match: time + (location OR 'any')
    exact = [
        r for r in routines
        if r.time_minutes == user_time and r.location in (user_loc, "any")
    ]
    if exact:
        return exact[0]

    # 2. Closest time bracket, same location preference (or 'any')
    return _find_closest_time_routine(routines, user_time, user_loc)


def _find_closest_time_routine(
    routines: List[WorkoutRoutine],
    target_time: int,
    location: str,
) -> Optional[WorkoutRoutine]:
    """Return the routine whose `time_minutes` is numerically closest to
    `target_time`, restricted to the user's location preference or 'any'.
    Ties break toward the LONGER routine (more conservative — under-delivering
    on workout volume is worse than asking for a couple of extra minutes).
    """
    eligible = [r for r in routines if r.location in (location, "any")]
    if not eligible:
        eligible = list(routines)
    if not eligible:
        return None

    return min(
        eligible,
        key=lambda r: (abs(r.time_minutes - target_time), -r.time_minutes),
    )


def find_matching_constraints(
    module: Module,
    problems: List[str],
) -> List[ModuleConstraint]:
    """Return the module's constraint rows whose name matches any user-stated
    problem (e.g. user selected `knee_pain` and the module has a constraint
    named 'Knee Pain (active flare)').

    Match strategy: case-insensitive substring of the problem slug (with
    underscores -> spaces) against `constraint_name`. Deliberately simple
    and auditable. NOT an LLM, NOT a fuzzy ratio.
    """
    if not module.constraints or not problems:
        return []

    needles = [p.replace("_", " ").lower() for p in problems]
    matches: List[ModuleConstraint] = []
    for c in module.constraints:
        name_lower = c.constraint_name.lower()
        if any(needle in name_lower for needle in needles):
            matches.append(c)
    return matches
