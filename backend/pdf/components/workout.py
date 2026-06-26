"""Section E — workout plan."""
from __future__ import annotations

from pdf.context import BuildContext, BulletRow, pretty_slug
from models.blueprint import AssembledBlueprint


def render(ctx: BuildContext, bp: AssembledBlueprint) -> None:
    wp = bp.workout_plan

    def body() -> None:
        exercises = [
            BulletRow(
                primary=e.exercise_name,
                secondary=" · ".join(
                    p
                    for p in [
                        f"{e.sets} sets" if e.sets else None,
                        e.reps_or_time,
                        f"rest {e.rest}" if e.rest else None,
                    ]
                    if p
                ),
            )
            for e in wp.exercises
        ]
        swaps = [
            BulletRow(
                label=c.constraint_name.upper(),
                primary=c.solution,
                secondary=c.approach,
            )
            for c in wp.constraint_swaps
        ]
        avoid = [
            BulletRow(
                label="AVOID",
                primary=e.exercise_type,
                secondary=e.why_avoid,
            )
            for e in wp.exercises_to_avoid
        ]
        if exercises:
            ctx.sub_heading("EXERCISES")
            ctx.bullet_list(exercises)
            ctx.spacer(6)
        if swaps:
            ctx.sub_heading("CONSTRAINT SWAPS")
            ctx.bullet_list(swaps)
            ctx.spacer(6)
        if avoid:
            ctx.sub_heading("AVOID")
            ctx.bullet_list(avoid)

    if wp is None:
        ctx.section(
            "E",
            "WORKOUT PLAN",
            "No workout routine",
            empty=True,
            empty_label=(
                "The primary module for this blueprint doesn't define a workout "
                "routine. See the standalone module if applicable."
            ),
        )
    else:
        title = f"{wp.time_minutes} min · {pretty_slug(wp.location)}"
        ctx.section(
            "E",
            "WORKOUT PLAN",
            title,
            subtitle=wp.routine_label,
            empty=not (
                wp.exercises or wp.constraint_swaps or wp.exercises_to_avoid
            ),
            body_fn=body,
        )
