"""Checker verdict types.

Kept small and stable — the GitHub Action serialises the JSON shape
directly into the sticky PR comment, so the structure is part of the
harness's public surface even though the dataclasses are internal.

Two levels:

- :class:`RecordVerdict` — one Work Record's verdict. Carries the
  slug, the per-record status / exit_code, and the ordered list of
  :class:`PredicateResult` for that record. Per-record status uses the
  same rule the single-record verdict used before slice 0: any blocking
  failed → ``blocking``; else any advisory failed → ``advisory``;
  else ``clean``.

- :class:`Verdict` — the overall verdict for a PR. Carries the rolled-
  up status / exit_code across all records, plus the per-record list
  in order. Overall aggregation uses the same rule across records.

A single-record run wraps its one record in ``records[0]``; multi-record
runs nest each.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class PredicateResult:
    """Result of one predicate evaluation.

    Names are dotted (``workrecord.exists``) so they're greppable in
    logs and stable across releases — tests pin them as goldens. The
    detail is a short human sentence; we deliberately don't try to be
    structured here because the predicate name is the structured part.
    """

    name: str
    passed: bool
    detail: str
    blocking: bool


@dataclass(frozen=True)
class RecordVerdict:
    """Verdict for one Work Record.

    Status and exit_code are derived from the predicate list using the
    same rule as the overall verdict — see :func:`_status_of`.

    ``effective_rules`` lists every predicate that fired on this
    record, paired with a source label (``core`` / ``default`` / ``repo``)
    naming where the rule originated. Reviewers consume this via the
    comment formatter to answer "which rules applied, and where did
    each come from?" — SPEC §13.1's last clause.
    """

    slug: str
    status: str
    exit_code: int
    predicates: list[PredicateResult] = field(default_factory=list)
    effective_rules: list[dict[str, str]] = field(default_factory=list)


@dataclass(frozen=True)
class Verdict:
    """Aggregate verdict for a PR's checked Work Records.

    Even a single-record run wraps its record in ``records[0]`` — the
    shape is uniform so the comment formatter doesn't need a separate
    code path for the single-record case (it picks the rendering shape
    from ``len(records)``).
    """

    status: str
    """One of ``clean``, ``advisory``, ``blocking``."""

    exit_code: int
    """``0`` clean, ``1`` advisory, ``2`` blocking. Mirrors ``status``."""

    records: list[RecordVerdict] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """JSON-serialisable view. Predicates flatten to dicts at the leaf."""
        return {
            "status": self.status,
            "exit_code": self.exit_code,
            "records": [
                {
                    "slug": r.slug,
                    "status": r.status,
                    "exit_code": r.exit_code,
                    "predicates": [asdict(p) for p in r.predicates],
                    "effective_rules": list(r.effective_rules),
                }
                for r in self.records
            ],
        }


def _status_of(predicates: list[PredicateResult]) -> tuple[str, int]:
    """Roll up a flat predicate list into (status, exit_code).

    Shared by both record-level and overall aggregation, so the same
    rule applies on both levels: any failed blocking → blocking;
    else any failed advisory → advisory; else clean.
    """
    any_blocking_failed = any(not p.passed and p.blocking for p in predicates)
    any_advisory_failed = any(not p.passed and not p.blocking for p in predicates)
    if any_blocking_failed:
        return "blocking", 2
    if any_advisory_failed:
        return "advisory", 1
    return "clean", 0


def aggregate_record(slug: str, predicates: list[PredicateResult]) -> RecordVerdict:
    """Build a :class:`RecordVerdict` from one record's predicate results."""
    status, exit_code = _status_of(predicates)
    return RecordVerdict(slug=slug, status=status, exit_code=exit_code, predicates=predicates)


def aggregate(records: list[RecordVerdict]) -> Verdict:
    """Roll up per-record verdicts into the overall :class:`Verdict`.

    The overall status applies the same rule one level up: any record
    with status ``blocking`` → overall blocking; else any record with
    status ``advisory`` → overall advisory; else overall clean.

    When ``records`` is empty (e.g. a PR that changed no Work Records),
    the overall verdict is clean — the "nothing to check" case is not
    itself a failure. The caller may surface it via a comment, but it
    is not a workflow gate.
    """
    if not records:
        return Verdict(status="clean", exit_code=0, records=[])

    if any(r.status == "blocking" for r in records):
        return Verdict(status="blocking", exit_code=2, records=records)
    if any(r.status == "advisory" for r in records):
        return Verdict(status="advisory", exit_code=1, records=records)
    return Verdict(status="clean", exit_code=0, records=records)
