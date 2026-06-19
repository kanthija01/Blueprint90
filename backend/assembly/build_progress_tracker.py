"""Builds the ProgressTracker section.

  - Columns come VERBATIM from the primary module's `tracker_columns`
    (e.g., PCOS tracks "Cramps/Pain", Thyroid tracks "Cortisol Level",
    Knee-Safe tracks "Pain Level", etc. — each module's tracker is shaped
    around what matters for that problem).
  - Weeks 1..12 always; the user fills the cells themselves in the printed PDF.
  - If the primary module has no tracker_columns, `columns` is empty (the
    PDF will render just the week numbers, which is still useful).

PURE function. No DB. No LLM.
"""
from __future__ import annotations

from models.blueprint import ProgressTracker
from models.module import Module


def build_progress_tracker(primary_module: Module) -> ProgressTracker:
    columns = [c.column_name for c in primary_module.tracker_columns]
    return ProgressTracker(columns=columns, weeks=list(range(1, 13)))
