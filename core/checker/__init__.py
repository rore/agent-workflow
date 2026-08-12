"""agent-workflow CI checker.

Reads the Work Record(s) via the configured backend and applies a set
of named predicates. Each predicate is one objective question — does
the Work Record exist, are the markers present, are the required fields
populated, is the state value allowed. The aggregate verdict drives an
exit code that GitHub Actions translates into a CI pass / fail.

Slice 0 made the checker multi-record aware: a PR may change more than
one Work Record under ``.agent-workflow/tasks/`` and the checker runs
the predicate set against each. Single-record runs (local CLI, tests)
go through the same path, wrapping their one record in the standard
verdict shape.

The harness does not decide whether the work is correct; it enforces
objective workflow gates and surfaces judgment-heavy risks for review
(see ``docs/SPEC.md`` §5 Judgment Boundary). Predicates here are
deliberately structural — prose quality, plan soundness, evidence
adequacy are not the checker's job.

Public API:

- :class:`Verdict`, :class:`RecordVerdict`, :class:`PredicateResult` —
  verdict data shapes.
- :func:`run_checker` — single-slug programmatic entry point (returns a
  :class:`Verdict` with one record).
- :func:`run_checker_multi` — multi-slug programmatic entry point.
- :func:`discover_slugs_from_changed_files` — turn a ``git diff
  --name-only`` output file into a list of Work Record slugs.
- :func:`main` — CLI entry point (used by ``python -m core.checker``).

Exit codes:

- ``0`` clean — every predicate on every record passed.
- ``1`` advisory — at least one non-blocking predicate failed (no
  blocking failures).
- ``2`` blocking — at least one blocking predicate failed.
"""

from .checker import (
    discover_slugs_from_changed_files,
    main,
    run_checker,
    run_checker_multi,
)
from .predicates import PREDICATE_SOURCE
from .verdict import PredicateResult, RecordVerdict, Verdict

__all__ = [
    "PREDICATE_SOURCE",
    "PredicateResult",
    "RecordVerdict",
    "Verdict",
    "discover_slugs_from_changed_files",
    "main",
    "run_checker",
    "run_checker_multi",
]
