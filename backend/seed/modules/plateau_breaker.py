"""Weight Loss Plateau — original module from fitness_database.docx.

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
    slug="plateau_breaker",
    display_name="Weight Loss Plateau",
    audience="People aged 25-50, 3+ months weight loss, now plateaued",
    primary_goal="Break plateau",
    main_barrier="Metabolism protecting; more effort = less result",
    pain_level=8,
    urgency=8,
    is_authored_extension=False,
    content_pending=False,
    emotions=[
    Emotion(emotion="Plateau", exact_phrase="Weight-loss plateau", sort_order=1),
    Emotion(emotion="Stop", exact_phrase="stop losing despite consistent diet and exercise", sort_order=2),
    Emotion(emotion="Metabolic", exact_phrase="metabolic set point", sort_order=3),
    Emotion(emotion="Metabolic", exact_phrase="decreased resting metabolic rate", sort_order=4),
    Emotion(emotion="Devastation", exact_phrase="Devastation after progress", sort_order=5),
    Emotion(emotion="Frustration", exact_phrase="frustration at body betrayal", sort_order=6),
    Emotion(emotion="Despair", exact_phrase="despair about forever stuck", sort_order=7),
],
    failed_solutions=[
    FailedSolution(solution_tried="Solution", why_it_failed="Why Failed", sort_order=1),
    FailedSolution(solution_tried="Cutting more calories", why_it_failed="Slows metabolism more", sort_order=2),
    FailedSolution(solution_tried="Adding more cardio", why_it_failed="Exhausting", sort_order=3),
    FailedSolution(solution_tried="Starving", why_it_failed="Worsens metabolism", sort_order=4),
    FailedSolution(solution_tried="Random changes", why_it_failed="No biological understanding", sort_order=5),
],
    root_causes=[
    RootCause(category="Biological", root_cause="Metabolic adaptation", sort_order=1),
    RootCause(category="Biological", root_cause="Decreased resting metabolic rate", sort_order=2),
    RootCause(category="Biological", root_cause="Hormonal changes", sort_order=3),
],
)
