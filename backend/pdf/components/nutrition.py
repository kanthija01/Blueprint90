"""Section D — nutrition strategy."""
from __future__ import annotations

from pdf.context import BuildContext, BulletRow, pretty_slug
from models.blueprint import AssembledBlueprint


def render(ctx: BuildContext, bp: AssembledBlueprint) -> None:
    ns = bp.nutrition_strategy
    target_rows = [
        BulletRow(primary=t.field_name, secondary=t.field_value)
        for t in ns.targets
    ]
    food_rows = [
        BulletRow(label=f.food_type.upper(), primary=f.options) for f in ns.foods
    ]
    avoid_rows = [
        BulletRow(
            label="AVOID",
            primary=f.food_type,
            secondary=f.why_avoid,
        )
        for f in ns.foods_to_avoid
    ]
    meal_rows = [
        BulletRow(label=m.meal_time.upper(), primary=m.meal_option)
        for m in ns.meal_ideas
    ]
    empty = not (
        target_rows or food_rows or avoid_rows or meal_rows
    )

    def body() -> None:
        if target_rows:
            ctx.sub_heading("TARGETS")
            ctx.bullet_list(target_rows)
            ctx.spacer(6)
        if food_rows:
            ctx.sub_heading("FOODS")
            ctx.bullet_list(food_rows)
            ctx.spacer(6)
        if avoid_rows:
            ctx.sub_heading("FOODS TO AVOID")
            ctx.bullet_list(avoid_rows)
            ctx.spacer(6)
        if meal_rows:
            ctx.sub_heading("MEAL IDEAS")
            ctx.bullet_list(meal_rows)

    ctx.section(
        "D",
        "NUTRITION STRATEGY",
        f"Engineered for {pretty_slug(ns.diet)}.",
        subtitle=f"Primary module: {pretty_slug(ns.source_module)}",
        empty=empty,
        empty_label=(
            "The primary module for this blueprint doesn't define nutrition "
            "targets or meal guidance."
        ),
        body_fn=body,
    )
