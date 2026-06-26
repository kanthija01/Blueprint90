"""Section A — cover page."""
from __future__ import annotations

from pdf.context import BuildContext, format_date, pretty_goal
from models.blueprint import AssembledBlueprint


def render(ctx: BuildContext, bp: AssembledBlueprint) -> None:
    cover = bp.cover_page
    meta = bp.meta

    def body() -> None:
        ctx.flowables.append(
            ctx._para("YOUR 90-DAY BLUEPRINT", "eyebrow")
        )
        ctx.flowables.append(
            ctx._para(pretty_goal(cover.goal), "cover_display")
        )
        ctx.flowables.append(
            ctx._para(
                f"Generated {format_date(cover.generated_at)} · "
                f"{cover.duration_days} days",
                "muted",
            )
        )
        if cover.biggest_struggle:
            ctx.spacer(10)
            ctx.flowables.append(ctx._para("IN YOUR WORDS", "eyebrow"))
            ctx.flowables.append(
                ctx._para(f'"{cover.biggest_struggle}"', "body")
            )

        if meta.modules_used:
            ctx.spacer(10)
            ctx.flowables.append(ctx._para("MODULES USED", "eyebrow"))
            for mod in meta.modules_used:
                label = mod.display_name
                if mod.slug == meta.primary_module_slug:
                    label = f"{label} (primary)"
                ctx.flowables.append(ctx._para(label, "body_strong"))
                if mod.is_fallback and mod.fallback_note:
                    ctx.flowables.append(
                        ctx._para(f"Fallback: {mod.fallback_note}", "muted")
                    )

    ctx.section("A", "COVER", "Your blueprint at a glance.", body_fn=body)
