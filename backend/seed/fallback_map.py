"""Seed entries for `module_fallback_map` collection.

Only two fallbacks per the architecture doc:
  - `night_shift_worker` -> executive_energy (high-stress, irregular schedule analogue)
  - `student_general`    -> dorm_fit         (no-kitchen / no-gym foundational plan)
Every fallback row is flagged so the assembled blueprint can soften copy
("adapted from..." instead of claiming a purpose-built plan).
"""
from models.fallback_map import FallbackMapEntry


ENTRIES: list[FallbackMapEntry] = [
    FallbackMapEntry(
        lifestyle="night_shift_worker",
        fallback_module_slug="executive_energy",
        is_fallback=True,
        fallback_note=(
            "Adapted from our high-stress, irregular-schedule plan for night shift routines."
        ),
    ),
    FallbackMapEntry(
        lifestyle="student_general",
        fallback_module_slug="dorm_fit",
        is_fallback=True,
        fallback_note=(
            "Adapted from our campus-living plan — let us know if you have full kitchen/gym "
            "access for a better fit."
        ),
    ),
]
