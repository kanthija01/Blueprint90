"""Section K — progress tracker grid."""
from __future__ import annotations

from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle

from pdf.context import BuildContext, BORDER, CARD_BG, TEXT
from models.blueprint import AssembledBlueprint


def render(ctx: BuildContext, bp: AssembledBlueprint) -> None:
    tracker = bp.progress_tracker
    columns = tracker.columns
    weeks = tracker.weeks

    def body() -> None:
        header = [ctx._para("Week", "eyebrow")]
        for col in columns:
            header.append(ctx._para(col, "label"))
        data = [header]

        for wk in weeks:
            row = [ctx._para(str(wk), "body_strong")]
            for _ in columns:
                row.append(ctx._para("", "body"))
            data.append(row)

        col_widths = [0.55 * inch] + [1.1 * inch] * len(columns)
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                    ("BACKGROUND", (0, 0), (-1, 0), CARD_BG),
                    ("TEXTCOLOR", (0, 0), (-1, 0), TEXT),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        ctx.flowables.append(table)
        if not columns:
            ctx.spacer(6)
            ctx.empty_note("No tracker columns defined for this module.")

    ctx.section(
        "K",
        "PROGRESS TRACKER",
        "Track what matters, week over week.",
        subtitle="Fill in each cell week over week.",
        body_fn=body,
    )
