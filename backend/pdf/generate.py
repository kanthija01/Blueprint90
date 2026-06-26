"""Generate blueprint PDFs from cached assembled_json using ReportLab.

Never invokes the assembly engine — callers pass an `AssembledBlueprint`
parsed from Mongo `assembled_json`.
"""
from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate

from models.blueprint import AssembledBlueprint
from pdf.components.cover_page import render as render_cover
from pdf.components.faq import render as render_faq
from pdf.components.habits import render as render_habits
from pdf.components.nutrition import render as render_nutrition
from pdf.components.plateau import render as render_plateau
from pdf.components.previous_attempts import render as render_previous_attempts
from pdf.components.progress_tracker import render as render_progress_tracker
from pdf.components.psychology import render as render_psychology
from pdf.components.root_causes import render as render_root_causes
from pdf.components.weekly_milestones import render as render_weekly_milestones
from pdf.components.workout import render as render_workout
from pdf.context import BuildContext, PAGE_MARGIN

BACKEND_ROOT = Path(__file__).resolve().parent.parent
STORAGE_DIR = BACKEND_ROOT / "storage" / "blueprints"


def blueprint_pdf_path(blueprint_id: str) -> Path:
    return STORAGE_DIR / f"{blueprint_id}.pdf"


def generate_blueprint_pdf(
    blueprint: AssembledBlueprint,
    output_path: Path | None = None,
    blueprint_id: str | None = None,
) -> Path:
    """Build a PDF and write it to `output_path` (or the default storage path)."""
    if output_path is None:
        if blueprint_id is None:
            raise ValueError("blueprint_id required when output_path is omitted")
        output_path = blueprint_pdf_path(blueprint_id)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=PAGE_MARGIN,
        rightMargin=PAGE_MARGIN,
        topMargin=PAGE_MARGIN,
        bottomMargin=PAGE_MARGIN,
        title="Blueprint90 — 90-Day Blueprint",
        author="Blueprint90",
    )

    ctx = BuildContext()
    # Sections A–K — same order as Phase 5 in-app preview.
    render_cover(ctx, blueprint)
    render_previous_attempts(ctx, blueprint)
    render_root_causes(ctx, blueprint)
    render_nutrition(ctx, blueprint)
    render_workout(ctx, blueprint)
    render_habits(ctx, blueprint)
    render_psychology(ctx, blueprint)
    render_faq(ctx, blueprint)
    render_plateau(ctx, blueprint)
    render_weekly_milestones(ctx, blueprint)
    render_progress_tracker(ctx, blueprint)

    ctx.spacer(8)
    ctx.flowables.append(
        ctx._para(
            f"Deterministically assembled from "
            f"{len(blueprint.meta.modules_used)} verified modules. No AI advice.",
            "footer",
        )
    )

    doc.build(ctx.flowables)
    return output_path
