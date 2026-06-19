"""Vegetarian Muscle Building — original module from fitness_database.docx.

Auto-generated from /tmp/fitness_database.docx by scripts/import_docx.py.
Every row below traces to a row in the source DOCX. No content invented.
"""
from models.module import (
    Emotion,
    ExerciseRecommended,
    FailedSolution,
    NutritionTarget,
    RootCause,
    Module,
)


MODULE = Module(
    slug="plant_power",
    display_name="Vegetarian Muscle Building",
    audience="Vegetarians/vegans aged 18-35, strength training",
    primary_goal="Build muscle on plants",
    main_barrier="Protein enough but muscle won't build; amino acids missing",
    pain_level=7,
    urgency=7,
    is_authored_extension=False,
    content_pending=False,
    emotions=[
    Emotion(emotion="Frustration", exact_phrase="Plant protein less efficient at building muscle", sort_order=1),
    Emotion(emotion="Planning", exact_phrase="needs more planning", sort_order=2),
    Emotion(emotion="Protein", exact_phrase="get enough protein but not enough what it's made of", sort_order=3),
    Emotion(emotion="Nutrients", exact_phrase="missing key muscle-building nutrients", sort_order=4),
    Emotion(emotion="Frustration", exact_phrase="Frustration at plateau", sort_order=5),
    Emotion(emotion="Restricted", exact_phrase="feeling restricted", sort_order=6),
    Emotion(emotion="Doubt", exact_phrase="doubt about diet choice", sort_order=7),
],
    failed_solutions=[
    FailedSolution(solution_tried="Solution", why_it_failed="Why Failed", sort_order=1),
    FailedSolution(solution_tried="Eating more beans", why_it_failed="Amino acids incomplete", sort_order=2),
    FailedSolution(solution_tried="Random protein powder", why_it_failed="Not targeted", sort_order=3),
    FailedSolution(solution_tried="Standard programs", why_it_failed="Animal-based; not vegan", sort_order=4),
    FailedSolution(solution_tried="Ignoring amino acids", why_it_failed="Muscle won't build", sort_order=5),
],
    root_causes=[
    RootCause(category="Biological", root_cause="Amino acid completeness not addressed", sort_order=1),
    RootCause(category="Knowledge", root_cause="Don't know which plant proteins combine", sort_order=2),
    RootCause(category="Knowledge", root_cause="Advice assumes meat", sort_order=3),
],
    nutrition_targets=[
    NutritionTarget(field_name="Field", field_value="Details", sort_order=1),
    NutritionTarget(field_name="Protein", field_value="100-120g", sort_order=2),
    NutritionTarget(field_name="Foods", field_value="Paneer, Tofu, Moong dal, Lentils, Chickpeas, Greek yogurt", sort_order=3),
    NutritionTarget(field_name="Amino Acids", field_value="Combine: grains + legumes", sort_order=4),
],
    exercises_recommended=[
    ExerciseRecommended(exercise_type="Strength", frequency="4x/week", duration="40 min", sort_order=1),
    ExerciseRecommended(exercise_type="Walking", frequency="Daily", duration="20 min", sort_order=2),
],
)
