"""Consistency Failure (Women) — original module from fitness_database.docx.

Auto-generated from /tmp/fitness_database.docx by scripts/import_docx.py.
Every row below traces to a row in the source DOCX. No content invented.
"""
from models.module import (
    Emotion,
    ExerciseRecommended,
    FailedSolution,
    Habit,
    ModuleConstraint,
    NutritionTarget,
    PsychologyThought,
    RootCause,
    Module,
)


MODULE = Module(
    slug="consistency_code",
    display_name="Consistency Failure (Women)",
    audience="Women aged 20-45, multiple failed fitness attempts",
    primary_goal="Consistent fitness without perfection",
    main_barrier="Programs don't match energy; exercises feel awful; no time",
    pain_level=8,
    urgency=8,
    is_authored_extension=False,
    content_pending=False,
    emotions=[
    Emotion(emotion="Consistency", exact_phrase="Can't stay consistent", sort_order=1),
    Emotion(emotion="Pain", exact_phrase="exercises I have to lay down for", sort_order=2),
    Emotion(emotion="Sensory", exact_phrase="sensory issues", sort_order=3),
    Emotion(emotion="Exhaustion", exact_phrase="tiredness from juggling excessive workloads, household chores, family obligations", sort_order=4),
    Emotion(emotion="Shame", exact_phrase="Shame cycle (start → quit → shame)", sort_order=5),
    Emotion(emotion="Trust", exact_phrase="self-trust broken", sort_order=6),
    Emotion(emotion="Failure", exact_phrase="feeling like always fails", sort_order=7),
    Emotion(emotion="Depression", exact_phrase="depression from repeated failure", sort_order=8),
],
    failed_solutions=[
    FailedSolution(solution_tried="60-min classes", why_it_failed="Too long; no time", sort_order=1),
    FailedSolution(solution_tried="Intense programs", why_it_failed="Too exhausting; don't match energy", sort_order=2),
    FailedSolution(solution_tried="Morning workouts", why_it_failed="Don't have time carved out", sort_order=3),
    FailedSolution(solution_tried="Exercises they dislike", why_it_failed="Feel awful; can't stick with", sort_order=4),
],
    root_causes=[
    RootCause(category="Lifestyle", root_cause="Programs don't match energy levels", sort_order=1),
    RootCause(category="Lifestyle", root_cause="Exercises feel awful (disliked)", sort_order=2),
    RootCause(category="Lifestyle", root_cause="Overlapping roles exhaust them", sort_order=3),
    RootCause(category="Lifestyle", root_cause="No time carved out", sort_order=4),
    RootCause(category="Psychological", root_cause="Shame cycle", sort_order=5),
    RootCause(category="Psychological", root_cause="Self-trust broken", sort_order=6),
    RootCause(category="Psychological", root_cause="Feeling like always fails", sort_order=7),
    RootCause(category="Sensory", root_cause="Sensory issues ignored", sort_order=8),
],
    nutrition_targets=[
    NutritionTarget(field_name="Field", field_value="Details", sort_order=1),
    NutritionTarget(field_name="Protein Target", field_value="100-120g per day", sort_order=2),
    NutritionTarget(field_name="Simplicity", field_value="Easy meals; no prep needed", sort_order=3),
    NutritionTarget(field_name="Consistency", field_value="3 meals/day; no fasting", sort_order=4),
],
    exercises_recommended=[
    ExerciseRecommended(exercise_type="Exercise Type", frequency="When to Do", duration="Duration", benefits="Benefit", sort_order=1),
    ExerciseRecommended(exercise_type="Walking", frequency="High energy OR low energy", duration="15-20 min", benefits="Always enjoyable", sort_order=2),
    ExerciseRecommended(exercise_type="Yoga", frequency="Low energy", duration="15 min", benefits="Relaxing; enjoyable", sort_order=3),
    ExerciseRecommended(exercise_type="Strength (favorite)", frequency="High energy", duration="20 min", benefits="Only favorite exercises", sort_order=4),
    ExerciseRecommended(exercise_type="Pilates", frequency="Medium energy", duration="15 min", benefits="Enjoyable; low impact", sort_order=5),
],
    constraints=[
    ModuleConstraint(constraint_name="Low energy", solution="Yoga or walking only", sort_order=1),
    ModuleConstraint(constraint_name="High energy", solution="Favorite strength exercises", sort_order=2),
    ModuleConstraint(constraint_name="No time", solution="15-min routine", sort_order=3),
    ModuleConstraint(constraint_name="Sensory issues", solution="Choose comfortable exercises", sort_order=4),
],
    habits=[
    Habit(habit_name="Habit", daily_target="Target", how_to_track="Tip", sort_order=1),
    Habit(habit_name="Workout", daily_target="3x/week (15 min)", how_to_track="Only favorite exercises", sort_order=2),
    Habit(habit_name="Energy match", daily_target="Match workout to energy", how_to_track="Low = yoga; High = strength", sort_order=3),
],
    psychology_thoughts=[
    PsychologyThought(common_thought="I always fail.", solution='"Throw away exercises you hate; only do what you enjoy"', sort_order=1),
    PsychologyThought(common_thought="Self-trust broken.", solution="15-min workouts = still counts", sort_order=2),
    PsychologyThought(common_thought="Always fails.", solution="Enjoyment-based = sustainable", sort_order=3),
],
)
