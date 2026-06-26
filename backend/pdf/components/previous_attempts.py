"""Section B — why previous attempts failed."""
from __future__ import annotations

from pdf.context import BuildContext, BulletRow, pretty_slug
from models.blueprint import AssembledBlueprint


def render(ctx: BuildContext, bp: AssembledBlueprint) -> None:
    rows = [
        BulletRow(
            label="TRIED",
            primary=item.solution_tried,
            secondary=item.why_it_failed,
            source=pretty_slug(item.source_module),
        )
        for item in bp.why_previous_attempts_failed
    ]

    def body() -> None:
        ctx.bullet_list(rows)

    ctx.section(
        "B",
        "WHY PREVIOUS ATTEMPTS FAILED",
        "What didn't work, and why.",
        empty=len(rows) == 0,
        empty_label="No prior attempts logged.",
        body_fn=body,
    )
