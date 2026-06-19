"""Deterministic deduplication helpers for the assembly engine.

Every dedupe is order-preserving (first occurrence wins) and uses a normalized
key (case-insensitive, whitespace-collapsed) so trivial casing/whitespace
differences across modules don't produce near-duplicate rows in the final PDF.

PURE functions. No I/O. No LLM.
"""
from __future__ import annotations

from typing import Callable, Iterable, List, TypeVar

T = TypeVar("T")


def normalize_text(s: str) -> str:
    """Lowercase + collapse whitespace + strip. Used to build dedupe keys."""
    return " ".join((s or "").lower().split())


def dedupe_by(items: Iterable[T], key_fn: Callable[[T], object]) -> List[T]:
    """Order-preserving dedupe: keep the first occurrence per normalized key."""
    seen: set = set()
    out: List[T] = []
    for item in items:
        k = key_fn(item)
        if k in seen:
            continue
        seen.add(k)
        out.append(item)
    return out


# --- Section-specific dedupe helpers -----------------------------------------
# Each operates on AssembledBlueprint-shaped items (they expose attributes,
# not dicts) and uses the most semantically-meaningful field as the dedupe key.

def dedupe_faqs(items):
    """Dedupe by normalized question."""
    return dedupe_by(items, lambda f: normalize_text(f.question))


def dedupe_habits(items):
    """Dedupe by normalized habit_name."""
    return dedupe_by(items, lambda h: normalize_text(h.habit_name))


def dedupe_root_causes(items):
    """Dedupe by (normalized category, normalized root_cause).
    Same root cause text under two different categories is intentionally
    kept — the categorization itself can be meaningful."""
    return dedupe_by(items, lambda r: (normalize_text(r.category), normalize_text(r.root_cause)))


def dedupe_psychology_thoughts(items):
    """Dedupe by normalized common_thought."""
    return dedupe_by(items, lambda p: normalize_text(p.common_thought))


def dedupe_psychology_techniques(items):
    """Dedupe by normalized technique."""
    return dedupe_by(items, lambda p: normalize_text(p.technique))


def dedupe_plateau_actions(items):
    """Dedupe by normalized trigger_condition."""
    return dedupe_by(items, lambda p: normalize_text(p.trigger_condition))


def dedupe_failed_solutions(items):
    """Dedupe by normalized solution_tried."""
    return dedupe_by(items, lambda f: normalize_text(f.solution_tried))
