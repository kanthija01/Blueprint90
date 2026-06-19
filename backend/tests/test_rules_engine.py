"""Phase 1 rules-engine tests.

Covers every requirement explicitly listed for Phase 1:
  - Every problem mapping (8 problems)
  - Every lifestyle mapping (4 lifestyles)
  - Night-shift fallback
  - Student fallback
  - Default path (no problems)
  - Unmapped slug raises ModuleMappingError
  - Gym anxiety keyword detection

Plus a handful of guardrail tests so subtle regressions (priority ordering,
unrelated lifestyles staying unmarked, plant_power activation) get caught.

NO database, NO API, NO LLM. Pure-function tests on the rules engine.
"""
from __future__ import annotations

from typing import Any, List

import pytest

from rules_engine.errors import ModuleMappingError
from rules_engine.maps.lifestyle_module_map import LIFESTYLE_MODULE_MAP
from rules_engine.maps.problem_module_map import PROBLEM_MODULE_MAP
from rules_engine.select_modules import (
    detect_gym_anxiety_signal,
    select_modules,
)
from rules_engine.types import Assessment, ModuleSelection
from rules_engine.validate import validate_module_slugs


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def make_assessment(**overrides: Any) -> Assessment:
    """Build a valid Assessment with sensible defaults; override per test."""
    base = dict(
        age=30,
        gender="female",
        height_cm=165.0,
        weight_kg=65.0,
        goal="fat_loss",
        lifestyle="working_professional",
        diet="non_vegetarian",
        workout_preference="home",
        time_available_min=30,
        problems=[],
        biggest_struggle="",
    )
    base.update(overrides)
    return Assessment(**base)


def slugs_of(selections: List[ModuleSelection]) -> List[str]:
    return [s.module_slug for s in selections]


# ---------------------------------------------------------------------------
# 1. Every Problem mapping resolves to the right module
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "problem_slug,expected_module",
    [
        ("pcos", "pcos"),
        ("thyroid", "thyroid"),
        ("plateau", "plateau_breaker"),
        ("consistency", "consistency_code"),
        ("emotional_eating", "emotional_eating_reset"),
        ("knee_pain", "knee_safe_strength"),
        ("back_pain", "back_strong"),
        ("stress", "calm_strength"),
    ],
)
def test_each_problem_maps_to_its_module(problem_slug: str, expected_module: str) -> None:
    a = make_assessment(problems=[problem_slug])
    sels = select_modules(a)
    selected_slugs = slugs_of(sels)
    assert expected_module in selected_slugs, (
        f"Problem {problem_slug!r} should resolve to module {expected_module!r}; "
        f"got {selected_slugs}"
    )
    # Problem-driven module must come FIRST (highest precedence)
    assert sels[0].module_slug == expected_module
    assert sels[0].reason == "problem_match"
    assert sels[0].priority == 0
    assert sels[0].is_fallback is False


def test_problem_module_map_covers_all_8_form_slugs() -> None:
    expected = {
        "pcos", "thyroid", "plateau", "consistency",
        "emotional_eating", "knee_pain", "back_pain", "stress",
    }
    assert set(PROBLEM_MODULE_MAP.keys()) == expected


# ---------------------------------------------------------------------------
# 2. Every Lifestyle mapping resolves correctly
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "lifestyle,expected_module,expected_is_fallback",
    [
        ("working_professional", "executive_energy", False),
        ("busy_mother", "mom_strong", False),
        ("student", "dorm_fit", True),
        ("night_shift_worker", "executive_energy", True),
    ],
)
def test_each_lifestyle_maps_to_its_module(
    lifestyle: str, expected_module: str, expected_is_fallback: bool
) -> None:
    a = make_assessment(lifestyle=lifestyle, problems=[])
    sels = select_modules(a)

    lifestyle_sels = [s for s in sels if s.reason in ("lifestyle_match", "fallback")]
    assert len(lifestyle_sels) == 1, f"Expected exactly one lifestyle selection, got {sels}"
    ls = lifestyle_sels[0]
    assert ls.module_slug == expected_module
    assert ls.is_fallback is expected_is_fallback


def test_lifestyle_module_map_covers_all_4_form_values() -> None:
    expected = {"working_professional", "busy_mother", "student", "night_shift_worker"}
    assert set(LIFESTYLE_MODULE_MAP.keys()) == expected


# ---------------------------------------------------------------------------
# 3. Night-shift fallback (explicit, single-purpose test)
# ---------------------------------------------------------------------------
def test_night_shift_falls_back_to_executive_energy() -> None:
    a = make_assessment(lifestyle="night_shift_worker", problems=[])
    sels = select_modules(a)
    ls = next(s for s in sels if s.reason in ("lifestyle_match", "fallback"))

    assert ls.module_slug == "executive_energy"
    assert ls.is_fallback is True
    assert ls.reason == "fallback"
    assert ls.fallback_note is not None
    assert "night shift" in ls.fallback_note.lower()


# ---------------------------------------------------------------------------
# 4. Student fallback
# ---------------------------------------------------------------------------
def test_student_falls_back_to_dorm_fit() -> None:
    a = make_assessment(lifestyle="student", problems=[])
    sels = select_modules(a)
    ls = next(s for s in sels if s.reason in ("lifestyle_match", "fallback"))

    assert ls.module_slug == "dorm_fit"
    assert ls.is_fallback is True
    assert ls.reason == "fallback"
    assert ls.fallback_note is not None
    assert "campus" in ls.fallback_note.lower()


# ---------------------------------------------------------------------------
# 5. Default path: no problems selected
# ---------------------------------------------------------------------------
def test_default_path_no_problems_still_returns_lifestyle_module() -> None:
    """With zero problems, the assessment is never empty — the lifestyle
    module always anchors the blueprint."""
    a = make_assessment(problems=[], lifestyle="working_professional")
    sels = select_modules(a)
    assert len(sels) >= 1
    assert sels[0].module_slug == "executive_energy"
    assert sels[0].reason == "lifestyle_match"


def test_default_path_no_problems_no_extras() -> None:
    """With no problems, no muscle-gain veg combo, and no anxiety signal,
    only the lifestyle module is selected — no spurious extras."""
    a = make_assessment(
        problems=[],
        lifestyle="working_professional",
        goal="fat_loss",
        diet="non_vegetarian",
        workout_preference="home",
        biggest_struggle="just trying to feel better",
    )
    sels = select_modules(a)
    assert slugs_of(sels) == ["executive_energy"]


# ---------------------------------------------------------------------------
# 6. Unmapped slug raises ModuleMappingError
# ---------------------------------------------------------------------------
def test_validate_module_slugs_passes_for_known_slugs() -> None:
    validate_module_slugs(["pcos", "stress", "back_pain"])  # should not raise


def test_validate_module_slugs_raises_for_single_unknown() -> None:
    with pytest.raises(ModuleMappingError) as excinfo:
        validate_module_slugs(["pcos", "diabetes"])
    assert "diabetes" in str(excinfo.value)
    assert excinfo.value.unknown_slugs == ["diabetes"]


def test_validate_module_slugs_lists_all_unknowns() -> None:
    with pytest.raises(ModuleMappingError) as excinfo:
        validate_module_slugs(["foo", "pcos", "bar"])
    # Preserves input order, only collects unknowns
    assert excinfo.value.unknown_slugs == ["foo", "bar"]


# ---------------------------------------------------------------------------
# 7. Gym anxiety keyword detection
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "text",
    [
        "I'm nervous about going to the gym",
        "I feel really anxious in the weight room",
        "Gyms intimidate me",
        "I'm intimidated by the equipment",
        "I'm scared everyone is watching",
        "I feel judged when I lift",
        "judgemental crowd",
        "It's my first time at the gym",
        "I'm new to the gym",
        "NERVOUS",  # case-insensitive
    ],
)
def test_detect_gym_anxiety_signal_positive(text: str) -> None:
    assert detect_gym_anxiety_signal(text) is True


@pytest.mark.parametrize(
    "text",
    [
        "",
        "I want to lose weight",
        "I love lifting heavy",
        "I have plenty of energy",
        "Want to gain muscle",
        "Confident in my form",
    ],
)
def test_detect_gym_anxiety_signal_negative(text: str) -> None:
    assert detect_gym_anxiety_signal(text) is False


def test_gym_anxiety_only_triggers_gym_confidence_when_workout_pref_is_gym() -> None:
    # Anxiety signal present, but the user picked home workouts -> gym_confidence
    # should NOT be injected (it's a gym-specific psychology add-on).
    a_home = make_assessment(
        workout_preference="home",
        biggest_struggle="I'm nervous about lifting weights",
    )
    assert "gym_confidence" not in slugs_of(select_modules(a_home))

    # Same signal + gym preference -> gym_confidence IS injected.
    a_gym = make_assessment(
        workout_preference="gym",
        biggest_struggle="I'm nervous about lifting weights",
    )
    assert "gym_confidence" in slugs_of(select_modules(a_gym))


# ---------------------------------------------------------------------------
# Guardrail tests (small + targeted; catch easy regressions)
# ---------------------------------------------------------------------------
def test_plant_power_triggers_for_muscle_gain_vegetarian() -> None:
    a = make_assessment(goal="muscle_gain", diet="vegetarian")
    assert "plant_power" in slugs_of(select_modules(a))


def test_plant_power_triggers_for_muscle_gain_vegan() -> None:
    a = make_assessment(goal="muscle_gain", diet="vegan")
    assert "plant_power" in slugs_of(select_modules(a))


def test_plant_power_does_not_trigger_for_non_veg() -> None:
    a = make_assessment(goal="muscle_gain", diet="non_vegetarian")
    assert "plant_power" not in slugs_of(select_modules(a))


def test_plant_power_does_not_trigger_for_fat_loss_vegetarian() -> None:
    a = make_assessment(goal="fat_loss", diet="vegetarian")
    assert "plant_power" not in slugs_of(select_modules(a))


def test_priority_is_monotonic_and_problems_come_first() -> None:
    a = make_assessment(
        problems=["pcos", "stress"],
        lifestyle="busy_mother",
        goal="muscle_gain",
        diet="vegetarian",
        workout_preference="gym",
        biggest_struggle="I feel intimidated by the gym",
    )
    sels = select_modules(a)
    # Priorities are strictly increasing and start at 0
    assert [s.priority for s in sels] == list(range(len(sels)))
    # Problems first
    assert sels[0].module_slug == "pcos"
    assert sels[1].module_slug == "calm_strength"
    # Then lifestyle
    assert sels[2].module_slug == "mom_strong"
    # Then goal+diet
    assert sels[3].module_slug == "plant_power"
    # Then gym anxiety
    assert sels[4].module_slug == "gym_confidence"


def test_every_problem_module_target_is_a_real_seeded_slug() -> None:
    """All right-hand-side values in PROBLEM_MODULE_MAP must correspond to
    one of the 14 seeded modules. Catches typos that would otherwise pass
    Phase 1 silently and break only at assembly time."""
    expected_seeded = {
        "pcos", "thyroid", "mom_strong", "executive_energy", "beginner_boost",
        "consistency_code", "dorm_fit", "plant_power", "gym_confidence",
        "plateau_breaker",
        "emotional_eating_reset", "knee_safe_strength", "back_strong", "calm_strength",
    }
    targets = set(PROBLEM_MODULE_MAP.values())
    assert targets.issubset(expected_seeded), (
        f"PROBLEM_MODULE_MAP points at unseeded slug(s): {targets - expected_seeded}"
    )


def test_every_lifestyle_module_target_is_a_real_seeded_slug() -> None:
    expected_seeded = {
        "pcos", "thyroid", "mom_strong", "executive_energy", "beginner_boost",
        "consistency_code", "dorm_fit", "plant_power", "gym_confidence",
        "plateau_breaker",
        "emotional_eating_reset", "knee_safe_strength", "back_strong", "calm_strength",
    }
    targets = {m.module_slug for m in LIFESTYLE_MODULE_MAP.values()}
    assert targets.issubset(expected_seeded)
