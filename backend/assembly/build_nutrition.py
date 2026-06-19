"""Builds the NutritionStrategy section.

Per the architecture doc:
  - Primary module owns ALL nutrition fields (one source of truth for numeric
    targets — never concatenate conflicting protein/fiber targets).
  - foods and meal_ideas are filtered by assessment.diet (strict; no fallback).
  - foods_to_avoid is diet-agnostic (the avoid list applies regardless of diet).

PURE function. No DB. No LLM.
"""
from __future__ import annotations

from models.blueprint import (
    FoodItem,
    FoodToAvoidItem,
    MealIdeaItem,
    NutritionStrategy,
    NutritionTargetItem,
)
from models.module import Module
from rules_engine.types import Assessment


def build_nutrition_strategy(
    primary_module: Module,
    assessment: Assessment,
) -> NutritionStrategy:
    targets = [
        NutritionTargetItem(field_name=t.field_name, field_value=t.field_value)
        for t in primary_module.nutrition_targets
    ]

    foods = [
        FoodItem(food_type=f.food_type, options=f.options)
        for f in primary_module.foods
        if f.diet_type == assessment.diet
    ]

    meal_ideas = [
        MealIdeaItem(meal_time=m.meal_time, meal_option=m.meal_option)
        for m in primary_module.meal_ideas
        if m.diet_type == assessment.diet
    ]

    foods_to_avoid = [
        FoodToAvoidItem(food_type=fa.food_type, why_avoid=fa.why_avoid)
        for fa in primary_module.foods_to_avoid
    ]

    return NutritionStrategy(
        diet=assessment.diet,
        targets=targets,
        foods=foods,
        foods_to_avoid=foods_to_avoid,
        meal_ideas=meal_ideas,
        source_module=primary_module.slug,
    )
