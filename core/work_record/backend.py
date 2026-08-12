"""Work Record backend interface.

The skill and the CI checker both read and write Work Records through
this interface. Two implementations land in the slice's lifetime:

- :class:`~core.work_record.local_backend.LocalBackend` — Markdown file
  in the repo (slice walking-skeleton).
- ``JiraBackend`` — marker-bounded comment on a Jira ticket (W18).

Keeping the surface narrow on purpose: ``read``, ``write``, and
``resolve_location`` are all callers need. Bootstrap and the slug
strategy live in higher layers.

Backends return and accept :class:`~core.work_record.parser.ParsedRecord`
(both routine and expanded shapes). The dispatcher inside :func:`parse_record`
picks the shape from the record's own ``(Risk, Complexity)``; backends
don't need to know which is which — they read and write whichever the
file declares.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .parser import ParsedRecord


@runtime_checkable
class WorkRecordBackend(Protocol):
    """Read and write a single Work Record identified by a slug.

    The slug is a short human-readable identifier derived from the
    branch or PR (Jira ID, branch-name suffix, etc.) — the exact
    derivation is the skill driver's job, not the backend's.
    """

    def read(self, slug: str) -> ParsedRecord | None:
        """Return the Work Record for ``slug`` or ``None`` if it does not exist.

        The returned :class:`ParsedRecord` carries both the shape
        (``"routine"`` or ``"expanded"``) and the typed record. Callers
        branch on ``parsed.shape`` when they care.

        Raises :exc:`~core.work_record.parser.WorkRecordParseError` when
        a Work Record exists but is malformed — callers should treat a
        parse error as "found but unreadable," not as "missing."
        """
        ...

    def write(self, slug: str, parsed: ParsedRecord) -> None:
        """Write ``parsed`` for ``slug``.

        Creates the Work Record on first write; updates it idempotently
        on subsequent writes (the marker block is replaced; anything
        outside it is preserved).

        The backend renders the record per its shape — routine-shape
        records get the routine field set; expanded-shape records get
        the §9.4 field set. See :func:`render_record`.
        """
        ...

    def resolve_location(self, slug: str) -> str:
        """Return a human-readable identifier for the Work Record location.

        Surface this in error messages, the CI verdict, and the recovery
        state. Format is backend-specific (a relative path for local; a
        Jira issue URL for jira).
        """
        ...
