"""Rules-engine errors. Kept tiny on purpose — the engine should fail loudly,
not gracefully, when its assumptions break.
"""


class ModuleMappingError(ValueError):
    """Raised when one or more problem slugs from an assessment have no entry
    in PROBLEM_MODULE_MAP.

    This is the single mechanism that keeps the system honest: if a new
    Problem checkbox is added to the form without a corresponding module +
    map entry, every assessment using that slug will fail here rather than
    silently produce a blueprint with a missing section.
    """

    def __init__(self, unknown_slugs: list[str]):
        self.unknown_slugs = unknown_slugs
        super().__init__(
            f"No module mapped for problem slug(s): {', '.join(unknown_slugs)}"
        )
