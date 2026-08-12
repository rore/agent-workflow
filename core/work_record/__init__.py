"""Work Record parser package.

Reads marker-bounded Work Records out of Markdown files. The marker
delimiters and field shape come from the routine template at
``core/templates/work-record-routine.md`` and the expanded template at
``core/templates/work-record-expanded.md``.

Public API:

- :class:`WorkRecord` — TypedDict of routine (compact) fields.
- :class:`ExpandedWorkRecord` — TypedDict of expanded fields (SPEC §9.4).
- :class:`ParsedRecord` — dispatcher result; carries ``shape`` and ``record``.
- :func:`parse_record` — parse + dispatch on ``(Risk, Complexity)`` to
  the right shape; the recommended entry point.
- :func:`parse` — legacy routine-only entry point; raises on expanded
  input. Retained for callers that pre-date the expanded shape.
- :func:`render` — render a routine :class:`WorkRecord` to a canonical
  marker block.
- :func:`render_expanded` — render an :class:`ExpandedWorkRecord`.
- :func:`render_record` — dispatch on ``parsed.shape`` and call the
  right renderer; the recommended write-side entry point.
- :func:`find_block_span` — locate the marker block in arbitrary text
  for in-place updates.
- :exc:`WorkRecordParseError` — raised on any malformed input.

Backends live alongside this module: see :mod:`backend` for the
protocol and :mod:`local_backend` for the local Markdown implementation.
"""

from .backend import WorkRecordBackend
from .local_backend import LocalBackend
from .parser import (
    ALLOWED_COMPLEXITY,
    ALLOWED_RISK,
    ExceptionEntry,
    ExpandedWorkRecord,
    ParsedRecord,
    Shape,
    WorkRecord,
    WorkRecordParseError,
    find_block_span,
    parse,
    parse_exceptions,
    parse_record,
    render,
    render_expanded,
    render_record,
)

__all__ = [
    "ALLOWED_COMPLEXITY",
    "ALLOWED_RISK",
    "ExceptionEntry",
    "ExpandedWorkRecord",
    "LocalBackend",
    "ParsedRecord",
    "Shape",
    "WorkRecord",
    "WorkRecordBackend",
    "WorkRecordParseError",
    "find_block_span",
    "parse",
    "parse_exceptions",
    "parse_record",
    "render",
    "render_expanded",
    "render_record",
]
