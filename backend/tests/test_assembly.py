"""Phase 2 assembly-engine tests.

Covers every required scenario:
  - PCOS only
  - PCOS + consistency
  - Thyroid + stress
  - Working professional + vegetarian muscle gain
  - Student fallback
  - Night shift fallback
  - Multi-module deduplication
  - Empty optional sections
  - Sparse modules
  - Diet filtering

Tests are PURE — they import seeded Module instances from the seed package
directly (no DB hits), exercise the rules engine to produce selections, then
feed selections+modules into `assemble_blueprint`. End-to-end deterministic.
"""
from __future__ import annotations

from typing import Any, Dict, List

import pytest

from assembly.assemble_blueprint import assemble_blueprint
from assembly.dedupe import (
    dedupe_failed_solutions,
    dedupe_faqs,
    dedupe_habits,
    dedupe_root_causes,
    normalize_text,
)
from models.module import Module
from rules_engine.select_modules import select_modules
from rules_engine.types import Assessment


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def make_assessment(**overrides: Any) -> Assessment:
    base: Dict[str, Any] = dict(
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


def load_modules(slugs: List[str]) -> List[Module]:
    """Import the seeded Module instances directly from the seed package."""
    import importlib

    mods: List[Module] = []
    for s in slugs:
        m = importlib.import_module(f"seed.modules.{s}")
        mods.append(m.MODULE)
    return mods


def assemble_for(assessment: Assessment):
    """Run rules engine, load the selected modules in order, and assemble."""
    selections = select_modules(assessment)
    mods = load_modules([s.module_slug for s in selections])
    return assemble_blueprint(assessment, selections, mods), selections, mods


# ---------------------------------------------------------------------------
# 1. PCOS only
# ---------------------------------------------------------------------------
def test_pcos_only_primary_owns_nutrition_and_workout() -> None:
    a = make_assessment(
        problems=["pcos"],
        lifestyle="working_professional",
        diet="non_vegetarian",
        workout_preference="home",
        time_available_min=30,
    )
    bp, sels, _ = assemble_for(a)

    # Primary module is pcos, then lifestyle (executive_energy)
    assert sels[0].module_slug == "pcos"
    assert bp.meta.primary_module_slug == "pcos"

    # Nutrition is sourced from pcos
    assert bp.nutrition_strategy.source_module == "pcos"
    assert bp.nutrition_strategy.diet == "non_vegetarian"
    assert len(bp.nutrition_strategy.targets) > 0
    # All food entries are non_vegetarian (diet filter applied)
    # (FoodItem doesn't carry diet_type in the output, but the upstream
    # Module's foods include both — we verify filtering by counting:
    # primary pcos has both veg and non-veg; output should contain only one half.)
    pcos_mod = load_modules(["pcos"])[0]
    expected_nonveg = sum(1 for f in pcos_mod.foods if f.diet_type == "non_vegetarian")
    assert len(bp.nutrition_strategy.foods) == expected_nonveg

    # Workout sourced from pcos, time matches
    assert bp.workout_plan is not None
    assert bp.workout_plan.source_module == "pcos"
    assert bp.workout_plan.time_minutes == 30

    # Weekly milestones cover all 12 weeks
    assert [m.week for m in bp.weekly_milestones] == list(range(1, 13))
    assert bp.weekly_milestones[0].focus.startswith("Baseline")
    assert bp.weekly_milestones[3].focus.startswith("Monthly review")
    assert bp.weekly_milestones[7].focus.startswith("Monthly review")
    assert bp.weekly_milestones[11].focus.startswith("Final review")

    # Progress tracker from primary
    assert bp.progress_tracker.weeks == list(range(1, 13))
    assert bp.progress_tracker.columns == [c.column_name for c in pcos_mod.tracker_columns]


# ---------------------------------------------------------------------------
# 2. PCOS + consistency (multi-module merge + dedupe)
# ---------------------------------------------------------------------------
def test_pcos_plus_consistency_merge_and_dedupe() -> None:
    a = make_assessment(problems=["pcos", "consistency"])
    bp, sels, mods = assemble_for(a)

    # Both modules in selections (plus lifestyle)
    slugs_used = [s.module_slug for s in sels]
    assert "pcos" in slugs_used
    assert "consistency_code" in slugs_used

    # Primary remains pcos (problem order from form preserved)
    assert bp.meta.primary_module_slug == "pcos"

    # Secondary modules contribute habits/psychology/root_causes etc.
    # PCOS has habits and so does consistency_code -> habit_system carries both
    # (deduped by habit_name).
    habit_sources = {h.source_module for h in bp.habit_system}
    # PCOS contributes; consistency_code may contribute non-conflicting habits.
    assert "pcos" in habit_sources

    # No duplicate habit_names in output
    names = [normalize_text(h.habit_name) for h in bp.habit_system]
    assert len(names) == len(set(names))

    # FAQs from both deduped
    questions = [normalize_text(f.question) for f in bp.faqs]
    assert len(questions) == len(set(questions))

    # Primary's source attribution on prescriptive sections
    assert bp.nutrition_strategy.source_module == "pcos"
    if bp.workout_plan is not None:
        assert bp.workout_plan.source_module == "pcos"


# ---------------------------------------------------------------------------
# 3. Thyroid + stress
# ---------------------------------------------------------------------------
def test_thyroid_plus_stress() -> None:
    a = make_assessment(problems=["thyroid", "stress"])
    bp, sels, _ = assemble_for(a)

    slugs_used = [s.module_slug for s in sels]
    assert slugs_used[:2] == ["thyroid", "calm_strength"]
    assert bp.meta.primary_module_slug == "thyroid"

    # Both thyroid AND calm_strength have psychology thoughts -> merged + deduped
    psy_sources = {p.source_module for p in bp.psychology_system.common_thoughts}
    assert "thyroid" in psy_sources
    # Dedupe applied — no duplicate common_thought texts
    thoughts = [normalize_text(t.common_thought) for t in bp.psychology_system.common_thoughts]
    assert len(thoughts) == len(set(thoughts))


# ---------------------------------------------------------------------------
# 4. Working professional + vegetarian muscle gain (triggers plant_power)
# ---------------------------------------------------------------------------
def test_working_pro_veg_muscle_gain_triggers_plant_power() -> None:
    a = make_assessment(
        problems=[],
        lifestyle="working_professional",
        goal="muscle_gain",
        diet="vegetarian",
    )
    bp, sels, _ = assemble_for(a)

    slugs_used = [s.module_slug for s in sels]
    assert "executive_energy" in slugs_used  # lifestyle
    assert "plant_power" in slugs_used  # goal+diet match

    # Primary is the lifestyle module (no problems selected, so lifestyle has
    # priority 0).
    assert bp.meta.primary_module_slug == "executive_energy"

    # Nutrition foods filtered to vegetarian only
    assert bp.nutrition_strategy.diet == "vegetarian"
    exec_mod = load_modules(["executive_energy"])[0]
    expected_veg = sum(1 for f in exec_mod.foods if f.diet_type == "vegetarian")
    assert len(bp.nutrition_strategy.foods) == expected_veg


# ---------------------------------------------------------------------------
# 5. Student fallback
# ---------------------------------------------------------------------------
def test_student_fallback_marks_meta_fallback() -> None:
    a = make_assessment(problems=[], lifestyle="student")
    bp, sels, _ = assemble_for(a)

    # dorm_fit is the only selection (problems empty, no muscle-gain veg combo,
    # no gym anxiety)
    assert sels[0].module_slug == "dorm_fit"
    assert sels[0].is_fallback is True
    assert sels[0].fallback_note is not None
    assert "campus" in sels[0].fallback_note.lower()

    # Meta surfaces the fallback flag
    assert bp.meta.modules_used[0].is_fallback is True
    assert bp.meta.modules_used[0].fallback_note is not None

    # dorm_fit is sparse -> workout_plan is None (no routines in source)
    assert bp.workout_plan is None  # see "sparse modules" test below for detail


# ---------------------------------------------------------------------------
# 6. Night shift fallback
# ---------------------------------------------------------------------------
def test_night_shift_fallback_uses_executive_energy() -> None:
    a = make_assessment(problems=[], lifestyle="night_shift_worker")
    bp, sels, _ = assemble_for(a)

    assert sels[0].module_slug == "executive_energy"
    assert sels[0].is_fallback is True
    assert "night shift" in sels[0].fallback_note.lower()

    assert bp.meta.primary_module_slug == "executive_energy"
    assert bp.meta.modules_used[0].is_fallback is True


# ---------------------------------------------------------------------------
# 7. Multi-module deduplication (exhaustive)
# ---------------------------------------------------------------------------
def test_multi_module_dedupe_unit() -> None:
    """Direct unit tests of dedupe helpers — order-preserving, case-insensitive."""
    from models.blueprint import FAQItem, HabitItem, RootCauseItem, FailedSolutionItem

    faqs = [
        FAQItem(question="Is rest important?", answer="Yes.", source_module="a"),
        FAQItem(question="  IS rest important?  ", answer="Different.", source_module="b"),
        FAQItem(question="Should I sleep?", answer="Yes.", source_module="c"),
    ]
    out = dedupe_faqs(faqs)
    assert [f.source_module for f in out] == ["a", "c"]

    habits = [
        HabitItem(habit_name="Walk daily", source_module="a"),
        HabitItem(habit_name="walk daily", source_module="b"),
    ]
    assert len(dedupe_habits(habits)) == 1
    assert dedupe_habits(habits)[0].source_module == "a"

    root_causes = [
        RootCauseItem(category="Biological", root_cause="Insulin resistance", source_module="a"),
        RootCauseItem(category="biological", root_cause="INSULIN RESISTANCE", source_module="b"),
        RootCauseItem(category="Lifestyle", root_cause="Insulin resistance", source_module="c"),
    ]
    out = dedupe_root_causes(root_causes)
    # Same root_cause text under DIFFERENT category is kept
    assert len(out) == 2

    failed = [
        FailedSolutionItem(solution_tried="Crash diet", why_it_failed="x", source_module="a"),
        FailedSolutionItem(solution_tried="Crash Diet", why_it_failed="y", source_module="b"),
    ]
    assert len(dedupe_failed_solutions(failed)) == 1


def test_real_pcos_thyroid_combo_no_duplicate_rows() -> None:
    a = make_assessment(problems=["pcos", "thyroid"])
    bp, _, _ = assemble_for(a)

    for field, key in [
        (bp.faqs, lambda f: normalize_text(f.question)),
        (bp.habit_system, lambda h: normalize_text(h.habit_name)),
        (bp.psychology_system.common_thoughts, lambda p: normalize_text(p.common_thought)),
        (bp.psychology_system.techniques, lambda p: normalize_text(p.technique)),
        (bp.plateau_playbook, lambda p: normalize_text(p.trigger_condition)),
        (bp.why_previous_attempts_failed, lambda f: normalize_text(f.solution_tried)),
    ]:
        keys = [key(x) for x in field]
        assert len(keys) == len(set(keys)), f"Duplicates in {field[:2]!r}"


# ---------------------------------------------------------------------------
# 8. Empty optional sections (sparse module as primary)
# ---------------------------------------------------------------------------
def test_empty_sections_when_primary_lacks_data() -> None:
    # plateau_breaker is the sparsest module — no nutrition, no workouts, etc.
    a = make_assessment(problems=["plateau"])
    bp, sels, _ = assemble_for(a)

    assert sels[0].module_slug == "plateau_breaker"
    assert bp.meta.primary_module_slug == "plateau_breaker"

    # Primary's prescriptive sections are empty (source is sparse)
    assert bp.nutrition_strategy.targets == []
    assert bp.nutrition_strategy.foods == []
    assert bp.nutrition_strategy.meal_ideas == []
    assert bp.workout_plan is None  # no routines in source
    assert bp.progress_tracker.columns == []  # no tracker_columns in source

    # But the secondary (lifestyle = executive_energy by default) still
    # contributes qualitative content
    assert len(bp.habit_system) > 0  # executive_energy has habits


# ---------------------------------------------------------------------------
# 9. Sparse modules (explicit — no workout, no tracker)
# ---------------------------------------------------------------------------
def test_sparse_module_dorm_fit_as_primary() -> None:
    a = make_assessment(problems=[], lifestyle="student")
    bp, sels, _ = assemble_for(a)

    assert bp.meta.primary_module_slug == "dorm_fit"
    # dorm_fit source has emotions/failed/root_causes/nutrition_targets/exercises_recommended
    # but no workout_routines, habits, faqs, plateau, tracker
    assert bp.workout_plan is None
    assert bp.progress_tracker.columns == []
    assert bp.weekly_milestones != []  # always 12 weeks, just with empty checklist
    assert bp.weekly_milestones[0].checklist_items == []  # no habits in dorm_fit
    assert bp.faqs == []  # no FAQs in dorm_fit source


# ---------------------------------------------------------------------------
# 10. Diet filtering
# ---------------------------------------------------------------------------
def test_diet_filter_vegetarian_excludes_non_veg_foods() -> None:
    a = make_assessment(problems=["pcos"], diet="vegetarian")
    bp, _, _ = assemble_for(a)
    # All food options come from PCOS's vegetarian entries only
    pcos_mod = load_modules(["pcos"])[0]
    expected_veg = sum(1 for f in pcos_mod.foods if f.diet_type == "vegetarian")
    assert len(bp.nutrition_strategy.foods) == expected_veg
    # And meal ideas filtered too
    expected_veg_meals = sum(1 for m in pcos_mod.meal_ideas if m.diet_type == "vegetarian")
    assert len(bp.nutrition_strategy.meal_ideas) == expected_veg_meals


def test_diet_filter_non_vegetarian() -> None:
    a = make_assessment(problems=["pcos"], diet="non_vegetarian")
    bp, _, _ = assemble_for(a)
    pcos_mod = load_modules(["pcos"])[0]
    expected = sum(1 for f in pcos_mod.foods if f.diet_type == "non_vegetarian")
    assert len(bp.nutrition_strategy.foods) == expected


def test_diet_filter_vegan_strict_no_fallback() -> None:
    """Vegan users get strict filtering. Source modules have only veg/non-veg
    entries — vegan diet honestly produces empty foods rather than silently
    falling back to vegetarian."""
    a = make_assessment(problems=["pcos"], diet="vegan")
    bp, _, _ = assemble_for(a)
    # PCOS source has no diet_type='vegan' entries -> empty
    assert bp.nutrition_strategy.foods == []
    assert bp.nutrition_strategy.meal_ideas == []
    # Targets (numeric prescriptive) are diet-agnostic and remain populated
    assert len(bp.nutrition_strategy.targets) > 0


# ---------------------------------------------------------------------------
# Guardrails
# ---------------------------------------------------------------------------
def test_source_module_metadata_on_every_qualitative_item() -> None:
    a = make_assessment(problems=["pcos", "stress"])
    bp, _, _ = assemble_for(a)
    for f in bp.why_previous_attempts_failed:
        assert f.source_module
    for r in bp.root_causes:
        assert r.source_module
    for h in bp.habit_system:
        assert h.source_module
    for q in bp.faqs:
        assert q.source_module
    for p in bp.psychology_system.common_thoughts:
        assert p.source_module
    for p in bp.psychology_system.techniques:
        assert p.source_module
    for p in bp.plateau_playbook:
        assert p.source_module


def test_cover_page_carries_assessment_context() -> None:
    a = make_assessment(
        problems=["pcos"],
        goal="fat_loss",
        biggest_struggle="I'm always tired",
    )
    bp, _, _ = assemble_for(a)
    assert bp.cover_page.goal == "fat_loss"
    assert bp.cover_page.duration_days == 90
    assert bp.cover_page.biggest_struggle == "I'm always tired"
    assert bp.cover_page.generated_at  # populated


def test_meta_modules_used_priorities_are_strictly_monotonic() -> None:
    a = make_assessment(
        problems=["pcos", "stress"],
        lifestyle="busy_mother",
        goal="muscle_gain",
        diet="vegetarian",
    )
    bp, _, _ = assemble_for(a)
    pris = [m.priority for m in bp.meta.modules_used]
    assert pris == sorted(pris) and len(set(pris)) == len(pris)


def test_assemble_blueprint_raises_on_empty_selections() -> None:
    from assembly.assemble_blueprint import assemble_blueprint as _ab

    a = make_assessment()
    with pytest.raises(ValueError, match="at least one selection"):
        _ab(a, [], [])


def test_assemble_blueprint_raises_on_length_mismatch() -> None:
    from assembly.assemble_blueprint import assemble_blueprint as _ab
    from rules_engine.types import ModuleSelection

    a = make_assessment()
    sel = [ModuleSelection(module_slug="pcos", reason="problem_match", priority=0)]
    with pytest.raises(ValueError, match="length mismatch"):
        _ab(a, sel, [])


def test_blueprint_is_pydantic_serializable() -> None:
    """The whole shape must round-trip through model_dump — that's what gets
    persisted to `blueprints.assembled_json`."""
    a = make_assessment(problems=["pcos"])
    bp, _, _ = assemble_for(a)
    dumped = bp.model_dump(mode="json")
    assert isinstance(dumped, dict)
    assert dumped["meta"]["primary_module_slug"] == "pcos"
    # No ObjectId leakage, no datetime objects (must be strings)
    import json
    json.dumps(dumped)  # must not raise
