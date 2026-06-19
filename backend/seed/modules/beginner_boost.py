"""BEGINNER BOOST (Beginner Fitness) — original module from fitness_database.docx.

Acts as the default foundational fallback when no other module is selected.

CONTENT PENDING: see seed/modules/pcos.py for the stub policy.
"""
from models.module import Module


MODULE = Module(
    slug="beginner_boost",
    display_name="Beginner Boost",
    is_authored_extension=False,
    content_pending=True,
)
