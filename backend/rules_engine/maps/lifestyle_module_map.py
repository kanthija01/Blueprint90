"""Lifestyle -> module map, with explicit fallback flags.

`working_professional` and `busy_mother` map to purpose-built modules.
`student` and `night_shift_worker` map to the closest existing module and are
flagged `is_fallback=True` so the assembled blueprint can soften copy
("adapted from..." rather than claiming a purpose-built plan).
"""
from __future__ import annotations

from typing import NamedTuple, Optional


class LifestyleMapping(NamedTuple):
    """Immutable mapping entry — keep it cheap and explicit."""

    module_slug: str
    is_fallback: bool
    fallback_note: Optional[str]


LIFESTYLE_MODULE_MAP: dict[str, LifestyleMapping] = {
    "working_professional": LifestyleMapping(
        module_slug="executive_energy",
        is_fallback=False,
        fallback_note=None,
    ),
    "busy_mother": LifestyleMapping(
        module_slug="mom_strong",
        is_fallback=False,
        fallback_note=None,
    ),
    "student": LifestyleMapping(
        # Fallback: `dorm_fit` assumes no kitchen/gym, which may not be true
        # for every student. We soften copy via fallback_note rather than
        # pretend it's a purpose-built plan.
        module_slug="dorm_fit",
        is_fallback=True,
        fallback_note=(
            "Adapted from our campus-living plan — let us know if you have "
            "full kitchen/gym access for a better fit."
        ),
    ),
    "night_shift_worker": LifestyleMapping(
        # Fallback: no dedicated module; the closest analogue is the
        # high-stress / irregular-schedule plan for working professionals.
        module_slug="executive_energy",
        is_fallback=True,
        fallback_note=(
            "Adapted from our high-stress, irregular-schedule plan "
            "for night shift routines."
        ),
    ),
}
