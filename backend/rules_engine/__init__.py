"""Blueprint90 rules engine.

The heart of "no hallucinations": this package decides — deterministically —
which modules apply to an assessment and which workout routine to pick within
the selected module. Zero LLM calls. Zero database I/O. Zero fuzzy matching.

Public surface:
    from rules_engine.select_modules import select_modules, detect_gym_anxiety_signal
    from rules_engine.validate import validate_module_slugs
    from rules_engine.resolve_constraints import resolve_workout_routine, find_matching_constraints
    from rules_engine.types import Assessment, ModuleSelection
    from rules_engine.errors import ModuleMappingError
"""
