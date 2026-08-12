"""Checker predicates.

Each predicate is a small function with the same shape: take a context
object, evaluate one objective question about the Work Record, return
a :class:`~core.checker.verdict.PredicateResult`. The checker walks them
in order and aggregates the results.

The current predicate set covers W13's routine concerns, the
shape-aware additions from slice A, and slice B's redline gates:

- ``workrecord.exists`` — backend resolves a Work Record for the slug.
- ``workrecord.markers_present`` — marker delimiters bound a single block.
- ``risk.declared`` — Risk field is present with a valid value.
- ``complexity.declared`` — Complexity field is present with a valid value.
- ``workrecord.shape_matches_classification`` — record shape matches
  what ``(Risk, Complexity)`` mandates (compact only at ``(Routine,
  Simple)``; everything else expanded).
- ``workrecord.routine_fields_present`` — for routine records, every
  required routine field is present and non-empty.
- ``workrecord.expanded_fields_present`` — for expanded records, every
  required expanded field is present and non-empty.
- ``workrecord.state_valid`` — state is one of the allowed values.
- ``risk.redline_findings_available`` — redline's verdict artifact is
  present and parsed (blocks under ``redline: required``, advisory
  under ``redline: optional``).
- ``risk.boundary_violation_absent`` — redline did not flag any
  architectural-boundary violation on the diff.
- ``risk.declared_not_below_detected`` — the Work Record's declared
  Risk meets the minimum redline detected on the diff.

The shape-specific fields predicates are mutually exclusive — only one
fires per verdict, named after the record's actual shape. The redline
predicates always fire (skipped results pass with a "skipped" detail
when there's no usable input) so the verdict's predicate list shape
stays stable across runs.

W14–W16 land additional predicates in later steps; the aggregation
contract (:func:`~core.checker.verdict.aggregate`) accepts any ordered
list, so adding new ones doesn't change the shape here.
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from core.work_record import (
    ALLOWED_COMPLEXITY,
    ALLOWED_RISK,
    ExceptionEntry,
    ExpandedWorkRecord,
    Shape,
    WorkRecord,
    WorkRecordBackend,
    WorkRecordParseError,
    find_block_span,
    parse_exceptions,
)

from .redline_verdict import RedlineVerdict, risk_at_least
from .verdict import PredicateResult

# Allowed Work Record state values. Both shapes share the same allowed
# states; routine fast-path lists three (SPEC §7), expanded uses the
# same set plus may add others later. We accept the "Blocked or
# returned to planning" long form for the second.
_ALLOWED_STATES: tuple[str, ...] = (
    "Ready to implement",
    "Blocked",
    "Blocked or returned to planning",
    "Ready for review",
)


@dataclass(frozen=True)
class CheckerContext:
    """Inputs shared across predicates.

    A predicate may consume any subset of these. The checker constructs
    a context once per run and passes it through. Predicates do not
    mutate state across each other — each is pure given the context.
    """

    backend: WorkRecordBackend
    slug: str

    # The Work Record parsed from disk, either shape. None when reading
    # failed (missing file, parse error). Predicates downstream of
    # ``workrecord.exists`` short-circuit when this is None — they
    # would all fail the same way otherwise, which would bury the real
    # cause under noise.
    record: WorkRecord | ExpandedWorkRecord | None
    """Parsed Work Record if present and well-formed; otherwise None."""

    shape: Shape | None
    """Shape selected by the parser from the record's own (Risk, Complexity)
    declaration. None when the record could not be parsed."""

    parse_error: WorkRecordParseError | None
    """Set when the file existed but failed to parse. Drives markers /
    fields predicates."""

    raw_text: str | None
    """Raw file content when the file existed (parsed or not). None
    when the file does not exist. Used by predicates that need to look
    at the unparsed bytes."""

    redline_verdict: RedlineVerdict | None
    """Parsed redline verdict when the file at the configured
    ``redlineVerdictPath`` exists and parsed. ``None`` when the file
    does not exist (the ``risk.redline_findings_available`` predicate
    decides whether that is a block under ``redline: required`` or
    advisory under ``redline: optional``) or when parsing failed (in
    which case ``redline_verdict_parse_error`` is set)."""

    redline_required: bool
    """Mirrors ``cfg.redline.required``. ``True`` when the per-repo
    config declares ``redline: required`` (the default) — a missing
    verdict is then a CI configuration error. ``False`` (``redline:
    optional``) turns a missing verdict into an advisory finding."""

    redline_verdict_parse_error: str | None
    """Set when the verdict file existed but did not parse. Surfaces
    as a blocking failure on ``risk.redline_findings_available``; the
    boundary + declared-vs-detected predicates short-circuit on it
    rather than re-stating the same root cause."""

    exceptions: tuple[ExceptionEntry, ...] = ()
    """Parsed exceptions from the Work Record's optional Exceptions
    field. Empty tuple when the field is absent or contains only ``—``.
    The exceptions.* predicates and the downgrade pass consume this."""

    exceptions_parse_error: str | None = None
    """Set when the Exceptions field existed but failed structural
    parsing. Surfaces as a blocking failure on
    ``exceptions.well_formed``. Predicates downstream short-circuit on
    it so the root cause isn't re-stated."""

    repo_root: Path | None = None
    """Repository root path. Set by the checker so predicates that
    need filesystem context (e.g. the ``workrecord.commit_order``
    advisory that walks ``git log``) can resolve it. ``None`` for
    predicates that don't need a repo root and for legacy direct
    library callers; predicates that need it skip gracefully when
    absent."""

    base_ref: str | None = None
    """Git ref or SHA marking the branch's base for commit-history
    walks. Set by the checker from ``--base-ref`` or the ``BASE_SHA``
    env var. ``None`` falls back to ``origin/main`` inside the
    predicate. CI workflows on a GitHub Actions ``pull/N/merge`` ref
    must pass the PR's actual base SHA so the synthetic merge commit
    doesn't collapse the branch's history to one."""

    head_ref: str | None = None
    """Git ref or SHA marking the branch tip for commit-history
    walks. Set by the checker from ``--head-ref`` or the ``HEAD_SHA``
    env var. ``None`` falls back to ``HEAD`` inside the predicate.
    On GitHub Actions' ``pull/N/merge`` checkout, ``HEAD`` is the
    synthetic merge commit; passing the PR's actual head SHA lets
    the predicate see the real branch."""


# ---------------------------------------------------------------------------
# Individual predicates
# ---------------------------------------------------------------------------


def workrecord_exists(ctx: CheckerContext) -> PredicateResult:
    """Predicate: a Work Record file resolves for the configured slug."""
    if ctx.raw_text is not None:
        return PredicateResult(
            name="workrecord.exists",
            passed=True,
            detail=f"Work Record located at {ctx.backend.resolve_location(ctx.slug)!r}.",
            blocking=True,
        )
    return PredicateResult(
        name="workrecord.exists",
        passed=False,
        detail=(
            f"no Work Record found for slug {ctx.slug!r} "
            f"(expected at {ctx.backend.resolve_location(ctx.slug)!r})"
        ),
        blocking=True,
    )


def workrecord_markers_present(ctx: CheckerContext) -> PredicateResult:
    """Predicate: a single marker-bounded block exists in the Work Record file.

    Checks marker structure only. A missing or mistyped field is the
    business of the fields / shape predicates downstream; the markers
    predicate fails only when the marker delimiters themselves are
    absent, unterminated, multiple, or out of order. This keeps the
    named-predicate contract honest: ``markers_present`` means markers,
    not "the parser was happy."

    Short-circuits cleanly when the file is missing — the
    ``workrecord.exists`` failure already covers that case and we don't
    want to surface a confusing second blocker for the same root cause.
    """
    if ctx.raw_text is None:
        return PredicateResult(
            name="workrecord.markers_present",
            passed=False,
            detail="skipped — Work Record file does not exist.",
            blocking=True,
        )
    try:
        span = find_block_span(ctx.raw_text)
    except WorkRecordParseError as exc:
        return PredicateResult(
            name="workrecord.markers_present",
            passed=False,
            detail=f"marker block malformed: {exc}",
            blocking=True,
        )
    if span is None:
        return PredicateResult(
            name="workrecord.markers_present",
            passed=False,
            detail="no marker block found in file.",
            blocking=True,
        )
    return PredicateResult(
        name="workrecord.markers_present",
        passed=True,
        detail="marker pair found, single block.",
        blocking=True,
    )


def risk_declared(ctx: CheckerContext) -> PredicateResult:
    """Predicate: the Risk field is present with a valid value.

    Valid values are Routine, Elevated, High (per ``ALLOWED_RISK``).
    Boundary Violation is not a valid Work Record value — the workflow
    stops at §9.3 before a record is written.
    """
    if ctx.record is None:
        return PredicateResult(
            name="risk.declared",
            passed=False,
            detail="skipped — Work Record could not be parsed.",
            blocking=True,
        )
    risk = ctx.record["risk"].strip()
    if risk in ALLOWED_RISK:
        return PredicateResult(
            name="risk.declared",
            passed=True,
            detail=f"Risk = {risk!r}.",
            blocking=True,
        )
    return PredicateResult(
        name="risk.declared",
        passed=False,
        detail=(
            f"Risk value {risk!r} is not allowed; expected one of "
            + ", ".join(repr(r) for r in sorted(ALLOWED_RISK))
        ),
        blocking=True,
    )


def complexity_declared(ctx: CheckerContext) -> PredicateResult:
    """Predicate: the Complexity field is present with a valid value.

    Valid values are Simple, Moderate, Large (per ``ALLOWED_COMPLEXITY``).
    """
    if ctx.record is None:
        return PredicateResult(
            name="complexity.declared",
            passed=False,
            detail="skipped — Work Record could not be parsed.",
            blocking=True,
        )
    complexity = ctx.record["complexity"].strip()
    if complexity in ALLOWED_COMPLEXITY:
        return PredicateResult(
            name="complexity.declared",
            passed=True,
            detail=f"Complexity = {complexity!r}.",
            blocking=True,
        )
    return PredicateResult(
        name="complexity.declared",
        passed=False,
        detail=(
            f"Complexity value {complexity!r} is not allowed; expected one of "
            + ", ".join(repr(c) for c in sorted(ALLOWED_COMPLEXITY))
        ),
        blocking=True,
    )


def shape_matches_classification(ctx: CheckerContext) -> PredicateResult:
    """Predicate: record shape matches what (Risk, Complexity) mandates.

    Compact records are allowed only at ``(Routine, Simple)``; everything
    else demands the expanded shape. The parser already enforces this
    rule by routing to the right validator, so a parsed-cleanly record
    necessarily satisfies this predicate — but firing the explicit
    verdict line makes the audit trail in the PR comment legible.

    When the parser rejected the record (mismatch surfaces as a
    ``WorkRecordParseError``), this predicate fails with the parse
    error as the detail so a reviewer sees the mismatch named here
    rather than buried in the markers / fields predicates.
    """
    if ctx.record is None:
        if ctx.parse_error is not None:
            return PredicateResult(
                name="workrecord.shape_matches_classification",
                passed=False,
                detail=f"shape mismatch: {ctx.parse_error}",
                blocking=True,
            )
        return PredicateResult(
            name="workrecord.shape_matches_classification",
            passed=False,
            detail="skipped — Work Record could not be parsed.",
            blocking=True,
        )
    assert ctx.shape is not None  # parser sets both or neither
    return PredicateResult(
        name="workrecord.shape_matches_classification",
        passed=True,
        detail=f"{ctx.shape} shape matches the declared classification.",
        blocking=True,
    )


def workrecord_fields_present(ctx: CheckerContext) -> PredicateResult:
    """Predicate: every required field for the record's shape is present.

    The parser's ``parse_record`` raises on missing-field, unknown-
    field, or empty-value cases against the shape selected by the
    record's own ``(Risk, Complexity)`` declaration. A successful parse
    already implies the field set is complete for the chosen shape;
    this predicate exists to surface the *named* success or failure in
    the verdict — callers reading the verdict JSON shouldn't have to
    derive presence-of-fields from absence-of-parse-error.

    The predicate's name reflects the actual shape: routine records
    fire ``workrecord.routine_fields_present``; expanded records fire
    ``workrecord.expanded_fields_present``. Only one fires per verdict.
    """
    # When parsing failed we don't know which shape was intended; emit
    # the routine name as the default so the verdict's predicate order
    # stays stable for visual comparison.
    if ctx.record is None or ctx.shape is None:
        return PredicateResult(
            name="workrecord.routine_fields_present",
            passed=False,
            detail="skipped — Work Record could not be parsed.",
            blocking=True,
        )
    name = (
        "workrecord.routine_fields_present"
        if ctx.shape == "routine"
        else "workrecord.expanded_fields_present"
    )
    detail = f"all required {ctx.shape}-path fields present and non-empty."
    return PredicateResult(
        name=name,
        passed=True,
        detail=detail,
        blocking=True,
    )


def workrecord_state_valid(ctx: CheckerContext) -> PredicateResult:
    """Predicate: the State field value is one of the allowed states.

    Both shapes share the State field and the same allowed values.
    """
    if ctx.record is None:
        return PredicateResult(
            name="workrecord.state_valid",
            passed=False,
            detail="skipped — Work Record could not be parsed.",
            blocking=True,
        )
    state = ctx.record["state"].rstrip(".").strip()
    if state in _ALLOWED_STATES:
        return PredicateResult(
            name="workrecord.state_valid",
            passed=True,
            detail=f"state {state!r} is valid.",
            blocking=True,
        )
    return PredicateResult(
        name="workrecord.state_valid",
        passed=False,
        detail=(
            f"state {state!r} is not one of "
            + ", ".join(repr(s) for s in _ALLOWED_STATES)
        ),
        blocking=True,
    )


# ---------------------------------------------------------------------------
# Redline predicates (slice B)
# ---------------------------------------------------------------------------
#
# Three separate predicates rather than one combined. Reviewer #6
# argued the case: a PR comment that names exactly which failure mode
# fired ("boundary violation" vs "declared risk too low") reads more
# cleanly than a single ``risk.redline_match`` that has to enumerate
# its reasons in the detail string. The three split cleanly along the
# axes redline emits: "is the verdict here", "are there boundary
# violations", "does declared risk meet detected risk".


def risk_redline_findings_available(ctx: CheckerContext) -> PredicateResult:
    """Predicate: redline's verdict artifact is present and parsed.

    The behaviour depends on ``ctx.redline_required``:

    - Verdict parsed → pass (``blocking=True`` — a successful parse is
      a confirmation, not a warning).
    - Verdict file missing and ``redline: required`` → fail blocking
      (``CI configuration error: no verdict at <path>``).
    - Verdict file missing and ``redline: optional`` → fail advisory
      (``blocking=False`` — the verdict is encouraged, not mandatory).
    - Verdict file present but failed to parse → fail blocking
      regardless of ``required`` (silent corruption would be worse
      than declaring it).
    """
    if ctx.redline_verdict_parse_error is not None:
        return PredicateResult(
            name="risk.redline_findings_available",
            passed=False,
            detail=(
                f"redline verdict failed to parse: "
                f"{ctx.redline_verdict_parse_error}"
            ),
            blocking=True,
        )
    if ctx.redline_verdict is not None:
        return PredicateResult(
            name="risk.redline_findings_available",
            passed=True,
            detail="redline verdict parsed.",
            blocking=True,
        )
    # Verdict missing — required or optional drives blocking.
    if ctx.redline_required:
        return PredicateResult(
            name="risk.redline_findings_available",
            passed=False,
            detail=(
                "redline verdict missing — CI configuration error "
                "(redline: required)."
            ),
            blocking=True,
        )
    return PredicateResult(
        name="risk.redline_findings_available",
        passed=False,
        detail=(
            "redline verdict missing (advisory — redline: optional)."
        ),
        blocking=False,
    )


def risk_boundary_violation_absent(ctx: CheckerContext) -> PredicateResult:
    """Predicate: redline's verdict does not flag any boundary violations.

    Skipped (passed, with a "skipped" detail) when redline's verdict
    is unavailable — the previous predicate already names that root
    cause and re-stating it here would be noise. A skipped result
    stays ``blocking=True`` because the gate exists conceptually; it
    just has no input to evaluate.

    When the verdict is available, any non-empty
    ``boundaryViolations`` list fails the predicate. Boundary
    violations are a separate concern from risk-level mismatch — a
    boundary violation blocks regardless of how the Work Record
    declared its Risk.
    """
    if ctx.redline_verdict is None:
        return PredicateResult(
            name="risk.boundary_violation_absent",
            passed=True,
            detail="skipped — redline verdict unavailable.",
            blocking=True,
        )
    if ctx.redline_verdict.has_boundary_violation:
        # One-line summary of the first violation; the full list is on
        # ``ctx.redline_verdict.boundary_violations`` for callers that
        # want detail. Surfacing only the first keeps PR comments
        # readable; reviewers see the rest in the redline artifact.
        first = ctx.redline_verdict.boundary_violations[0]
        rule = first.get("rule", "<unknown rule>")
        return PredicateResult(
            name="risk.boundary_violation_absent",
            passed=False,
            detail=(
                f"boundary violation: {rule} "
                f"(plus {len(ctx.redline_verdict.boundary_violations) - 1} more)"
                if len(ctx.redline_verdict.boundary_violations) > 1
                else f"boundary violation: {rule}"
            ),
            blocking=True,
        )
    return PredicateResult(
        name="risk.boundary_violation_absent",
        passed=True,
        detail="no boundary violations.",
        blocking=True,
    )


def risk_declared_not_below_detected(ctx: CheckerContext) -> PredicateResult:
    """Predicate: declared Risk meets the minimum redline detected.

    Skipped (passed, with a "skipped" detail) when:

    - the verdict is unavailable (``risk.redline_findings_available``
      already named the root cause), or
    - the Work Record could not be parsed (``risk.declared`` named
      that root cause), or
    - redline flagged a boundary violation (the previous predicate is
      the named blocker; this predicate would otherwise still run and
      add noise — one named gate is enough).

    On a usable verdict, computes the minimum detected Risk via
    :meth:`RedlineVerdict.detected_risk` and compares to the declared
    Risk on the record using :func:`risk_at_least`. Fails blocking
    when declared is below detected.
    """
    if ctx.redline_verdict is None:
        return PredicateResult(
            name="risk.declared_not_below_detected",
            passed=True,
            detail="skipped — redline verdict unavailable.",
            blocking=True,
        )
    if ctx.record is None:
        return PredicateResult(
            name="risk.declared_not_below_detected",
            passed=True,
            detail="skipped — Work Record could not be parsed.",
            blocking=True,
        )
    if ctx.redline_verdict.has_boundary_violation:
        return PredicateResult(
            name="risk.declared_not_below_detected",
            passed=True,
            detail="skipped — boundary violation already blocks.",
            blocking=True,
        )
    declared = ctx.record["risk"].strip()
    detected = ctx.redline_verdict.detected_risk()
    if risk_at_least(declared, detected):
        return PredicateResult(
            name="risk.declared_not_below_detected",
            passed=True,
            detail=f"declared {declared!r} >= detected {detected!r}.",
            blocking=True,
        )
    return PredicateResult(
        name="risk.declared_not_below_detected",
        passed=False,
        detail=(
            f"declared {declared!r} is below detected {detected!r}; "
            f"raise the Work Record's Risk to at least {detected!r}."
        ),
        blocking=True,
    )


def review_checkpoints_satisfied(ctx: CheckerContext) -> PredicateResult:
    """Predicate: every triggered redline checkpoint is satisfied.

    Closes SPEC §9.7 result-review enforcement at the harness level. The
    harness does NOT re-implement redline's satisfaction logic — redline
    already evaluates each triggered checkpoint against PR labels and
    CODEOWNER approvals (see ``core/agent-redline/core/reporter/
    reporter.py:_is_satisfied``). This predicate reads redline's
    already-computed ``satisfied`` state and surfaces it through our
    verdict so a red-zone (or any checkpoint-triggering) change cannot
    merge with an unsatisfied review checkpoint.

    Skipped (passed, with a "skipped" detail) when the verdict is
    unavailable — the ``risk.redline_findings_available`` predicate
    already names that root cause. Skipped (passed) when redline
    reported no triggered checkpoints (a blue-only diff).

    On a usable verdict with checkpoints triggered: passes when every
    checkpoint's ``satisfied`` field is ``True``; otherwise blocks with
    the first unsatisfied checkpoint's id, reason, and the ``satisfy_by``
    options that would satisfy it.

    Non-waivable per SPEC §13.4: checkpoint satisfaction MUST remain
    distinct from human approval — a slice-F exception waiving this
    would collapse that distinction. Listed in
    :data:`_NON_WAIVABLE_PREDICATES`.
    """
    if ctx.redline_verdict is None:
        return PredicateResult(
            name="review.checkpoints_satisfied",
            passed=True,
            detail="skipped — redline verdict unavailable.",
            blocking=True,
        )
    checkpoints = ctx.redline_verdict.checkpoints
    if not checkpoints:
        return PredicateResult(
            name="review.checkpoints_satisfied",
            passed=True,
            detail="no review checkpoints triggered by the diff.",
            blocking=True,
        )
    # ``.get("satisfied", False)`` keeps the predicate fail-closed when
    # an older redline version emits a checkpoint without the field.
    unsatisfied = [cp for cp in checkpoints if not cp.get("satisfied", False)]
    if not unsatisfied:
        return PredicateResult(
            name="review.checkpoints_satisfied",
            passed=True,
            detail=f"all {len(checkpoints)} checkpoint(s) satisfied.",
            blocking=True,
        )
    first = unsatisfied[0]
    cp_id = first.get("id", "<unknown>")
    reason = first.get("reason", "")
    satisfy_by = first.get("satisfy_by") or []
    satisfy_str = ", ".join(satisfy_by) if satisfy_by else "(no satisfy-by recorded)"
    more = f" (+{len(unsatisfied) - 1} more)" if len(unsatisfied) > 1 else ""
    reason_part = f" — {reason}" if reason else ""
    # Disposition follows the redline policy's modes.report (or the
    # default mode when perCheck.report is unset). In shadow mode the
    # reporter has already chosen to surface the same finding as exit
    # code 1 (advisory) with recommendedAction `review-shadow-warnings`;
    # honour the same disposition here so the calibration window the
    # docs promise actually exists. Binding mode blocks as before.
    # Boundary-violation and structural-shape preconditions stay
    # blocking via their own predicates — they are not affected here.
    is_binding = ctx.redline_verdict.is_binding("report")
    mode_note = "" if is_binding else " [shadow — advisory]"
    return PredicateResult(
        name="review.checkpoints_satisfied",
        passed=False,
        detail=(
            f"unsatisfied checkpoint {cp_id!r}{reason_part}; "
            f"satisfy by: {satisfy_str}{more}{mode_note}"
        ),
        blocking=is_binding,
    )


# ---------------------------------------------------------------------------
# Exceptions predicates (slice F)
# ---------------------------------------------------------------------------
#
# Three predicates surface the well-formedness of any task-level
# exceptions recorded in the Work Record. Validation happens here, not
# in the parser — the parser only enforces structural presence of
# required sub-fields. The exceptions.* predicates validate content
# (rule names that are non-waivable, expiry dates in the past).


# Predicates that may never be downgraded by a task exception.
#
# SPEC §11 explicitly forbids waiving boundary-violation findings.
# Beyond that, the structural-shape preconditions are also non-
# waivable — they establish whether the Work Record itself is
# meaningful, and waiving them would leave the verdict noise.
_NON_WAIVABLE_PREDICATES: frozenset[str] = frozenset({
    # SPEC §11 — boundary violations never waivable.
    "risk.boundary_violation_absent",
    # Preconditions — without these, the rest of the verdict is unreliable.
    "workrecord.exists",
    "workrecord.markers_present",
    "risk.declared",
    "complexity.declared",
    "workrecord.shape_matches_classification",
    # The exception predicates themselves — circular waivers are not
    # honoured. An exception waiving exceptions.well_formed would be
    # the harness telling itself to ignore its own content checks.
    "exceptions.well_formed",
    "exceptions.not_against_boundary",
    "exceptions.not_expired",
    # SPEC §13.4 structural invariant — clean-context review MUST NOT
    # satisfy a human-approval requirement. Waiving this would mean
    # declaring "the clean-context review IS the human approval" —
    # contradicting the workflow model.
    "approval.clean_context_does_not_satisfy_human",
    # SPEC §13.4 — checkpoint satisfaction MUST remain distinct from
    # human approval. Waiving this would collapse the distinction the
    # spec explicitly requires.
    "review.checkpoints_satisfied",
    # SPEC §13.5 — evidence.failure_not_claimed_as_success would have
    # been here, but the slice-E stop-condition downgraded it to
    # advisory because the regex misfires on Work Records that
    # describe contradictory prose as planning content (e.g. demo
    # fixture references). A follow-up will refine detection (skip
    # fenced code blocks / quoted spans) and re-promote to blocking
    # non-waivable.
})


def exceptions_well_formed(ctx: CheckerContext) -> PredicateResult:
    """Predicate: every exception entry parsed cleanly.

    The parser already raises on missing required sub-fields; this
    predicate surfaces the named pass/fail in the verdict and reports
    the parse failure when it happened. When no exceptions are
    recorded, the predicate passes with a "no exceptions" detail.
    """
    if ctx.exceptions_parse_error is not None:
        return PredicateResult(
            name="exceptions.well_formed",
            passed=False,
            detail=f"exceptions could not be parsed: {ctx.exceptions_parse_error}",
            blocking=True,
        )
    if not ctx.exceptions:
        return PredicateResult(
            name="exceptions.well_formed",
            passed=True,
            detail="no exceptions recorded.",
            blocking=True,
        )
    return PredicateResult(
        name="exceptions.well_formed",
        passed=True,
        detail=f"{len(ctx.exceptions)} exception(s) parsed cleanly.",
        blocking=True,
    )


def exceptions_not_against_boundary(ctx: CheckerContext) -> PredicateResult:
    """Predicate: no exception waives a non-waivable predicate.

    SPEC §11 forbids waiving boundary-violation findings. The harness
    extends this to the structural-shape preconditions; see
    :data:`_NON_WAIVABLE_PREDICATES`. An exception naming any of these
    is a blocking failure and the original predicate continues to fire
    normally (the downgrade pass refuses to honour the exception).
    """
    if ctx.exceptions_parse_error is not None or not ctx.exceptions:
        return PredicateResult(
            name="exceptions.not_against_boundary",
            passed=True,
            detail=(
                "skipped — no exceptions to validate."
                if not ctx.exceptions_parse_error
                else "skipped — exceptions parse error already named."
            ),
            blocking=True,
        )
    offending = [e for e in ctx.exceptions if e.rule in _NON_WAIVABLE_PREDICATES]
    if offending:
        names = ", ".join(repr(e.rule) for e in offending)
        return PredicateResult(
            name="exceptions.not_against_boundary",
            passed=False,
            detail=(
                f"exception(s) name non-waivable predicate(s): {names}. "
                "SPEC §11 forbids waiving boundary-violation findings; "
                "the harness extends the rule to the structural-shape "
                "preconditions that establish verdict meaningfulness."
            ),
            blocking=True,
        )
    return PredicateResult(
        name="exceptions.not_against_boundary",
        passed=True,
        detail="every exception names a waivable predicate.",
        blocking=True,
    )


def exceptions_not_expired(ctx: CheckerContext) -> PredicateResult:
    """Predicate: no exception has an expiry date in the past.

    Today is the calendar date the CI run starts. An expiry of today
    is still valid (the exception expires at the end of the day).
    Malformed dates (non-ISO) are surfaced as blocking — they prevent
    the predicate from making a determination.
    """
    if ctx.exceptions_parse_error is not None or not ctx.exceptions:
        return PredicateResult(
            name="exceptions.not_expired",
            passed=True,
            detail=(
                "skipped — no exceptions to validate."
                if not ctx.exceptions_parse_error
                else "skipped — exceptions parse error already named."
            ),
            blocking=True,
        )
    today = date.today()
    expired: list[tuple[str, str]] = []
    malformed: list[tuple[str, str]] = []
    for entry in ctx.exceptions:
        if entry.expiry is None:
            continue
        try:
            d = date.fromisoformat(entry.expiry)
        except ValueError:
            malformed.append((entry.rule, entry.expiry))
            continue
        if d < today:
            expired.append((entry.rule, entry.expiry))
    if malformed:
        names = ", ".join(f"{r!r} ({e!r})" for r, e in malformed)
        return PredicateResult(
            name="exceptions.not_expired",
            passed=False,
            detail=(
                f"exception(s) have malformed expiry date(s) (expected ISO "
                f"YYYY-MM-DD): {names}"
            ),
            blocking=True,
        )
    if expired:
        names = ", ".join(f"{r!r} (expired {e})" for r, e in expired)
        return PredicateResult(
            name="exceptions.not_expired",
            passed=False,
            detail=f"exception(s) have expired: {names}",
            blocking=True,
        )
    return PredicateResult(
        name="exceptions.not_expired",
        passed=True,
        detail="every exception is current.",
        blocking=True,
    )


# ---------------------------------------------------------------------------
# Approval predicates (slice D)
# ---------------------------------------------------------------------------
#
# Three predicates enforce SPEC §9.4 Plan Review at the level each Risk
# demands, and SPEC §13.4's clean-context-vs-human invariant.
#
# Per the 2026-06-18 traceability-not-identity decision: the harness
# validates artifact *shape*, never the identity of who recorded it.
# Per the 2026-06-23 "Slice D human approval" decision: the cheating
# window is acknowledged — an agent could fabricate "Approved by user
# ..." text in the Approvals field. Integrity rests on the human being
# in the loop and choosing to write the Work Record honestly.

# Values that signal "no clean-context review was performed" for the
# Elevated predicate. Case-insensitive comparison; whitespace stripped.
_NO_CLEAN_CONTEXT_VALUES: frozenset[str] = frozenset({
    "",
    "—",
    "—.",
    "self",
    "self-review",
    "self review",
})

# Sentinel for the High-risk approval line. Format:
#   Approved by user <timestamp>: "<verbatim quote>"
# Compiled case-insensitive; whitespace around the colon is tolerated.
_HIGH_APPROVAL_RE = re.compile(
    r"approved\s+by\s+user\s+[^:]+:",
    re.IGNORECASE,
)

# Regex to locate a "## Plan review" heading and the prose between
# it and the next heading. The prose must be at least 20 characters
# (stripped) to count as a real review record — a bare heading with
# no content does not satisfy the predicate.
_PLAN_REVIEW_SECTION_RE = re.compile(
    r"^##\s+Plan review\s*$(.*?)(?=^##\s+|\Z)",
    re.MULTILINE | re.DOTALL,
)


def _normalise_reference(text: str) -> str:
    """Normalise a reference string for clean-context-vs-human comparison.

    Strips surrounding whitespace and quotes, lowercases, and collapses
    internal whitespace runs to single spaces. Two references that
    point at the same thing modulo formatting normalise to the same
    string.
    """
    s = text.strip()
    # Strip matched surrounding quote characters.
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'"):
        s = s[1:-1]
    s = " ".join(s.lower().split())
    return s


def approval_elevated_clean_context_review_present(ctx: CheckerContext) -> PredicateResult:
    """Predicate: Elevated tasks record a clean-context plan review.

    When Risk == Elevated, the `plan_review` field must reference a
    real review — either a link/session reference in the field itself,
    or a `## Plan review` section in the Work Record file with non-
    trivial prose (≥ 20 chars stripped). A bare `self` or `—` in the
    field with no section fails the predicate.

    Per default profile §3, presence is enforced (tightened from the
    portable SPEC's SHOULD). The predicate is waivable via a slice-F
    task exception — consumers using a custom profile wanting SHOULD behaviour can
    record an exception per task.

    Fires with a "skipped" detail when Risk != Elevated, so the
    predicate-list shape stays stable across risk levels.
    """
    if ctx.record is None:
        return PredicateResult(
            name="approval.elevated_clean_context_review_present",
            passed=False,
            detail="skipped — Work Record could not be parsed.",
            blocking=True,
        )
    risk = ctx.record["risk"].strip()
    if risk != "Elevated":
        return PredicateResult(
            name="approval.elevated_clean_context_review_present",
            passed=True,
            detail=f"skipped — only applies at Risk=Elevated (record is Risk={risk!r}).",
            blocking=True,
        )
    # Field must exist on the expanded shape.
    plan_review = ctx.record.get("plan_review", "")  # type: ignore[union-attr]
    normalised_field = plan_review.strip().lower()
    if normalised_field and normalised_field not in _NO_CLEAN_CONTEXT_VALUES:
        return PredicateResult(
            name="approval.elevated_clean_context_review_present",
            passed=True,
            detail=f"Plan review references {plan_review.strip()!r}.",
            blocking=True,
        )
    # Field is empty / "—" / "self" / etc. — look for a ## Plan review
    # section in the surrounding prose. The marker block was excluded
    # from raw text? No — ctx.raw_text is the whole file. The Plan
    # review prose lives outside the marker block per the operating-
    # mode convention.
    if ctx.raw_text is not None:
        for match in _PLAN_REVIEW_SECTION_RE.finditer(ctx.raw_text):
            prose = match.group(1).strip()
            # Drop bullet-point or table boilerplate; require ≥ 20 chars
            # of real content.
            if len(prose) >= 20:
                return PredicateResult(
                    name="approval.elevated_clean_context_review_present",
                    passed=True,
                    detail=(
                        "Plan review field is short, but '## Plan review' "
                        "section carries the review prose."
                    ),
                    blocking=True,
                )
    return PredicateResult(
        name="approval.elevated_clean_context_review_present",
        passed=False,
        detail=(
            "Elevated task requires a clean-context plan review reference. "
            "The Plan review field is empty / '—' / 'self' and no '## Plan review' "
            "section with content was found. Either fill the field with a real "
            "reference, or add a '## Plan review' section below the marker "
            "block carrying the review prose."
        ),
        blocking=True,
    )


def approval_high_risk_approval_recorded(ctx: CheckerContext) -> PredicateResult:
    """Predicate: High tasks record a verbatim human approval.

    Looks for the sentinel ``Approved by user <timestamp>:`` in the
    Approvals field. Case-insensitive; whitespace around the colon is
    tolerated.

    Per the 2026-06-23 decision: the agent stops at plan-review for
    High tasks and refuses to advance until the human approves. The
    approval is recorded verbatim. The checker enforces *that*
    something approval-shaped is recorded — not who wrote it. Per the
    cheating-window acknowledgement, integrity rests on the human
    being in the loop.

    Fires with a "skipped" detail when Risk != High.
    """
    if ctx.record is None:
        return PredicateResult(
            name="approval.high_risk_approval_recorded",
            passed=False,
            detail="skipped — Work Record could not be parsed.",
            blocking=True,
        )
    risk = ctx.record["risk"].strip()
    if risk != "High":
        return PredicateResult(
            name="approval.high_risk_approval_recorded",
            passed=True,
            detail=f"skipped — only applies at Risk=High (record is Risk={risk!r}).",
            blocking=True,
        )
    approvals = ctx.record.get("approvals", "")  # type: ignore[union-attr]
    if _HIGH_APPROVAL_RE.search(approvals):
        return PredicateResult(
            name="approval.high_risk_approval_recorded",
            passed=True,
            detail="Approvals field carries an 'Approved by user <timestamp>:' line.",
            blocking=True,
        )
    return PredicateResult(
        name="approval.high_risk_approval_recorded",
        passed=False,
        detail=(
            "High task requires a recorded human approval in the Approvals "
            "field. Expected pattern (case-insensitive): "
            "'Approved by user <timestamp>: \"<verbatim quote>\"'. "
            "Got: " + (repr(approvals.strip()[:80]) if approvals.strip() else "empty")
        ),
        blocking=True,
    )


def approval_clean_context_does_not_satisfy_human(ctx: CheckerContext) -> PredicateResult:
    """Predicate: a clean-context review reference may not also be the human approval.

    SPEC §13.4: "A clean-context agent review MUST NOT satisfy a
    human-approval requirement." This is a structural invariant of the
    workflow model, not a policy choice — hence non-waivable (see
    :data:`_NON_WAIVABLE_PREDICATES`).

    Compares normalised forms of the Plan review and Approvals fields:
    strips whitespace and surrounding quotes, lowercases, collapses
    internal whitespace runs. Same reference with different formatting
    is correctly identified as the same.

    Fires with a "skipped" detail when Risk != High.
    """
    if ctx.record is None:
        return PredicateResult(
            name="approval.clean_context_does_not_satisfy_human",
            passed=False,
            detail="skipped — Work Record could not be parsed.",
            blocking=True,
        )
    risk = ctx.record["risk"].strip()
    if risk != "High":
        return PredicateResult(
            name="approval.clean_context_does_not_satisfy_human",
            passed=True,
            detail=f"skipped — only applies at Risk=High (record is Risk={risk!r}).",
            blocking=True,
        )
    plan_review = ctx.record.get("plan_review", "")  # type: ignore[union-attr]
    approvals = ctx.record.get("approvals", "")  # type: ignore[union-attr]
    p_norm = _normalise_reference(plan_review)
    a_norm = _normalise_reference(approvals)
    if not p_norm or not a_norm:
        # One of the fields is empty/—; the high_risk_approval_recorded
        # predicate handles that case. This invariant fires only when
        # both have content — there's nothing to confuse otherwise.
        return PredicateResult(
            name="approval.clean_context_does_not_satisfy_human",
            passed=True,
            detail="skipped — one of Plan review / Approvals is empty.",
            blocking=True,
        )
    if p_norm == a_norm:
        return PredicateResult(
            name="approval.clean_context_does_not_satisfy_human",
            passed=False,
            detail=(
                "Plan review and Approvals reference the same text. "
                "SPEC §13.4 invariant: a clean-context review MUST NOT "
                "satisfy a human-approval requirement. Record a distinct "
                "human approval in the Approvals field."
            ),
            blocking=True,
        )
    return PredicateResult(
        name="approval.clean_context_does_not_satisfy_human",
        passed=True,
        detail="Plan review and Approvals reference distinct items.",
        blocking=True,
    )


# ---------------------------------------------------------------------------
# Evidence predicates (slice E)
# ---------------------------------------------------------------------------
#
# Two predicates enforce SPEC §13.3 (Verification Record) at a
# structural level and SPEC §13.5's "no false success claims"
# invariant. The harness validates *presence/status/revision/freshness*
# of the recorded verification methods. It does NOT validate
# *adequacy* — whether the named check meaningfully proves the
# criterion — that stays a reviewer judgment per §5 Judgment Boundary.
#
# Per the night-plan framing: the Work Record names what verifies the
# work; the PR's surface (CI runs, comments) carries the actual
# evidence; the checker bridges them. This slice does the Work-Record
# half — naming + local invariant. The PR-status half (is the required
# CI green) is deferred to a follow-up because the checker runs as one
# of those CI jobs (chicken-and-egg).

# A criterion is mapped when its Verification plan line is one of:
# - <criterion> → <method>           (Unicode right-arrow)
# - <criterion> -> <method>          (ASCII)
# - <criterion> — <method>           (em-dash)
# - <method>: <criterion>            (colon, method-first)
# - manual: <description>            (explicit manual prefix)
_VERIFICATION_LINE_RES: tuple[re.Pattern, ...] = (
    re.compile(r"^.+?\s*→\s*.+$"),
    re.compile(r"^.+?\s*->\s*.+$"),
    re.compile(r"^.+?\s*—\s*.+$"),
    re.compile(r"^\s*manual\s*:\s*.+$", re.IGNORECASE),
    # method-first colon shape: requires a method-like prefix
    # (alphanumeric, dot-separated, no leading whitespace except indent)
    # followed by ': ' and then content.
    re.compile(r"^[A-Za-z][\w.]+\s*:\s*.+$"),
)


def _is_verification_line_mapped(line: str) -> bool:
    """True when `line` matches one of the accepted Verification-plan shapes."""
    stripped = line.strip().lstrip("-").strip()
    if not stripped:
        return False
    for pattern in _VERIFICATION_LINE_RES:
        if pattern.match(stripped):
            return True
    return False


def evidence_criteria_have_methods(ctx: CheckerContext) -> PredicateResult:
    """Predicate: every Verification plan line names a method or manual procedure.

    SPEC §13.3 demands each completion criterion map to a method (plus
    a result reference, revision, etc. — those live on the PR side and
    are out of scope for this slice). The predicate validates the
    structural mapping locally: scan the Verification plan field, count
    lines that aren't a recognised mapping shape.

    Always advisory — never blocks. The structural enforcement is a
    nudge toward better Work Records; reviewer judgment decides whether
    the recorded method actually covers the criterion. Routine records
    skip (their Verification field is short prose, not a per-criterion
    list).
    """
    if ctx.record is None:
        return PredicateResult(
            name="evidence.criteria_have_methods",
            passed=False,
            detail="skipped — Work Record could not be parsed.",
            blocking=False,
        )
    if ctx.shape != "expanded":
        return PredicateResult(
            name="evidence.criteria_have_methods",
            passed=True,
            detail="skipped — only applies to expanded records.",
            blocking=False,
        )
    plan = ctx.record.get("verification_plan", "")  # type: ignore[union-attr]
    lines = [ln for ln in plan.splitlines() if ln.strip()]
    if not lines:
        # Empty field — the expanded_fields_present predicate catches
        # this case already. Don't double-report.
        return PredicateResult(
            name="evidence.criteria_have_methods",
            passed=True,
            detail="skipped — Verification plan is empty (caught elsewhere).",
            blocking=False,
        )
    unmapped = [ln for ln in lines if not _is_verification_line_mapped(ln)]
    if not unmapped:
        return PredicateResult(
            name="evidence.criteria_have_methods",
            passed=True,
            detail=f"all {len(lines)} Verification plan line(s) map a criterion to a method.",
            blocking=False,
        )
    examples = "; ".join(repr(ln.strip()[:60]) for ln in unmapped[:3])
    more = f" (+{len(unmapped) - 3} more)" if len(unmapped) > 3 else ""
    return PredicateResult(
        name="evidence.criteria_have_methods",
        passed=False,
        detail=(
            f"{len(unmapped)}/{len(lines)} Verification plan line(s) lack a "
            f"recognised mapping. Accepted shapes: 'criterion → method', "
            f"'criterion -> method', 'criterion — method', "
            f"'method: criterion', 'manual: description'. "
            f"Examples: {examples}{more}"
        ),
        blocking=False,
    )


# Failure markers and success markers for the false-claim invariant.
# Used to detect explicit contradictions in the Work Record's prose.
_FAILURE_MARKERS = ("failed", "❌", "fail")
_SUCCESS_MARKERS = ("passed", "✅", "succeeded", "success", "green")

# CamelCase test/method identifier (e.g. WalletTest, ConcurrentRetryTest).
# Used to anchor a false-claim detection — both halves of a contradicting
# span must reference the same identifier, to avoid false positives on
# unrelated prose.
_TEST_ID_RE = re.compile(r"\b([A-Z][a-zA-Z0-9]*(?:Test|Spec|IT|Check)\b)")


def evidence_failure_not_claimed_as_success(ctx: CheckerContext) -> PredicateResult:
    """Predicate: the Work Record does not claim success for a failed check.

    SPEC §13.5: "harness MUST NOT convert unavailable evidence into a
    passing result." Local enforcement: scan the raw Work Record text
    for tightly-localised contradictions — a failure marker AND a
    success marker AND the same CamelCase test/method identifier
    appearing within a 300-char span.

    **Shipped as advisory** rather than blocking, per the slice-E
    stop condition. The regex misfires on Work Records that *describe*
    contradictory prose as part of their planning content (e.g. this
    slice's own Work Record names ``WalletTest: ❌ FAILED ... ✅ passed``
    as a planned demo fixture). Downgrading to advisory keeps the
    signal visible while avoiding a blocker on legitimate prose. A
    follow-up slice can refine detection (e.g. skip detection inside
    fenced code blocks or quoted spans) and re-promote to blocking.
    """
    text = ctx.raw_text
    if text is None:
        return PredicateResult(
            name="evidence.failure_not_claimed_as_success",
            passed=True,
            detail="skipped — Work Record file does not exist.",
            blocking=False,
        )

    lower = text.lower()
    window = 300
    for fmarker in _FAILURE_MARKERS:
        for fmatch in re.finditer(re.escape(fmarker), lower):
            start = max(0, fmatch.start() - window // 2)
            end = min(len(text), fmatch.end() + window // 2)
            span = text[start:end]
            span_lower = span.lower()
            if not any(sm in span_lower for sm in _SUCCESS_MARKERS):
                continue
            f_offset_end = span.lower().find(fmarker) + len(fmarker)
            f_text = span[:f_offset_end]
            s_text = span[f_offset_end:]
            f_ids = {m.group(1) for m in _TEST_ID_RE.finditer(f_text)}
            s_ids = {m.group(1) for m in _TEST_ID_RE.finditer(s_text)}
            shared = f_ids & s_ids
            if shared:
                hit = sorted(shared)[0]
                snippet = " ".join(span.split())[:200]
                return PredicateResult(
                    name="evidence.failure_not_claimed_as_success",
                    passed=False,
                    detail=(
                        f"contradictory success claim detected for {hit!r}: "
                        f"failure and success markers within 300 chars. "
                        f"Span: {snippet!r}. (Advisory — see SPEC §13.5; "
                        f"detection may misfire on legitimate prose, a "
                        f"follow-up will refine.)"
                    ),
                    blocking=False,
                )
    return PredicateResult(
        name="evidence.failure_not_claimed_as_success",
        passed=True,
        detail="no contradictory success claims detected.",
        blocking=False,
    )


# ---------------------------------------------------------------------------
# Predicate-source map (slice F effective-rules surfacing)
# ---------------------------------------------------------------------------
#
# Each predicate name maps to a label naming where the rule originated:
#
# - ``core`` — portable harness rules; apply to every conforming repo.
# - ``default`` — default profile rules; redline-derived risk controls.
# - ``repo`` — repository-specific rules; reserved for a later slice
#   when per-repo rule extensions land. No predicates carry this label
#   today.
#
# The labels approximately map to SPEC §13.1's "core, group, repository,
# exception" sources: ``core`` ≈ core harness rules, ``default`` ≈ group
# (default profile) rules, ``repo`` ≈ repository overrides. ``exception`` is not a
# source-label here; exceptions are recorded per-task in the Work Record
# and surfaced via the downgrade pass in :mod:`core.checker.checker`.
PREDICATE_SOURCE: dict[str, str] = {
    # core — portable harness
    "workrecord.exists": "core",
    "workrecord.markers_present": "core",
    "workrecord.required_for_branch_changes": "core",
    "risk.declared": "core",
    "complexity.declared": "core",
    "workrecord.shape_matches_classification": "core",
    "workrecord.routine_fields_present": "core",
    "workrecord.expanded_fields_present": "core",
    "workrecord.state_valid": "core",
    "exceptions.well_formed": "core",
    "exceptions.not_against_boundary": "core",
    "exceptions.not_expired": "core",
    "approval.elevated_clean_context_review_present": "core",
    "approval.high_risk_approval_recorded": "core",
    "approval.clean_context_does_not_satisfy_human": "core",
    "evidence.criteria_have_methods": "core",
    "evidence.failure_not_claimed_as_success": "core",
    "workrecord.commit_order": "core",
    # default — redline-derived risk controls
    "risk.redline_findings_available": "default",
    "risk.boundary_violation_absent": "default",
    "risk.declared_not_below_detected": "default",
    "review.checkpoints_satisfied": "default",
}


# ---------------------------------------------------------------------------
# Work Record commit-order discipline (advisory)
# ---------------------------------------------------------------------------


# Consistent timeout for every git invocation in this layer. The
# branch walk + per-commit `git show` calls all use this. Picked to
# tolerate slow GHES clones without letting a wedged subprocess hang
# the predicate indefinitely.
_GIT_TIMEOUT_SEC = 15


def workrecord_commit_order(ctx: CheckerContext) -> PredicateResult:
    """Advisory: the Work Record's first branch commit lands before the
    first code commit on the same branch.

    A killed mid-task session can only be resumed from the Work Record.
    A WR written retroactively (committed alongside or after the code
    it describes) has no recovery value — it's a postmortem, not a plan.
    This predicate is the harness's objective signal that a WR was
    likely written first.

    Approach: one ``--first-parent --reverse`` walk between the
    configured base ref (``origin/main`` by convention) and the head
    ref. For each commit, ``git show --name-only`` reveals which paths
    it touched; classify as WR-touching, code-touching, or both, and
    track the first of each in chronological order. The classification
    + same-commit detection falls out of the single walk — no second
    git invocation needed.

    Skipped when:
    - ``repo_root`` is None (legacy caller, no git context)
    - git is not on the path or returns an error
    - the branch's base can't be resolved (unrelated history, shallow
      clone where ``origin/main`` is missing)
    - the branch has no commits touching either side (housekeeping or
      no WR file on the branch yet)

    Per-commit ``git show`` failures inside the walk are logged-and-
    continued — a single transient subprocess error doesn't bail the
    predicate. The initial ``git log`` failure is a skip; failures
    inside the walk are skipped commits.

    Advisory only. This is a signal to check whether recovery state
    was sacrificed, not a gate.
    """
    name = "workrecord.commit_order"
    if ctx.repo_root is None:
        return PredicateResult(
            name=name, passed=True,
            detail="skipped — no repo_root available (direct library caller).",
            blocking=False,
        )

    try:
        wr_rel = ctx.backend.resolve_location(ctx.slug)
    except Exception:
        return PredicateResult(
            name=name, passed=True,
            detail="skipped — could not resolve Work Record path.",
            blocking=False,
        )
    # Normalise to forward-slash path for git regardless of host OS.
    # Windows backends produce '.agent-workflow\\tasks\\foo.md' which
    # git treats as a literal path that doesn't match
    # '.agent-workflow/tasks/foo.md' in the tree.
    wr_rel = wr_rel.replace("\\", "/")

    # Base + head resolution. GitHub Actions checks out pull/N/merge
    # which is a single synthetic merge commit; without the override,
    # `origin/main..HEAD` collapses the branch's history to one. The
    # workflow passes the PR's real base+head SHAs via --base-ref /
    # --head-ref or BASE_SHA / HEAD_SHA env vars.
    base = ctx.base_ref or os.environ.get("BASE_SHA") or "origin/main"
    head = ctx.head_ref or os.environ.get("HEAD_SHA") or "HEAD"

    # Step 1: get the branch's commit list in chronological order.
    try:
        log = subprocess.run(
            [
                "git", "log", "--first-parent", "--reverse", "--format=%H",
                f"{base}..{head}",
            ],
            cwd=str(ctx.repo_root),
            capture_output=True,
            text=True,
            timeout=_GIT_TIMEOUT_SEC,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.TimeoutExpired):
        return PredicateResult(
            name=name, passed=True,
            detail="skipped — git unavailable.", blocking=False,
        )
    if log.returncode != 0:
        return PredicateResult(
            name=name, passed=True,
            detail=f"skipped — git log {base}..{head} failed.",
            blocking=False,
        )
    shas = [s.strip() for s in log.stdout.splitlines() if s.strip()]
    if not shas:
        return PredicateResult(
            name=name, passed=True,
            detail=f"skipped — no commits in {base}..{head}.",
            blocking=False,
        )

    # Step 2: walk commits once, classifying each. Track the first
    # WR-touching commit and the first code-touching commit, plus
    # which of the two was assigned first ('wr' or 'code'). Tracking
    # the assignment order in the walk eliminates a later index()
    # lookup — the chronological walk already encodes order, so a
    # one-liner during the walk records what we'd otherwise need
    # `shas.index(...)` to recompute. Per the PR #33 review.
    wr_first: str | None = None
    code_first: str | None = None
    first_kind: str | None = None  # 'wr' | 'code' | None
    for sha in shas:
        try:
            show = subprocess.run(
                ["git", "show", "--first-parent", "--name-only", "--format=", sha],
                cwd=str(ctx.repo_root),
                capture_output=True,
                text=True,
                timeout=_GIT_TIMEOUT_SEC,
                encoding="utf-8",
                errors="replace",
            )
        except (OSError, subprocess.TimeoutExpired):
            # Per-commit failure: don't bail the predicate. Skip this
            # commit and continue — the rest of the walk may still
            # produce a useful classification. If the failure cascade
            # is broad enough that we can't classify either side,
            # we'll fall through to a graceful skip after the loop.
            continue
        if show.returncode != 0:
            continue
        touched = [
            line.strip() for line in show.stdout.splitlines() if line.strip()
        ]
        touched_wr = wr_rel in touched
        touched_code = any(p != wr_rel for p in touched)
        if touched_wr and wr_first is None:
            wr_first = sha
            if first_kind is None:
                first_kind = "wr"
        if touched_code and code_first is None:
            code_first = sha
            if first_kind is None:
                first_kind = "code"
        # Early exit once both first-of-each are known. Walking
        # further can't change the answer.
        if wr_first is not None and code_first is not None:
            break

    if wr_first is None:
        return PredicateResult(
            name=name, passed=True,
            detail=(
                f"skipped — no WR commit in {base}..{head} for {wr_rel!r} "
                "(branch may not have a WR file yet, or git ref not "
                "available)."
            ),
            blocking=False,
        )

    if code_first is None:
        return PredicateResult(
            name=name, passed=True,
            detail="WR committed; no code-only commits on the branch yet.",
            blocking=False,
        )

    if wr_first == code_first:
        return PredicateResult(
            name=name, passed=False,
            detail=(
                "advisory — Work Record and code landed in the same commit "
                f"({wr_first[:8]}). Ideally the WR is a separate commit "
                "BEFORE any code commit so it serves as recovery state. "
                "Non-blocking; treat as a signal to check whether the WR "
                "was written first or retroactively."
            ),
            blocking=False,
        )

    # Different commits. ``first_kind`` was set in the walk: whichever
    # of wr_first / code_first was assigned earlier (chronologically
    # earlier in the branch) is recorded there. No second-pass index
    # lookup, no error case to guard.
    if first_kind == "wr":
        return PredicateResult(
            name=name, passed=True,
            detail=(
                f"Work Record commit ({wr_first[:8]}) lands at or before "
                f"the first code commit ({code_first[:8]}) on this branch."
            ),
            blocking=False,
        )
    return PredicateResult(
        name=name, passed=False,
        detail=(
            "advisory — Work Record was committed AFTER the first code "
            f"commit on this branch (WR: {wr_first[:8]}, first code: "
            f"{code_first[:8]}). The WR was likely written retroactively; "
            "if the session had been killed mid-task, the WR would not "
            "have served as recovery state. Non-blocking; treat as a "
            "signal to check whether plan-first discipline held."
        ),
        blocking=False,
    )

# Order matters — this is the order predicates appear in the verdict.
# The shape-aware predicates sit between markers_present and the
# fields_present predicate so a reviewer reads the verdict top-to-
# bottom: exists, markers, classification (risk + complexity + shape),
# fields, state. Redline predicates (slice B) appended after slice A's
# stable order. Exception predicates (slice F) appended next. Approval
# predicates (slice D) appended last so slice-A/B/F order isn't
# shuffled.
PREDICATES: tuple = (
    workrecord_exists,
    workrecord_markers_present,
    risk_declared,
    complexity_declared,
    shape_matches_classification,
    workrecord_fields_present,
    workrecord_state_valid,
    # --- redline predicates (slice B) -------------------------------
    risk_redline_findings_available,
    risk_boundary_violation_absent,
    risk_declared_not_below_detected,
    # --- review checkpoint enforcement (slice G) --------------------
    # Consumes redline's already-computed checkpoint satisfaction state
    # — no double-implementation of redline's satisfy-by logic. Appended
    # here so the three redline-derived predicates stay grouped.
    review_checkpoints_satisfied,
    # --- exceptions predicates (slice F) ----------------------------
    exceptions_well_formed,
    exceptions_not_against_boundary,
    exceptions_not_expired,
    # --- approval predicates (slice D) ------------------------------
    approval_elevated_clean_context_review_present,
    approval_high_risk_approval_recorded,
    approval_clean_context_does_not_satisfy_human,
    # --- evidence predicates (slice E) ------------------------------
    evidence_criteria_have_methods,
    evidence_failure_not_claimed_as_success,
    # --- WR-lifecycle discipline (advisory) -------------------------
    workrecord_commit_order,
)

# Backwards-compat alias retained for any caller that imported
# ROUTINE_PREDICATES before the slice A rename.
ROUTINE_PREDICATES = PREDICATES
