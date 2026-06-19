"""Top-level assembly entry point.

Given a validated Assessment + ordered ModuleSelections + the corresponding
Module documents, produce a single AssembledBlueprint JSON. This is the cached
output stored in `blueprints.assembled_json` — both the in-app preview and
the PDF generator read from this shape, never the raw module documents.

Merging strategy (architecture doc, Section 5.1):
  * Primary module (modules[0]) owns ALL prescriptive / numeric fields:
      - nutrition_strategy (targets, foods, foods_to_avoid, meal_ideas)
      - workout_plan
      - weekly_milestones checklist (uses primary's habits verbatim)
      - progress_tracker columns
  * Secondary modules contribute ONLY qualitative additions:
      - failed_solutions
      - root_causes
      - habits (concatenated and deduped, but primary's habits remain
        authoritative for the weekly checklist)
      - psychology_thoughts / psychology_techniques
      - faqs
      - plateau_actions

Each merged item carries `source_module` so the rendered PDF can attribute
content. Dedupe is order-preserving — the primary module's row wins when
two modules disagree on the same row (e.g. both have a "Walking" habit).

PURE function. No DB. No LLM. The caller is responsible for fetching modules.
"""
from __future__ import annotations

from typing import List, Sequence

from assembly.build_nutrition import build_nutrition_strategy
from assembly.build_progress_tracker import build_progress_tracker
from assembly.build_weekly_milestones import build_weekly_milestones
from assembly.build_workout import build_workout_plan
from assembly.dedupe import (
    dedupe_failed_solutions,
    dedupe_faqs,
    dedupe_habits,
    dedupe_plateau_actions,
    dedupe_psychology_techniques,
    dedupe_psychology_thoughts,
    dedupe_root_causes,
)
from models.blueprint import (
    AssembledBlueprint,
    AssembledMeta,
    CoverPage,
    FAQItem,
    FailedSolutionItem,
    HabitItem,
    ModuleUsedMeta,
    PlateauActionItem,
    PsychologySystem,
    PsychologyTechniqueItem,
    PsychologyThoughtItem,
    RootCauseItem,
    utc_now_iso,
)
from models.module import Module
from rules_engine.types import Assessment, ModuleSelection


def assemble_blueprint(
    assessment: Assessment,
    selections: Sequence[ModuleSelection],
    modules: Sequence[Module],
) -> AssembledBlueprint:
    """Build the AssembledBlueprint.

    `modules` MUST be in the same order as `selections` (highest-priority
    first). The caller fetches both — assembly is pure.
    """
    if not selections:
        raise ValueError("assemble_blueprint: at least one selection required")
    if len(selections) != len(modules):
        raise ValueError(
            f"selections/modules length mismatch: {len(selections)} vs {len(modules)}"
        )

    primary = modules[0]

    # -- Cover page -------------------------------------------------------
    cover = CoverPage(
        goal=assessment.goal,
        duration_days=90,
        generated_at=utc_now_iso(),
        biggest_struggle=(assessment.biggest_struggle or None) or None,
    )

    # -- Qualitative concatenations (then dedupe; primary's rows win on ties) -
    failed_solutions: List[FailedSolutionItem] = []
    root_causes: List[RootCauseItem] = []
    habits: List[HabitItem] = []
    psy_thoughts: List[PsychologyThoughtItem] = []
    psy_techniques: List[PsychologyTechniqueItem] = []
    faqs: List[FAQItem] = []
    plateau_actions: List[PlateauActionItem] = []

    for mod in modules:
        slug = mod.slug
        for fs in mod.failed_solutions:
            failed_solutions.append(
                FailedSolutionItem(
                    solution_tried=fs.solution_tried,
                    why_it_failed=fs.why_it_failed,
                    source_module=slug,
                )
            )
        for rc in mod.root_causes:
            root_causes.append(
                RootCauseItem(
                    category=rc.category,
                    root_cause=rc.root_cause,
                    source_module=slug,
                )
            )
        for h in mod.habits:
            habits.append(
                HabitItem(
                    habit_name=h.habit_name,
                    daily_target=h.daily_target,
                    how_to_track=h.how_to_track,
                    source_module=slug,
                )
            )
        for pt in mod.psychology_thoughts:
            psy_thoughts.append(
                PsychologyThoughtItem(
                    common_thought=pt.common_thought,
                    emotional_impact=pt.emotional_impact,
                    solution=pt.solution,
                    source_module=slug,
                )
            )
        for pq in mod.psychology_techniques:
            psy_techniques.append(
                PsychologyTechniqueItem(
                    technique=pq.technique,
                    how_to_apply=pq.how_to_apply,
                    source_module=slug,
                )
            )
        for q in mod.faqs:
            faqs.append(
                FAQItem(
                    question=q.question,
                    answer=q.answer,
                    source_module=slug,
                )
            )
        for pa in mod.plateau_actions:
            plateau_actions.append(
                PlateauActionItem(
                    trigger_condition=pa.trigger_condition,
                    action_to_take=pa.action_to_take,
                    timeframe=pa.timeframe,
                    source_module=slug,
                )
            )

    failed_solutions = dedupe_failed_solutions(failed_solutions)
    root_causes = dedupe_root_causes(root_causes)
    habits = dedupe_habits(habits)
    psy_thoughts = dedupe_psychology_thoughts(psy_thoughts)
    psy_techniques = dedupe_psychology_techniques(psy_techniques)
    faqs = dedupe_faqs(faqs)
    plateau_actions = dedupe_plateau_actions(plateau_actions)

    # -- Prescriptive sections (primary only) -----------------------------
    nutrition = build_nutrition_strategy(primary, assessment)
    workout = build_workout_plan(primary, assessment)
    milestones = build_weekly_milestones(primary)
    tracker = build_progress_tracker(primary)

    # -- Meta -------------------------------------------------------------
    by_slug = {m.slug: m for m in modules}
    modules_used = [
        ModuleUsedMeta(
            slug=sel.module_slug,
            display_name=by_slug[sel.module_slug].display_name,
            reason=sel.reason,
            priority=sel.priority,
            is_fallback=sel.is_fallback,
            fallback_note=sel.fallback_note,
        )
        for sel in selections
    ]
    meta = AssembledMeta(
        modules_used=modules_used,
        assembled_at=utc_now_iso(),
        primary_module_slug=primary.slug,
    )

    return AssembledBlueprint(
        cover_page=cover,
        why_previous_attempts_failed=failed_solutions,
        root_causes=root_causes,
        nutrition_strategy=nutrition,
        workout_plan=workout,
        habit_system=habits,
        psychology_system=PsychologySystem(
            common_thoughts=psy_thoughts,
            techniques=psy_techniques,
        ),
        faqs=faqs,
        plateau_playbook=plateau_actions,
        weekly_milestones=milestones,
        progress_tracker=tracker,
        meta=meta,
    )
