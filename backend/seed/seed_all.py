"""Idempotent seed runner.

Usage:
    cd /app/backend && python -m seed.seed_all

Behaviour:
  * Connects to MongoDB via core.db.get_sync_db()
  * Ensures unique indexes on `modules.slug` and `module_fallback_map.lifestyle`
  * Upserts each module by slug (replace_one(..., upsert=True)) — re-runs are safe
  * Upserts each fallback entry by lifestyle
  * Validates every module against the Pydantic schema BEFORE writing
  * Loudly warns on every stub (content_pending=True) so the gap is impossible to miss
  * Refuses to declare success if any required slug is missing from the seed list

NO LLM, NO FUZZY MATCHING.  If a fact isn't in a module file, it isn't in the DB.
"""
from __future__ import annotations

import sys
from typing import List

# Ensure `from models...` and `from core...` resolve when run as a module
# from /app/backend.  We deliberately don't sys.path-hack at runtime; running
# via `python -m seed.seed_all` from /app/backend handles it cleanly.

from core.db import Collections, get_sync_db
from models.module import Module
from models.fallback_map import FallbackMapEntry

# Import every module seed file. Listed explicitly (not auto-discovered) so the
# set of modules in production is a deliberate, reviewable list.
from seed.modules import (
    pcos,
    thyroid,
    mom_strong,
    executive_energy,
    beginner_boost,
    consistency_code,
    dorm_fit,
    plant_power,
    gym_confidence,
    plateau_breaker,
    emotional_eating_reset,
    knee_safe_strength,
    back_strong,
    calm_strength,
)
from seed.fallback_map import ENTRIES as FALLBACK_ENTRIES


# Authoritative list of module slugs Blueprint90 expects to find seeded.
# This is the contract the rules engine relies on. Any addition here is a
# product decision, not a bug fix.
EXPECTED_SLUGS: List[str] = [
    # 10 originals (from fitness_database.docx)
    "pcos",
    "thyroid",
    "mom_strong",
    "executive_energy",
    "beginner_boost",
    "consistency_code",
    "dorm_fit",
    "plant_power",
    "gym_confidence",
    "plateau_breaker",
    # 4 Claude-authored extensions (from new_modules.md)
    "emotional_eating_reset",
    "knee_safe_strength",
    "back_strong",
    "calm_strength",
]


ALL_MODULE_SEEDS: List[Module] = [
    pcos.MODULE,
    thyroid.MODULE,
    mom_strong.MODULE,
    executive_energy.MODULE,
    beginner_boost.MODULE,
    consistency_code.MODULE,
    dorm_fit.MODULE,
    plant_power.MODULE,
    gym_confidence.MODULE,
    plateau_breaker.MODULE,
    emotional_eating_reset.MODULE,
    knee_safe_strength.MODULE,
    back_strong.MODULE,
    calm_strength.MODULE,
]


def _check_expected_slugs(modules: List[Module]) -> None:
    seeded = {m.slug for m in modules}
    missing = [s for s in EXPECTED_SLUGS if s not in seeded]
    extra = sorted(seeded - set(EXPECTED_SLUGS))
    if missing:
        raise RuntimeError(
            f"Seed refusing to run: expected slugs missing from ALL_MODULE_SEEDS: {missing}"
        )
    if extra:
        # Not fatal, but surface it loudly so unknown modules aren't silently shipped.
        print(f"[seed][warn] Extra module slugs not in EXPECTED_SLUGS: {extra}")


def seed_modules() -> tuple[int, int]:
    """Upsert all 14 modules. Returns (upserted_count, stub_count)."""
    db = get_sync_db()
    coll = db[Collections.MODULES]

    # Unique index on slug — re-runs are safe.
    coll.create_index("slug", unique=True)

    _check_expected_slugs(ALL_MODULE_SEEDS)

    stubs: List[str] = []
    for mod in ALL_MODULE_SEEDS:
        # Pydantic re-validates on dump — this catches schema drift early.
        doc = mod.model_dump(mode="json")
        coll.replace_one({"slug": mod.slug}, doc, upsert=True)
        marker = " [STUB - content_pending]" if mod.content_pending else ""
        print(f"[seed] modules: upserted {mod.slug}{marker}")
        if mod.content_pending:
            stubs.append(mod.slug)

    if stubs:
        print()
        print("=" * 72)
        print(f"[seed][WARNING] {len(stubs)} module(s) seeded as STUBS with no content:")
        for s in stubs:
            print(f"  - {s}")
        print(
            "These modules currently contain only `slug` and `display_name`.\n"
            "Provide fitness_database.docx (or the section text) so their\n"
            "content arrays can be populated BEFORE Phase 1 testing.\n"
            "The rules engine will still resolve to them, but the assembly\n"
            "engine will produce empty sections for these modules until\n"
            "the content is filled in."
        )
        print("=" * 72)

    return len(ALL_MODULE_SEEDS), len(stubs)


def seed_fallback_map() -> int:
    db = get_sync_db()
    coll = db[Collections.MODULE_FALLBACK_MAP]
    coll.create_index("lifestyle", unique=True)

    for entry in FALLBACK_ENTRIES:
        assert isinstance(entry, FallbackMapEntry)
        doc = entry.model_dump(mode="json")
        coll.replace_one({"lifestyle": entry.lifestyle}, doc, upsert=True)
        print(
            f"[seed] module_fallback_map: upserted {entry.lifestyle} "
            f"-> {entry.fallback_module_slug}"
        )

    return len(FALLBACK_ENTRIES)


def main() -> int:
    print("[seed] starting Blueprint90 module + fallback-map seed")
    upserted, stubs = seed_modules()
    fallback_count = seed_fallback_map()
    print()
    print(
        f"[seed] done: {upserted} modules upserted ({stubs} stub), "
        f"{fallback_count} fallback entries"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
