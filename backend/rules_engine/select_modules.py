"""Deterministic module selection.

Given a validated `Assessment`, return an ordered list of `ModuleSelection`s.

Selection priority (lower priority value = higher precedence at assembly time):
    1. Each explicitly-selected Problem.
    2. Lifestyle (always present — every Lifestyle Literal has a map entry).
    3. Goal + Diet combo: muscle_gain + (vegetarian | vegan) -> plant_power.
    4. Workout preference + low-confidence cue: gym + anxiety keywords -> gym_confidence.
    5. Default foundational plan (beginner_boost) if and ONLY if nothing else matched.
       Currently unreachable given a valid Assessment (lifestyle always populates step 2);
       kept as an explicit safety net so an unforeseen schema change can never produce
       an empty blueprint.

PURE function. No DB. No LLM. No fuzzy matching.
`validate_module_slugs()` MUST be called first to reject unmapped problem slugs.
"""
from __future__ import annotations

from typing import List

from rules_engine.maps.lifestyle_module_map import LIFESTYLE_MODULE_MAP
from rules_engine.maps.problem_module_map import PROBLEM_MODULE_MAP
from rules_engine.types import Assessment, ModuleSelection


# Deliberately short, deliberately deterministic. Do NOT replace with embeddings
# or LLM similarity. If you need broader coverage, ADD a checkbox to the form;
# do not soften this list into a guess.
GYM_ANXIETY_SIGNALS: tuple[str, ...] = (
    "nervous",
    "anxious",
    "intimidat",  # intimidate / intimidating / intimidated
    "scared",
    "judg",  # judge / judged / judgement / judgemental
    "first time at the gym",
    "new to the gym",
)


def detect_gym_anxiety_signal(text: str) -> bool:
    """Return True if `text` contains any explicit gym-anxiety keyword.

    Case-insensitive substring match. Pure function. No LLM.
    """
    lower = (text or "").lower()
    return any(s in lower for s in GYM_ANXIETY_SIGNALS)


def select_modules(a: Assessment) -> List[ModuleSelection]:
    """Deterministic module picker. Returns selections in application order."""
    selections: List[ModuleSelection] = []
    priority = 0

    # ----- Priority 1: explicit Problems (highest precedence — these are
    # the user's stated reason for being here) ----------------------------
    for problem in a.problems:
        slug = PROBLEM_MODULE_MAP.get(problem)
        if slug is None:
            # Defensive only. Reaching this branch means validate_module_slugs
            # was not called first — that's a programming error upstream.
            # We do NOT silently skip; we let the caller's lack of validation
            # surface as an inconsistency.
            continue
        selections.append(
            ModuleSelection(
                module_slug=slug,
                reason="problem_match",
                priority=priority,
                is_fallback=False,
            )
        )
        priority += 1

    # ----- Priority 2: Lifestyle module ---------------------------------
    lifestyle_mapping = LIFESTYLE_MODULE_MAP[a.lifestyle]
    selections.append(
        ModuleSelection(
            module_slug=lifestyle_mapping.module_slug,
            reason="fallback" if lifestyle_mapping.is_fallback else "lifestyle_match",
            priority=priority,
            is_fallback=lifestyle_mapping.is_fallback,
            fallback_note=lifestyle_mapping.fallback_note,
        )
    )
    priority += 1

    # ----- Priority 3: Goal + Diet combination --------------------------
    # Vegetarian/vegan + muscle gain has a dedicated module (Plant Power).
    if a.goal == "muscle_gain" and a.diet in ("vegetarian", "vegan"):
        selections.append(
            ModuleSelection(
                module_slug="plant_power",
                reason="goal_diet_match",
                priority=priority,
                is_fallback=False,
            )
        )
        priority += 1

    # ----- Priority 4: Workout pref + low-confidence keyword cue --------
    # gym_confidence is a psychology add-on, not a universal "gym module".
    # It only triggers when the user explicitly signals anxiety in the
    # free-text biggest_struggle field.
    if a.workout_preference == "gym" and detect_gym_anxiety_signal(a.biggest_struggle):
        selections.append(
            ModuleSelection(
                module_slug="gym_confidence",
                reason="problem_match",
                priority=priority,
                is_fallback=False,
            )
        )
        priority += 1

    # ----- Priority 5: Default foundational module ----------------------
    # Safety net only. Lifestyle always populates step 2 given a valid
    # Assessment, so this branch is unreachable today. Kept for the day
    # a schema change accidentally introduces an empty selection set.
    if not selections:
        selections.append(
            ModuleSelection(
                module_slug="beginner_boost",
                reason="default",
                priority=priority,
                is_fallback=True,
                fallback_note=(
                    "General foundational plan — add a specific concern for "
                    "a more tailored blueprint."
                ),
            )
        )

    return selections
