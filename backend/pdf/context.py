"""Shared ReportLab build context for blueprint PDF sections."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

# Brand tokens (aligned with frontend theme).
PRIMARY = colors.HexColor("#FFD60A")
TEXT = colors.HexColor("#1A1A1A")
TEXT_MUTED = colors.HexColor("#6B6B6B")
BORDER = colors.HexColor("#E0E0E0")
CARD_BG = colors.HexColor("#F7F7F7")
MILESTONE_BG = colors.HexColor("#FFF9E0")

PAGE_MARGIN = 0.65 * inch
SECTION_GAP = 14


def pretty_goal(goal: str) -> str:
    return goal.replace("_", " ").title()


def pretty_slug(slug: str) -> str:
    return slug.replace("_", " ").title()


def format_date(iso: str) -> str:
    from datetime import datetime

    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%d %b %Y")
    except ValueError:
        return iso


@dataclass
class BulletRow:
    label: Optional[str] = None
    primary: str = ""
    secondary: Optional[str] = None
    source: Optional[str] = None


@dataclass
class BuildContext:
    """Accumulates platypus flowables for one blueprint PDF."""

    flowables: List = field(default_factory=list)
    styles: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        base = getSampleStyleSheet()
        self.styles = {
            "eyebrow": ParagraphStyle(
                "Eyebrow",
                parent=base["Normal"],
                fontName="Helvetica-Bold",
                fontSize=8,
                leading=10,
                textColor=TEXT_MUTED,
                spaceAfter=2,
            ),
            "title": ParagraphStyle(
                "Title",
                parent=base["Normal"],
                fontName="Helvetica-Bold",
                fontSize=14,
                leading=17,
                textColor=TEXT,
                spaceAfter=4,
            ),
            "subtitle": ParagraphStyle(
                "Subtitle",
                parent=base["Normal"],
                fontName="Helvetica",
                fontSize=9,
                leading=12,
                textColor=TEXT_MUTED,
                spaceAfter=6,
            ),
            "body": ParagraphStyle(
                "Body",
                parent=base["Normal"],
                fontName="Helvetica",
                fontSize=10,
                leading=13,
                textColor=TEXT,
            ),
            "body_strong": ParagraphStyle(
                "BodyStrong",
                parent=base["Normal"],
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=13,
                textColor=TEXT,
            ),
            "label": ParagraphStyle(
                "Label",
                parent=base["Normal"],
                fontName="Helvetica-Bold",
                fontSize=8,
                leading=10,
                textColor=PRIMARY,
            ),
            "muted": ParagraphStyle(
                "Muted",
                parent=base["Normal"],
                fontName="Helvetica",
                fontSize=9,
                leading=12,
                textColor=TEXT_MUTED,
            ),
            "empty": ParagraphStyle(
                "Empty",
                parent=base["Normal"],
                fontName="Helvetica-Oblique",
                fontSize=9,
                leading=12,
                textColor=TEXT_MUTED,
            ),
            "cover_display": ParagraphStyle(
                "CoverDisplay",
                parent=base["Normal"],
                fontName="Helvetica-Bold",
                fontSize=22,
                leading=26,
                textColor=PRIMARY,
                spaceAfter=6,
            ),
            "footer": ParagraphStyle(
                "Footer",
                parent=base["Normal"],
                fontName="Helvetica",
                fontSize=8,
                leading=10,
                textColor=TEXT_MUTED,
                alignment=TA_LEFT,
            ),
        }

    def spacer(self, height: float = SECTION_GAP) -> None:
        self.flowables.append(Spacer(1, height))

    def _para(self, text: str, style_name: str) -> Paragraph:
        safe = (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br/>")
        )
        return Paragraph(safe, self.styles[style_name])

    def section_block(
        self,
        letter: str,
        eyebrow: str,
        title: str,
        subtitle: Optional[str] = None,
    ) -> None:
        letter_cell = self._para(letter, "label")
        header_bits = [
            self._para(eyebrow, "eyebrow"),
            self._para(title, "title"),
        ]
        if subtitle:
            header_bits.append(self._para(subtitle, "subtitle"))
        header_table = Table(
            [[letter_cell, header_bits]],
            colWidths=[0.45 * inch, None],
        )
        header_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ("BOX", (0, 0), (0, 0), 1, BORDER),
                    ("BACKGROUND", (0, 0), (0, 0), CARD_BG),
                    ("ALIGN", (0, 0), (0, 0), "CENTER"),
                ]
            )
        )
        self.flowables.append(header_table)

    def sub_heading(self, text: str) -> None:
        self.flowables.append(self._para(text, "eyebrow"))
        self.spacer(4)

    def empty_note(self, text: str) -> None:
        self.flowables.append(self._para(text, "empty"))

    def bullet_list(self, rows: List[BulletRow]) -> None:
        if not rows:
            return
        for row in rows:
            bits: List[Paragraph] = []
            if row.label:
                bits.append(self._para(row.label, "label"))
            bits.append(self._para(row.primary, "body_strong"))
            if row.secondary:
                bits.append(self._para(row.secondary, "muted"))
            if row.source:
                bits.append(self._para(f"from {row.source}", "muted"))
            inner = Table([[bits]], colWidths=[None])
            inner.setStyle(
                TableStyle(
                    [
                        ("LEFTPADDING", (0, 0), (-1, -1), 10),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("LINEBEFORE", (0, 0), (0, -1), 2, PRIMARY),
                    ]
                )
            )
            self.flowables.append(inner)
            self.spacer(4)

    def card_wrap(self, inner_flowables: List) -> None:
        table = Table([[inner_flowables]], colWidths=[None])
        table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 1, BORDER),
                    ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ]
            )
        )
        self.flowables.append(table)

    def section(
        self,
        letter: str,
        eyebrow: str,
        title: str,
        subtitle: Optional[str] = None,
        empty: bool = False,
        empty_label: Optional[str] = None,
        body_fn=None,
    ) -> None:
        """Render one A–K section card."""
        inner: List = []
        saved = self.flowables
        self.flowables = inner

        self.section_block(letter, eyebrow, title, subtitle)
        self.spacer(8)
        if empty:
            self.empty_note(empty_label or "Nothing to show in this section yet.")
        elif body_fn:
            body_fn()

        self.flowables = saved
        self.card_wrap(inner)
        self.spacer(SECTION_GAP)
