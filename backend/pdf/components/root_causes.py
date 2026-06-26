"""Section C — root causes."""
from __future__ import annotations

from pdf.context import BuildContext, BulletRow, pretty_slug
from models.blueprint import AssembledBlueprint


def render(ctx: BuildContext, bp: AssembledBlueprint) -> None:
    rows = [
        BulletRow(
            label=item.category.upper(),
            primary=item.root_cause,
            source=pretty_slug(item.source_module),
        )
        for item in bp.root_causes
    ]

    def body() -> None:
        ctx.bullet_list(rows)

    ctx.section(
        "C",
        "ROOT CAUSES",
        "What's actually driving this.",
        empty=len(rows) == 0,
        body_fn=body,
    )
