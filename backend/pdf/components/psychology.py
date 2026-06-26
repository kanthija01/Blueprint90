"""Section G — psychology system."""
from __future__ import annotations

from pdf.context import BuildContext, BulletRow, pretty_slug
from models.blueprint import AssembledBlueprint


def render(ctx: BuildContext, bp: AssembledBlueprint) -> None:
    ps = bp.psychology_system
    thought_rows = [
        BulletRow(
            label="THOUGHT",
            primary=t.common_thought,
            secondary=" → ".join(
                p for p in [t.emotional_impact, t.solution] if p
            ),
            source=pretty_slug(t.source_module),
        )
        for t in ps.common_thoughts
    ]
    technique_rows = [
        BulletRow(
            label="TECHNIQUE",
            primary=t.technique,
            secondary=t.how_to_apply,
            source=pretty_slug(t.source_module),
        )
        for t in ps.techniques
    ]
    empty = not thought_rows and not technique_rows

    def body() -> None:
        if thought_rows:
            ctx.sub_heading("COMMON THOUGHTS")
            ctx.bullet_list(thought_rows)
            ctx.spacer(6)
        if technique_rows:
            ctx.sub_heading("TECHNIQUES")
            ctx.bullet_list(technique_rows)

    ctx.section(
        "G",
        "PSYCHOLOGY SYSTEM",
        "What you'll think, and what to do.",
        empty=empty,
        body_fn=body,
    )
