"""Builds the WeeklyMilestones section (12-week structure).

Structure is fixed by the architecture doc:
  Week 1  -> Baseline (establish habits, no major changes)
  Week 4  -> Monthly review (per Plateau Database rules)
  Week 8  -> Monthly review (per Plateau Database rules)
  Week 12 -> Final review (90-day outcome assessment)
  Weeks 2,3,5,6,7,9,10,11 -> Consistency week (default focus)

Checklist items come VERBATIM from the primary module's `habits` array —
nothing is generated. If the primary module has no habits, the checklist is
empty (faithful to the source — sparse modules with no habits get empty
checklists).

PURE function. No DB. No LLM.
"""
from __future__ import annotations

from typing import List

from models.blueprint import WeeklyMilestone
from models.module import Module

WEEK_FOCUS_OVERRIDES = {
    1: "Baseline — establish habits, no major changes",
    4: "Monthly review — reassess per Plateau Database rules",
    8: "Monthly review — reassess per Plateau Database rules",
    12: "Final review — 90-day outcome assessment",
}
DEFAULT_FOCUS = "Consistency week — follow workout + nutrition + habit plan"


def _format_habit(habit_name: str, daily_target: str | None) -> str:
    if daily_target:
        return f"{habit_name}: {daily_target}"
    return habit_name


def build_weekly_milestones(primary_module: Module) -> List[WeeklyMilestone]:
    checklist = [
        _format_habit(h.habit_name, h.daily_target)
        for h in primary_module.habits
    ]
    return [
        WeeklyMilestone(
            week=w,
            focus=WEEK_FOCUS_OVERRIDES.get(w, DEFAULT_FOCUS),
            checklist_items=checklist,
        )
        for w in range(1, 13)
    ]
