"""Section J — weekly milestones."""
from __future__ import annotations

from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle

from pdf.context import BuildContext, MILESTONE_BG, PRIMARY, BORDER
from models.blueprint import AssembledBlueprint

_REVIEW_WEEKS = {1, 4, 8, 12}


def render(ctx: BuildContext, bp: AssembledBlueprint) -> None:
    milestones = bp.weekly_milestones

    def body() -> None:
        for m in milestones:
            milestone = m.week in _REVIEW_WEEKS
            badge = f"WK {m.week}"
            focus_para = ctx._para(m.focus, "body_strong")
            rows = [[ctx._para(badge, "label"), focus_para]]
            table = Table(rows, colWidths=[0.7 * inch, None])
            style_cmds = [
                ("BOX", (0, 0), (-1, -1), 1, PRIMARY if milestone else BORDER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
            if milestone:
                style_cmds.append(("BACKGROUND", (0, 0), (-1, -1), MILESTONE_BG))
            table.setStyle(TableStyle(style_cmds))
            ctx.flowables.append(table)

            if m.checklist_items:
                for item in m.checklist_items:
                    ctx.flowables.append(
                        ctx._para(f"□ {item}", "muted")
                    )
            ctx.spacer(6)

    ctx.section(
        "J",
        "WEEKLY MILESTONES",
        "The 12-week structure.",
        subtitle="Weeks 1, 4, 8 and 12 are review weeks.",
        empty=len(milestones) == 0,
        body_fn=body,
    )
