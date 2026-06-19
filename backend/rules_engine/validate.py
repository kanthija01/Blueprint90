"""Fail-loud validation for problem slugs.

This is the single mechanism that keeps the system honest. Run it BEFORE
`select_modules` so an unmapped problem never reaches selection / assembly /
PDF where the gap would be hidden behind partially-rendered output.
"""
from __future__ import annotations

from typing import Iterable

from rules_engine.errors import ModuleMappingError
from rules_engine.maps.problem_module_map import PROBLEM_MODULE_MAP


def validate_module_slugs(problems: Iterable[str]) -> None:
    """Raise `ModuleMappingError` if any problem slug is not mapped.

    No silent drops. No fuzzy matching. If the form grew a new Problem
    checkbox without a matching module + map entry, this throws.
    """
    unknown = [p for p in problems if p not in PROBLEM_MODULE_MAP]
    if unknown:
        raise ModuleMappingError(unknown)
