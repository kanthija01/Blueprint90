"""Pydantic model for `module_fallback_map` collection.

Maps lifestyles that don't have a purpose-built module to the closest existing one.
Per the architecture doc, only `night_shift_worker` and the generic `student_general`
fall back today. Adding new entries here is a deliberate content decision, not a fix.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class FallbackMapEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lifestyle: str  # 'night_shift_worker', 'student_general'
    fallback_module_slug: str
    is_fallback: bool = True
    fallback_note: str
