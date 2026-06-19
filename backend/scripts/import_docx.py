"""One-shot DOCX -> seed file importer for the 10 original modules.

Reads /tmp/fitness_database.docx, walks the body in document order, groups
sections by module (every '1. Problem Profile' heading starts a new module),
parses each section's table by deterministic heading-prefix matching, and
emits one regenerated `backend/seed/modules/<slug>.py` file per module.

Rules followed strictly:
  * NO content is invented. Each emitted field traces directly to a docx cell.
  * Missing sections leave the corresponding list EMPTY (and a warning is logged).
  * The 4 Claude-authored modules (`new_modules.md` content) are NEVER touched.
  * Module slug is determined by POSITION in the docx, not fuzzy name matching.
  * Header rows in each table are detected by a per-section header-token list
    and skipped; never confused with content rows.

Run once:
    cd /app/backend && python -m scripts.import_docx
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table

DOCX_PATH = Path("/tmp/fitness_database.docx")
SEED_DIR = Path(__file__).resolve().parent.parent / "seed" / "modules"

# Position in docx -> existing seed slug (the file we will overwrite).
# The 4 Claude-authored slugs are NOT in this list and are NEVER touched.
SLUGS_IN_ORDER: List[str] = [
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
]

# Common header tokens that mark a row as a header (to skip).
HEADER_TOKENS = {
    "field", "value",
    "emotion", "exact words people use", "exact words",
    "solution tried", "why it failed",
    "category", "root cause",
    "food type", "options",
    "why avoid",
    "meal time", "vegetarian option", "non-veg option", "non vegetarian option",
    "exercise type", "frequency", "duration", "benefits",
    "exercise", "reps/time", "reps", "sets", "rest",
    "constraint", "solution", "exercises/approach", "approach",
    "habit", "daily target", "how to track",
    "common thoughts", "common thought", "emotional impact",
    "technique", "how to apply",
    "when progress stops", "action to take", "timeframe",
    "question", "answer",
    "week",
    "measurement", "frequency", "why",
    "metric", "target", "why important",
}


def is_header_row(row_cells: List[str]) -> bool:
    """A row is treated as a header iff EVERY non-empty cell is in HEADER_TOKENS."""
    non_empty = [c.strip().lower() for c in row_cells if c.strip()]
    if not non_empty:
        return True  # blank row -> skip
    return all(c in HEADER_TOKENS for c in non_empty)


# ---------------------------------------------------------------------------
# 1. Walk doc body, collect (heading_text, table) pairs in order
# ---------------------------------------------------------------------------
def collect_sections(doc: Document) -> List[Dict[str, Any]]:
    """Returns a list of {heading, rows} dicts in document order.

    `rows` is a list of list-of-strings (raw cell text). Header rows are NOT
    filtered here — that happens in the per-section parser so a 'Field|Value'
    style first row doesn't get confused with a real row by the same parser.
    """
    sections: List[Dict[str, Any]] = []
    pending_heading: Optional[str] = None
    para_iter = iter(doc.paragraphs)

    for child in doc.element.body.iterchildren():
        if child.tag == qn("w:p"):
            try:
                p = next(para_iter)
            except StopIteration:
                continue
            text = p.text.strip()
            if p.style.name == "Heading 2" and text:
                pending_heading = text
        elif child.tag == qn("w:tbl"):
            t = Table(child, doc.part)
            rows: List[List[str]] = [
                [cell.text.strip() for cell in row.cells]
                for row in t.rows
            ]
            sections.append({"heading": pending_heading or "", "rows": rows})
            pending_heading = None
    return sections


# ---------------------------------------------------------------------------
# 2. Group sections by module (each '1. Problem Profile' starts a new module)
# ---------------------------------------------------------------------------
def group_by_module(sections: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    groups: List[List[Dict[str, Any]]] = []
    current: List[Dict[str, Any]] = []
    for s in sections:
        h = (s["heading"] or "").lower()
        if h.startswith("1. problem profile"):
            if current:
                groups.append(current)
            current = [s]
        else:
            if current:
                current.append(s)
    if current:
        groups.append(current)
    return groups


# ---------------------------------------------------------------------------
# 3. Section parsers — each returns a list of dict rows (or {}) for that field
# ---------------------------------------------------------------------------
def parse_problem_profile(rows: List[List[str]]) -> Dict[str, Any]:
    """Section 1 — key/value pairs. Returns dict of normalised fields."""
    out: Dict[str, Any] = {}
    for r in rows:
        if len(r) < 2:
            continue
        key, val = r[0].strip().lower(), r[1].strip()
        if key in ("field", ""):
            continue
        if not val:
            continue
        if key == "problem name":
            out["display_name_raw"] = val
        elif key == "audience":
            out["audience"] = val
        elif key == "goal":
            out["primary_goal"] = val
        elif key == "pain level":
            out["pain_level"] = parse_score(val)
        elif key == "urgency":
            out["urgency"] = parse_score(val)
        elif key == "main barrier":
            out["main_barrier"] = val
    return out


def parse_score(text: str) -> Optional[int]:
    """'8/10' -> 8, '8' -> 8, '' -> None."""
    m = re.match(r"\s*(\d+)", text)
    return int(m.group(1)) if m else None


def parse_two_col(
    rows: List[List[str]],
    field_a: str,
    field_b: str,
) -> List[Dict[str, Any]]:
    """Generic 2-column parser. Skips header rows and empty rows."""
    out: List[Dict[str, Any]] = []
    order = 1
    for r in rows:
        if is_header_row(r):
            continue
        if len(r) < 2:
            continue
        a, b = r[0].strip(), r[1].strip()
        if not a and not b:
            continue
        out.append({field_a: a, field_b: b, "sort_order": order})
        order += 1
    return out


def parse_three_col(
    rows: List[List[str]],
    field_a: str,
    field_b: str,
    field_c: str,
    two_col_drop: str = "c",  # 'b' or 'c' — which field to drop when table is 2-col
) -> List[Dict[str, Any]]:
    """Generic 3-column parser that degrades gracefully to a 2-col table.

    `two_col_drop` controls which field is dropped when the source table only
    has 2 columns. Use 'b' for sections where the 3rd field carries the main
    content (e.g. Psychology Thoughts: drop `emotional_impact`, keep
    `solution`). Use 'c' (default) for sections where the 3rd column is
    auxiliary (e.g. Plateau timeframe, Habit how_to_track, Constraint approach).
    """
    out: List[Dict[str, Any]] = []
    order = 1
    # Detect col count from first non-empty row
    col_count = max((len(r) for r in rows if any(c.strip() for c in r)), default=0)
    is_two_col_source = col_count <= 2

    for r in rows:
        if is_header_row(r):
            continue
        if len(r) < 2:
            continue
        a = r[0].strip()
        b = r[1].strip() if len(r) > 1 else ""
        c = r[2].strip() if len(r) > 2 else ""
        if not a and not b and not c:
            continue
        entry: Dict[str, Any] = {field_a: a}
        if is_two_col_source:
            # Source only has 2 cols; route col2 to the "important" field
            if two_col_drop == "b":
                entry[field_c] = b
            else:
                entry[field_b] = b
        else:
            entry[field_b] = b
            if c:
                entry[field_c] = c
        entry["sort_order"] = order
        out.append(entry)
        order += 1
    return out


def parse_foods(rows: List[List[str]], diet_type: str) -> List[Dict[str, Any]]:
    """Section 5a/5b: 2-col (food_type, options)."""
    out: List[Dict[str, Any]] = []
    order = 1
    for r in rows:
        if is_header_row(r):
            continue
        if len(r) < 2:
            continue
        ft, opts = r[0].strip(), r[1].strip()
        if not ft or not opts:
            continue
        out.append({
            "diet_type": diet_type,
            "food_type": ft,
            "options": opts,
            "sort_order": order,
        })
        order += 1
    return out


def parse_meal_ideas(rows: List[List[str]]) -> List[Dict[str, Any]]:
    """Section 5c (3-col: meal_time, veg_option, nonveg_option) -> expand into
    MealIdea rows for each diet type."""
    out: List[Dict[str, Any]] = []
    order = 1
    for r in rows:
        if is_header_row(r):
            continue
        if len(r) < 2:
            continue
        meal_time = r[0].strip()
        veg = r[1].strip() if len(r) > 1 else ""
        nonveg = r[2].strip() if len(r) > 2 else ""
        if not meal_time:
            continue
        if veg:
            out.append({
                "meal_time": meal_time,
                "diet_type": "vegetarian",
                "meal_option": veg,
                "sort_order": order,
            })
            order += 1
        if nonveg:
            out.append({
                "meal_time": meal_time,
                "diet_type": "non_vegetarian",
                "meal_option": nonveg,
                "sort_order": order,
            })
            order += 1
    return out


def parse_exercises_recommended(rows: List[List[str]]) -> List[Dict[str, Any]]:
    """Section 6: 4-col (exercise_type, frequency, duration, benefits)."""
    out: List[Dict[str, Any]] = []
    order = 1
    for r in rows:
        if is_header_row(r):
            continue
        if len(r) < 2:
            continue
        et = r[0].strip()
        if not et:
            continue
        out.append({
            "exercise_type": et,
            "frequency": r[1].strip() if len(r) > 1 else None,
            "duration": r[2].strip() if len(r) > 2 else None,
            "benefits": r[3].strip() if len(r) > 3 else None,
            "sort_order": order,
        })
        order += 1
    return out


# Matches '15 Minutes Routine A', '30 Minutes Routine B', etc. anywhere
# inside the heading. Deliberately requires 'minutes' DIRECTLY followed by
# 'routine' (no extra words) so e.g. '5 Minutes Desk Routine' is filtered.
WORKOUT_HEADING_RE = re.compile(
    r"(\d+)\s*minutes?\s*routine\s*([a-z]?)",
    re.IGNORECASE,
)


def parse_workout_routine(
    heading: str,
    rows: List[List[str]],
) -> Optional[Dict[str, Any]]:
    """Section 7/7a/7b: heading is 'X Minutes Routine Y'. Extract time + label.
    Column layout varies by module — we inspect the header row to map columns
    to (reps_or_time, sets, rest) instead of assuming a fixed order.
    Extra columns (e.g. 'Week 1', 'Week 2'...) are folded into week_progression."""
    m = WORKOUT_HEADING_RE.search(heading)
    if not m:
        return None
    time_minutes = int(m.group(1))
    if time_minutes not in (15, 30, 45, 60):
        return None
    label_letter = m.group(2).upper() or None
    label = f"Routine {label_letter}" if label_letter else None

    if not rows:
        return None

    # Header-driven column mapping
    header = [c.strip().lower() for c in rows[0]]
    col_map: Dict[str, int] = {}
    week_cols: List[tuple[int, str]] = []  # (col_index, week_label)
    for i, h in enumerate(header):
        if i == 0:
            col_map["exercise_name"] = i
            continue
        if h in ("reps/time", "reps", "reps / time", "time"):
            col_map["reps_or_time"] = i
        elif h == "sets":
            col_map["sets"] = i
        elif h == "rest":
            col_map["rest"] = i
        elif h.startswith("week "):
            week_cols.append((i, header[i]))

    exercises: List[Dict[str, Any]] = []
    order = 1
    for r in rows[1:]:  # skip header row we just parsed
        if is_header_row(r):
            continue
        if not r or not r[0].strip():
            continue
        entry: Dict[str, Any] = {
            "exercise_name": r[0].strip(),
            "sort_order": order,
        }
        for field, idx in col_map.items():
            if field == "exercise_name":
                continue
            if idx < len(r) and r[idx].strip():
                entry[field] = r[idx].strip()
        if week_cols:
            wp = {}
            for idx, label_text in week_cols:
                if idx < len(r) and r[idx].strip():
                    # 'week 1' -> 'week1' for stable key naming
                    wp[label_text.replace(" ", "")] = r[idx].strip()
            if wp:
                entry["week_progression"] = wp
        exercises.append(entry)
        order += 1

    return {
        "time_minutes": time_minutes,
        "location": "any",
        "routine_label": label,
        "exercises": exercises,
    }


def parse_tracker_columns(rows: List[List[str]]) -> List[Dict[str, Any]]:
    """Section 13: header row of weekly tracker -> column names.
    The first cell is typically 'Week' or empty. We take row 0 cells (excluding the first
    'Week' label) as the tracker columns."""
    if not rows:
        return []
    header = rows[0]
    out: List[Dict[str, Any]] = []
    order = 1
    # Skip the first cell (typically 'Week')
    for cell in header[1:]:
        name = cell.strip()
        if not name or name.lower() == "week":
            continue
        out.append({"column_name": name, "sort_order": order})
        order += 1
    return out


# ---------------------------------------------------------------------------
# 4. Match a section's heading to a parser + target field on the Module
# ---------------------------------------------------------------------------
def classify_heading(heading: str) -> Optional[str]:
    h = heading.lower()
    if h.startswith("1. problem profile"):
        return "problem_profile"
    if h.startswith("2. emotional"):
        return "emotions"
    if h.startswith("3. failed solutions"):
        return "failed_solutions"
    if h.startswith("4. root causes"):
        return "root_causes"
    if h.startswith("5. nutrition"):
        return "nutrition_targets"
    if h.startswith("5a."):
        if "meal idea" in h:
            return "meal_ideas"
        return "foods_veg"
    if h.startswith("5b."):
        if "meal idea" in h:
            return "meal_ideas"
        if "foods to avoid" in h:
            return "foods_to_avoid"
        return "foods_nonveg"
    if h.startswith("5c."):
        if "foods to avoid" in h:
            return "foods_to_avoid"
        return "meal_ideas"
    if h.startswith("5d."):
        if "foods to avoid" in h:
            return "foods_to_avoid"
        return "meal_ideas"
    if h.startswith("6. exercise") or h.startswith("6. exercise database"):
        return "exercises_recommended"
    if h.startswith("6a."):
        return "exercises_avoid"
    if re.match(r"^7[a-z]?\.", h):
        return "workout_routine"
    if h.startswith("8. constraint"):
        return "constraints"
    if h.startswith("9. habit"):
        return "habits"
    if h.startswith("10. psychology"):
        return "psychology_thoughts"
    if h.startswith("10a."):
        return "psychology_techniques"
    if h.startswith("11. plateau"):
        return "plateau_actions"
    if h.startswith("12. faq"):
        return "faqs"
    if h.startswith("13. progress tracking"):
        return "tracker_columns"
    if h.startswith("13a.") or h.startswith("13b. key metrics"):
        if "key metrics" in h:
            return "key_metrics"
        return None  # 13a measurements — skip, not in our schema
    return None


# ---------------------------------------------------------------------------
# 5. Build Module data dict for one module
# ---------------------------------------------------------------------------
def build_module_data(slug: str, sections: List[Dict[str, Any]]) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "slug": slug,
        "display_name": None,
        "audience": None,
        "primary_goal": None,
        "pain_level": None,
        "urgency": None,
        "main_barrier": None,
        "is_authored_extension": False,
        "content_pending": False,
        "emotions": [],
        "failed_solutions": [],
        "root_causes": [],
        "nutrition_targets": [],
        "foods": [],
        "foods_to_avoid": [],
        "meal_ideas": [],
        "exercises_recommended": [],
        "exercises_avoid": [],
        "workout_routines": [],
        "constraints": [],
        "habits": [],
        "psychology_thoughts": [],
        "psychology_techniques": [],
        "plateau_actions": [],
        "faqs": [],
        "tracker_columns": [],
        "key_metrics": [],
    }

    seen_sections: set[str] = set()

    for s in sections:
        kind = classify_heading(s["heading"])
        if kind is None:
            continue
        seen_sections.add(kind)
        rows = s["rows"]

        if kind == "problem_profile":
            prof = parse_problem_profile(rows)
            for k in ("audience", "primary_goal", "pain_level", "urgency", "main_barrier"):
                if prof.get(k) is not None:
                    data[k] = prof[k]
            # display_name_raw goes into display_name (keep title-case raw)
            if prof.get("display_name_raw"):
                data["display_name"] = prof["display_name_raw"]
        elif kind == "emotions":
            data["emotions"] = parse_two_col(rows, "emotion", "exact_phrase")
        elif kind == "failed_solutions":
            data["failed_solutions"] = parse_two_col(rows, "solution_tried", "why_it_failed")
        elif kind == "root_causes":
            data["root_causes"] = parse_two_col(rows, "category", "root_cause")
        elif kind == "nutrition_targets":
            data["nutrition_targets"] = parse_two_col(rows, "field_name", "field_value")
        elif kind == "foods_veg":
            data["foods"].extend(parse_foods(rows, "vegetarian"))
        elif kind == "foods_nonveg":
            data["foods"].extend(parse_foods(rows, "non_vegetarian"))
        elif kind == "foods_to_avoid":
            data["foods_to_avoid"] = parse_two_col(rows, "food_type", "why_avoid")
        elif kind == "meal_ideas":
            data["meal_ideas"] = parse_meal_ideas(rows)
        elif kind == "exercises_recommended":
            data["exercises_recommended"] = parse_exercises_recommended(rows)
        elif kind == "exercises_avoid":
            data["exercises_avoid"] = parse_two_col(rows, "exercise_type", "why_avoid")
        elif kind == "workout_routine":
            routine = parse_workout_routine(s["heading"], rows)
            if routine:
                data["workout_routines"].append(routine)
        elif kind == "constraints":
            data["constraints"] = parse_three_col(
                rows, "constraint_name", "solution", "approach", two_col_drop="c"
            )
        elif kind == "habits":
            data["habits"] = parse_three_col(
                rows, "habit_name", "daily_target", "how_to_track", two_col_drop="c"
            )
        elif kind == "psychology_thoughts":
            data["psychology_thoughts"] = parse_three_col(
                rows, "common_thought", "emotional_impact", "solution", two_col_drop="b"
            )
        elif kind == "psychology_techniques":
            data["psychology_techniques"] = parse_two_col(rows, "technique", "how_to_apply")
        elif kind == "plateau_actions":
            data["plateau_actions"] = parse_three_col(
                rows, "trigger_condition", "action_to_take", "timeframe", two_col_drop="c"
            )
        elif kind == "faqs":
            data["faqs"] = parse_two_col(rows, "question", "answer")
        elif kind == "tracker_columns":
            data["tracker_columns"] = parse_tracker_columns(rows)
        elif kind == "key_metrics":
            data["key_metrics"] = parse_three_col(
                rows, "metric_name", "target", "why_important", two_col_drop="c"
            )

    # If display_name didn't get set from Problem Profile, leave existing seed name
    # to be filled by the writer (won't override existing display_name in such case).
    return data


# ---------------------------------------------------------------------------
# 6. Emit a Python seed file from the data dict
# ---------------------------------------------------------------------------
SECTION_MODEL = {
    "emotions": ("Emotion", ["emotion", "exact_phrase", "sort_order"]),
    "failed_solutions": ("FailedSolution", ["solution_tried", "why_it_failed", "sort_order"]),
    "root_causes": ("RootCause", ["category", "root_cause", "sort_order"]),
    "nutrition_targets": ("NutritionTarget", ["field_name", "field_value", "sort_order"]),
    "foods": ("Food", ["diet_type", "food_type", "options", "sort_order"]),
    "foods_to_avoid": ("FoodToAvoid", ["food_type", "why_avoid", "sort_order"]),
    "meal_ideas": ("MealIdea", ["meal_time", "diet_type", "meal_option", "sort_order"]),
    "exercises_recommended": ("ExerciseRecommended", ["exercise_type", "frequency", "duration", "benefits", "sort_order"]),
    "exercises_avoid": ("ExerciseAvoid", ["exercise_type", "why_avoid", "sort_order"]),
    "constraints": ("ModuleConstraint", ["constraint_name", "solution", "approach", "sort_order"]),
    "habits": ("Habit", ["habit_name", "daily_target", "how_to_track", "sort_order"]),
    "psychology_thoughts": ("PsychologyThought", ["common_thought", "emotional_impact", "solution", "sort_order"]),
    "psychology_techniques": ("PsychologyTechnique", ["technique", "how_to_apply", "sort_order"]),
    "plateau_actions": ("PlateauAction", ["trigger_condition", "action_to_take", "timeframe", "sort_order"]),
    "faqs": ("FAQ", ["question", "answer", "sort_order"]),
    "tracker_columns": ("TrackerColumn", ["column_name", "sort_order"]),
    "key_metrics": ("KeyMetric", ["metric_name", "target", "why_important", "sort_order"]),
}


def py_repr(v: Any) -> str:
    """repr that keeps strings clean (uses double quotes) and handles None."""
    if v is None:
        return "None"
    if isinstance(v, bool):
        return repr(v)
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return _quote_string(v)
    raise TypeError(f"unrepr-able: {type(v)}")


def _quote_string(s: str) -> str:
    # Prefer double quotes; escape only what's needed.
    if '"' not in s and "\\" not in s:
        return f'"{s}"'
    if "'" not in s and "\\" not in s:
        return f"'{s}'"
    return repr(s)


def emit_rows(class_name: str, fields: List[str], rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "[]"
    parts = ["["]
    for r in rows:
        kwargs = []
        for f in fields:
            if f in r and r[f] not in (None, ""):
                kwargs.append(f"{f}={py_repr(r[f])}")
        parts.append(f"    {class_name}({', '.join(kwargs)}),")
    parts.append("]")
    return "\n".join(parts)


def emit_workouts(routines: List[Dict[str, Any]]) -> str:
    if not routines:
        return "[]"
    parts = ["["]
    for r in routines:
        ex_parts = []
        for e in r["exercises"]:
            kwargs = []
            for f in ("exercise_name", "reps_or_time", "sets", "rest", "sort_order"):
                if f in e and e[f] not in (None, ""):
                    kwargs.append(f"{f}={py_repr(e[f])}")
            ex_parts.append(f"            WorkoutExercise({', '.join(kwargs)}),")
        parts.append("    WorkoutRoutine(")
        parts.append(f"        time_minutes={r['time_minutes']},")
        parts.append(f"        location={py_repr(r['location'])},")
        if r.get("routine_label"):
            parts.append(f"        routine_label={py_repr(r['routine_label'])},")
        parts.append("        exercises=[")
        parts.extend(ex_parts)
        parts.append("        ],")
        parts.append("    ),")
    parts.append("]")
    return "\n".join(parts)


def emit_seed_file(slug: str, display_name_fallback: str, data: Dict[str, Any]) -> str:
    # Determine which imports we actually need (omit unused symbols)
    used: List[str] = []
    for key, (model, _) in SECTION_MODEL.items():
        if data.get(key):
            used.append(model)
    if data.get("workout_routines"):
        used.extend(["WorkoutExercise", "WorkoutRoutine"])
    used = sorted(set(used))

    imports = ",\n    ".join(used + ["Module"])

    display = data.get("display_name") or display_name_fallback
    head_meta_lines = [
        f"    slug={py_repr(slug)},",
        f"    display_name={py_repr(display)},",
    ]
    for k in ("audience", "primary_goal", "main_barrier"):
        if data.get(k):
            head_meta_lines.append(f"    {k}={py_repr(data[k])},")
    for k in ("pain_level", "urgency"):
        if data.get(k) is not None:
            head_meta_lines.append(f"    {k}={data[k]},")
    head_meta_lines.append("    is_authored_extension=False,")
    head_meta_lines.append("    content_pending=False,")

    section_lines: List[str] = []
    for key in [
        "emotions", "failed_solutions", "root_causes",
        "nutrition_targets", "foods", "foods_to_avoid", "meal_ideas",
        "exercises_recommended", "exercises_avoid",
    ]:
        rows = data.get(key) or []
        if rows:
            class_name, fields = SECTION_MODEL[key]
            section_lines.append(f"    {key}={emit_rows(class_name, fields, rows)},")
    if data.get("workout_routines"):
        section_lines.append(f"    workout_routines={emit_workouts(data['workout_routines'])},")
    for key in [
        "constraints", "habits",
        "psychology_thoughts", "psychology_techniques",
        "plateau_actions", "faqs",
        "tracker_columns", "key_metrics",
    ]:
        rows = data.get(key) or []
        if rows:
            class_name, fields = SECTION_MODEL[key]
            section_lines.append(f"    {key}={emit_rows(class_name, fields, rows)},")

    body = "\n".join(head_meta_lines + section_lines)

    return f'''"""{display} — original module from fitness_database.docx.

Auto-generated from /tmp/fitness_database.docx by scripts/import_docx.py.
Every row below traces to a row in the source DOCX. No content invented.
"""
from models.module import (
    {imports},
)


MODULE = Module(
{body}
)
'''


# ---------------------------------------------------------------------------
# 7. Main
# ---------------------------------------------------------------------------
def main() -> int:
    if not DOCX_PATH.exists():
        print(f"[import][ERROR] DOCX not found at {DOCX_PATH}", file=sys.stderr)
        return 2

    print(f"[import] reading {DOCX_PATH}")
    doc = Document(str(DOCX_PATH))

    print("[import] collecting sections in document order")
    sections = collect_sections(doc)

    groups = group_by_module(sections)
    print(f"[import] grouped into {len(groups)} module blocks")

    if len(groups) != len(SLUGS_IN_ORDER):
        print(
            f"[import][ERROR] expected {len(SLUGS_IN_ORDER)} module blocks "
            f"but found {len(groups)}",
            file=sys.stderr,
        )
        return 3

    expected_sections = {
        "emotions", "failed_solutions", "root_causes", "nutrition_targets",
        "foods_veg", "foods_nonveg", "exercises_recommended", "exercises_avoid",
        "workout_routine", "constraints", "habits",
        "psychology_thoughts", "psychology_techniques",
        "plateau_actions", "faqs", "tracker_columns",
    }

    for slug, group in zip(SLUGS_IN_ORDER, groups):
        print(f"\n[import] === {slug} ===")
        data = build_module_data(slug, group)

        # Warnings for missing-but-expected sections
        present = {classify_heading(s["heading"]) for s in group if classify_heading(s["heading"])}
        missing = sorted(expected_sections - present)
        if missing:
            print(f"[import][warn] {slug}: missing sections -> {missing}")

        # Display fallback if Problem Profile didn't supply a display_name
        fallback_name = data.get("display_name") or slug.replace("_", " ").title()

        seed_path = SEED_DIR / f"{slug}.py"
        contents = emit_seed_file(slug, fallback_name, data)
        seed_path.write_text(contents, encoding="utf-8")
        print(f"[import] wrote {seed_path} ({len(contents)} bytes)")

    print("\n[import] done. Run `python -m seed.seed_all` to reseed Mongo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
