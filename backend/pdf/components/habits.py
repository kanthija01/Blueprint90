"""Section F — habit system."""
from __future__ import annotations

from pdf.context import BuildContext, BulletRow, pretty_slug
from models.blueprint import AssembledBlueprint


def render(ctx: BuildContext, bp: AssembledBlueprint) -> None:
    rows = [
        BulletRow(
            primary=h.habit_name,
            secondary=" · ".join(
                p for p in [h.daily_target, h.how_to_track] if p
            ),
            source=pretty_slug(h.source_module),
        )
        for h in bp.habit_system
    ]

    def body() -> None:
        ctx.bullet_list(rows)

    ctx.section(
        "F",
        "HABIT SYSTEM",
        "The daily moves that compound.",
        empty=len(rows) == 0,
        body_fn=body,
    )
