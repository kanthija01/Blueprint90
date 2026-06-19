"""DORM FIT (College Dorm Fitness) — original module from fitness_database.docx.

Also serves as the fallback module for `student_general` lifestyle.

CONTENT PENDING: see seed/modules/pcos.py for the stub policy.
"""
from models.module import Module


MODULE = Module(
    slug="dorm_fit",
    display_name="Dorm Fit",
    is_authored_extension=False,
    content_pending=True,
)
