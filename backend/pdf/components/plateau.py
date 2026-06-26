"""Section I — plateau playbook."""
from __future__ import annotations

from pdf.context import BuildContext, BulletRow, pretty_slug
from models.blueprint import AssembledBlueprint


def render(ctx: BuildContext, bp: AssembledBlueprint) -> None:
    rows = [
        BulletRow(
            label=p.trigger_condition.upper(),
            primary=p.action_to_take,
            secondary=p.timeframe,
            source=pretty_slug(p.source_module),
        )
        for p in bp.plateau_playbook
    ]

    def body() -> None:
        ctx.bullet_list(rows)

    ctx.section(
        "I",
        "PLATEAU PLAYBOOK",
        "When progress stalls, do this.",
        empty=len(rows) == 0,
        empty_label="No plateau actions defined for this module.",
        body_fn=body,
    )
