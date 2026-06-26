"""Section H — FAQs."""
from __future__ import annotations

from pdf.context import BuildContext, BulletRow, pretty_slug
from models.blueprint import AssembledBlueprint


def render(ctx: BuildContext, bp: AssembledBlueprint) -> None:
    rows = [
        BulletRow(
            label="Q",
            primary=f.question,
            secondary=f.answer,
            source=pretty_slug(f.source_module),
        )
        for f in bp.faqs
    ]

    def body() -> None:
        ctx.bullet_list(rows)

    ctx.section(
        "H",
        "FAQS",
        "Quick answers to common questions.",
        empty=len(rows) == 0,
        body_fn=body,
    )
