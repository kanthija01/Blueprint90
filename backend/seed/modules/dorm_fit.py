"""College Dorm Fitness — original module from fitness_database.docx.

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
    slug="dorm_fit",
    display_name="College Dorm Fitness",
    audience="College students aged 18-24, living on campus",
    primary_goal="Weight control + energy",
    main_barrier="Free food everywhere; no kitchen; class chaos",
    pain_level=7,
    urgency=7,
    is_authored_extension=False,
    content_pending=False,
    emotions=[
    Emotion(emotion="Struggle", exact_phrase="Lifestyle and weight struggles", sort_order=1),
    Emotion(emotion="Eating", exact_phrase="hard time eating", sort_order=2),
    Emotion(emotion="Time", exact_phrase="finding time to workout", sort_order=3),
    Emotion(emotion="Food", exact_phrase="free food available", sort_order=4),
    Emotion(emotion="Eating", exact_phrase="mindless eating", sort_order=5),
    Emotion(emotion="Food", exact_phrase="always free food", sort_order=6),
    Emotion(emotion="Shame", exact_phrase="Freshman 15 shame", sort_order=7),
    Emotion(emotion="Control", exact_phrase="feeling out of control", sort_order=8),
    Emotion(emotion="Anxiety", exact_phrase="anxiety about health", sort_order=9),
],
    failed_solutions=[
    FailedSolution(solution_tried="Solution", why_it_failed="Why Failed", sort_order=1),
    FailedSolution(solution_tried="Long gym sessions", why_it_failed="No time", sort_order=2),
    FailedSolution(solution_tried="Meal prep", why_it_failed="No kitchen", sort_order=3),
    FailedSolution(solution_tried="Calorie tracking", why_it_failed="Forget", sort_order=4),
    FailedSolution(solution_tried="Running", why_it_failed="No time", sort_order=5),
],
    root_causes=[
    RootCause(category="Lifestyle", root_cause="Free food everywhere", sort_order=1),
    RootCause(category="Lifestyle", root_cause="No cooking facilities", sort_order=2),
    RootCause(category="Lifestyle", root_cause="Class schedule chaos", sort_order=3),
    RootCause(category="Lifestyle", root_cause="2-hour workouts impossible", sort_order=4),
],
    nutrition_targets=[
    NutritionTarget(field_name="Field", field_value="Details", sort_order=1),
    NutritionTarget(field_name="Protein", field_value="100-120g", sort_order=2),
    NutritionTarget(field_name="Foods", field_value="Greek yogurt, Protein bars, Nuts, Eggs (if microwave)", sort_order=3),
    NutritionTarget(field_name="No Kitchen", field_value="Grab-and-go only", sort_order=4),
],
    exercises_recommended=[
    ExerciseRecommended(exercise_type="Exercise", frequency="Reps", duration="Time", sort_order=1),
    ExerciseRecommended(exercise_type="Body Squats", frequency="15 reps", duration="3 min", sort_order=2),
    ExerciseRecommended(exercise_type="Push-ups", frequency="10 reps", duration="3 min", sort_order=3),
    ExerciseRecommended(exercise_type="Glute Bridges", frequency="15 reps", duration="3 min", sort_order=4),
    ExerciseRecommended(exercise_type="Plank", frequency="30 sec", duration="2 min", sort_order=5),
    ExerciseRecommended(exercise_type="Stretch", frequency="—", duration="2 min", sort_order=6),
],
)
