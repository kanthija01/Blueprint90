"""Gym Anxiety (Men) — original module from fitness_database.docx.

Auto-generated from /tmp/fitness_database.docx by scripts/import_docx.py.
Every row below traces to a row in the source DOCX. No content invented.
"""
from models.module import (
    Emotion,
    FailedSolution,
    RootCause,
    Module,
)


MODULE = Module(
    slug="gym_confidence",
    display_name="Gym Anxiety (Men)",
    audience="Men aged 18-35, first-time gym or returning",
    primary_goal="Gym confidence",
    main_barrier="Fear of judgment; don't know machines; anxiety",
    pain_level=6,
    urgency=6,
    is_authored_extension=False,
    content_pending=False,
    emotions=[
    Emotion(emotion="Anxiety", exact_phrase="Gym anxiety", sort_order=1),
    Emotion(emotion="Anxiety", exact_phrase="gymtimidation", sort_order=2),
    Emotion(emotion="Fear", exact_phrase="intimidated", sort_order=3),
    Emotion(emotion="Fear", exact_phrase="panicky", sort_order=4),
    Emotion(emotion="Anxiety", exact_phrase="feeling really anxious", sort_order=5),
    Emotion(emotion="Confidence", exact_phrase="not confident", sort_order=6),
    Emotion(emotion="First", exact_phrase="first day", sort_order=7),
],
    failed_solutions=[
    FailedSolution(solution_tried="Solution", why_it_failed="Why Failed", sort_order=1),
    FailedSolution(solution_tried="Watching YouTube", why_it_failed="Too much info; confusing", sort_order=2),
    FailedSolution(solution_tried="Going at busy times", why_it_failed="More anxiety", sort_order=3),
    FailedSolution(solution_tried="Random machine use", why_it_failed="Don't know what to do", sort_order=4),
    FailedSolution(solution_tried="Avoiding gym", why_it_failed="No progress", sort_order=5),
],
    root_causes=[
    RootCause(category="Psychological", root_cause="Fear of judgment", sort_order=1),
    RootCause(category="Psychological", root_cause="Shame about weakness", sort_order=2),
    RootCause(category="Psychological", root_cause="Anxiety paralyzes", sort_order=3),
    RootCause(category="Knowledge", root_cause="Don't know which machine", sort_order=4),
],
)
