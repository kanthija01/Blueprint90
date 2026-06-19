"""Problem-slug -> module-slug map.

This is a STRAIGHT LOOKUP TABLE, not a guess.  Every key here corresponds to
an actual checkbox value sent by the assessment form, and every value
corresponds to an actual `modules.slug` in the database. Adding a new entry
here is a deliberate content decision that must be paired with:
  1. a new (or existing) Module document in MongoDB, and
  2. a new option in the form's Problems multi-select.

If a problem slug in an assessment is not present here, `validate_module_slugs`
raises `ModuleMappingError` — the system never silently drops it.
"""
from __future__ import annotations


PROBLEM_MODULE_MAP: dict[str, str] = {
    # Originals (10)
    "pcos": "pcos",
    "thyroid": "thyroid",
    "plateau": "plateau_breaker",
    "consistency": "consistency_code",
    # Claude-authored extensions (4)
    "emotional_eating": "emotional_eating_reset",
    "knee_pain": "knee_safe_strength",
    "back_pain": "back_strong",
    "stress": "calm_strength",
}
