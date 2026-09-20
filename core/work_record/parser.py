"""Work Record parser.

Parses the marker-bounded block produced by the routine and expanded
templates at ``core/templates/work-record-routine.md`` and
``core/templates/work-record-expanded.md``.

A Work Record is a Markdown block bounded by:

    <!-- agent-workflow:start -->
    **Outcome:** ...
    **Target:** ...
    ...
    <!-- agent-workflow:end -->

The block sits anywhere inside a Markdown file; prose around it is
human notes (implementation references, evidence, result review). Each
field is introduced by ``**<Field name>:**`` and runs until the next
field or the end-marker. Field content may span multiple lines and is
captured verbatim (modulo trailing whitespace).

The record's shape — compact (routine) or expanded — is derived from
its own ``(Risk, Complexity)`` declaration. ``(Routine, Simple)`` may
use the compact shape; everything else must use the expanded shape.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Literal, NotRequired, TypedDict

# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

# Allowed values per SPEC.md §8. Boundary Violation stops the workflow
# before a Work Record is written and is not a valid Risk value.
ALLOWED_RISK: frozenset[str] = frozenset({"Routine", "Elevated", "High"})
ALLOWED_COMPLEXITY: frozenset[str] = frozenset({"Simple", "Moderate", "Large"})

# (Routine, Simple) is the only classification that may use the compact
# (routine) shape. Anything else must use the expanded shape.
_COMPACT_ALLOWED: frozenset[tuple[str, str]] = frozenset({("Routine", "Simple")})


@dataclass(frozen=True)
class RequirementBaseline:
    """The immutable Task Context captured before discovery."""

    source: str | None
    outcome: str
    scope: str
    constraints: str
    completion_criteria: str


@dataclass(frozen=True)
class BehaviorChangeAuthority:
    """BehaviorChangeAuthority domain and name recorded for a requirement change."""

    scope: Literal["task", "repository"]
    name: str


@dataclass(frozen=True)
class BehaviorChangeApproval:
    """BehaviorChangeApproval-shaped evidence bound to one exact behavior change."""

    by: str
    reference: str
    verbatim: str


@dataclass(frozen=True)
class BehaviorChange:
    """One structured Task Context or repository-contract change."""

    target: str
    classification: Literal["equivalent", "coverage-only", "requirement-change"]
    before: str
    after: str
    reason: str
    path: str | None = None
    impact: str | None = None
    alternatives: str | None = None
    authority: BehaviorChangeAuthority | None = None
    approval: BehaviorChangeApproval | None = None






class WorkRecord(TypedDict):
    """Typed routine (compact) Work Record.

    Field labels mirror ``core/templates/work-record-routine.md``; Python
    identifiers are snake_case. ``risk`` and ``complexity`` are the
    spec's two orthogonal axes (§8); ``reason`` is the justification for
    the (risk, complexity) decision (optional on the compact shape since
    only the default (Routine, Simple) is allowed here; non-default
    classifications must use the expanded shape).
    """

    outcome: str
    target: str
    scope: str
    constraints: str
    completion_criteria: str
    risk: str
    complexity: str
    reason: str
    approach: str
    verification: str
    state: str
    requirement_baseline: NotRequired[RequirementBaseline]
    behavior_changes: NotRequired[list[BehaviorChange]]


class ExpandedWorkRecord(TypedDict):
    """Typed expanded Work Record per SPEC.md §9.4.

    Carries the full Task Context + the expanded-path additions:
    Discovery, Material assumptions (each with disproving evidence +
    action), Plan, Verification plan, Plan review, Approvals,
    Exceptions. Reason is required at any non-default classification.

    Implementation, Evidence, and Result review references live in the
    prose around the marker block — they are not marker-block fields.

    The ``exceptions`` field carries the free-text content of the
    Exceptions marker-block field as written by the agent. The
    structured per-entry shape (rule / reason / scope / approver /
    expiry / compensating_validation) is decoded by
    :func:`parse_exceptions` when the checker needs it; the TypedDict
    just carries the raw text so the round-trip render/parse keeps the
    field as a stable string. ``exceptions`` is optional at the record
    level: an empty string or a "no content" sentinel (``—``, ``-``,
    ``None``, ``N/A``; case-insensitive) means no exceptions are recorded.
    """

    outcome: str
    target: str
    scope: str
    constraints: str
    completion_criteria: str
    risk: str
    complexity: str
    reason: str
    discovery: str
    material_assumptions: str
    plan: str
    verification_plan: str
    plan_review: str
    approvals: str
    exceptions: str
    state: str
    requirement_baseline: NotRequired[RequirementBaseline]
    behavior_changes: NotRequired[list[BehaviorChange]]


Shape = Literal["routine", "expanded"]


@dataclass(frozen=True)
class ParsedRecord:
    """Result of parsing a Work Record.

    ``shape`` is determined from the record's own ``(Risk, Complexity)``
    declaration. The right TypedDict is populated:

    - ``shape == "routine"`` → ``record`` is a :class:`WorkRecord`.
    - ``shape == "expanded"`` → ``record`` is an :class:`ExpandedWorkRecord`.

    Callers that already know which shape they want can use the legacy
    :func:`parse` (returns :class:`WorkRecord`, raises on expanded
    input). New callers should use :func:`parse_record` which dispatches
    on the declaration.
    """

    shape: Shape
    record: WorkRecord | ExpandedWorkRecord


class WorkRecordParseError(ValueError):
    """Raised when a Work Record cannot be parsed.

    Carries a short, human-readable reason. Callers (the checker, the
    skill driver) translate it into named-predicate failures in their
    own verdict format.
    """


# ---------------------------------------------------------------------------
# Markers and field schemas
# ---------------------------------------------------------------------------

_START_MARKER = "<!-- agent-workflow:start -->"
_END_MARKER = "<!-- agent-workflow:end -->"

# Routine field order. ``parse()`` returns these in insertion order
# (Python 3.7+). Labels match the routine template exactly, case-
# sensitive — cosmetic edits to the template surface as parse failures
# rather than silently re-mapping.
_FIELD_SCHEMA: tuple[tuple[str, str], ...] = (
    ("Outcome", "outcome"),
    ("Target", "target"),
    ("Scope", "scope"),
    ("Constraints", "constraints"),
    ("Completion criteria", "completion_criteria"),
    ("Risk", "risk"),
    ("Complexity", "complexity"),
    ("Reason", "reason"),
    ("Approach", "approach"),
    ("Verification", "verification"),
    ("State", "state"),
)

# Expanded field order. Mirrors the expanded template; same matching
# rules. ``approach`` and ``verification`` from the routine schema are
# absorbed by the richer ``plan`` and ``verification_plan`` fields on
# the expanded path.
_EXPANDED_FIELD_SCHEMA: tuple[tuple[str, str], ...] = (
    ("Outcome", "outcome"),
    ("Target", "target"),
    ("Scope", "scope"),
    ("Constraints", "constraints"),
    ("Completion criteria", "completion_criteria"),
    ("Risk", "risk"),
    ("Complexity", "complexity"),
    ("Reason", "reason"),
    ("Discovery", "discovery"),
    ("Material assumptions", "material_assumptions"),
    ("Plan", "plan"),
    ("Verification plan", "verification_plan"),
    ("Plan review", "plan_review"),
    ("Approvals", "approvals"),
    ("State", "state"),
)

# Optional fields are accepted on both shapes so legacy records remain
# parseable and routine records do not migrate merely to carry integrity data.
_OPTIONAL_JSON_FIELDS: dict[str, str] = {
    "Requirement baseline": "requirement_baseline",
    "Behavior changes": "behavior_changes",
}
_EXPANDED_OPTIONAL_EXTRA_FIELDS: dict[str, str] = {
    **_OPTIONAL_JSON_FIELDS,
    "Exceptions": "exceptions",
}
_ROUTINE_OPTIONAL_EXTRA_FIELDS: dict[str, str] = dict(_OPTIONAL_JSON_FIELDS)

# Fields whose value is allowed to be empty on each shape. Everything
# else is rejected as malformed when its value is blank. On the routine
# shape, ``reason`` is optional. On the expanded shape, ``approvals``
# is optional (only required at High risk; the checker will enforce
# that conditionally in a later step).
_OPTIONAL_FIELDS: frozenset[str] = frozenset({"reason"})
_EXPANDED_OPTIONAL_FIELDS: frozenset[str] = frozenset({"approvals", "exceptions"})

# Sentinel values meaning "no content here" on fields that accept an
# explicit absence-marker (Exceptions, and any future field that uses
# the same convention). All compared case-insensitively after a
# ``.lower()``. The canonical form in the template is ``—`` (em-dash);
# the rest are common agent-keyboard alternatives the parser tolerates
# so a Work Record isn't rejected over a punctuation typo.
#
# IMPORTANT: this set is for fields whose absence-marker is structural
# (the parser routes on it). It is NOT for required content fields
# where the validator already enforces non-emptiness.
_NONE_SENTINELS: frozenset[str] = frozenset({
    "—",      # em-dash (template canonical)
    "-",      # hyphen (common substitute on keyboards without em-dash)
    "--",     # double hyphen
    "none",   # word
    "n/a",    # not-applicable
    "na",     # variant of n/a
})

_LABELS_BY_KEY = {key: label for label, key in _FIELD_SCHEMA}

# Match ``**Label:**`` at the start of a line. ``re.M`` lets ``^`` match
# every line. The captured group is the label text; trailing content on
# that line and subsequent lines (up to the next match or end-of-block)
# is the field value.
_FIELD_HEADER_RE = re.compile(r"^\*\*([^*]+?):\*\*\s*", re.MULTILINE)


# ---------------------------------------------------------------------------
# Marker extraction
# ---------------------------------------------------------------------------

# Markers must appear on their own line — i.e. start-of-line, only
# whitespace allowed before and after. This is what the template
# renders and what we read; references to the marker tokens inside
# prose (e.g. backticked inline mentions) MUST NOT be matched as
# block boundaries. Anchoring to line boundaries avoids that
# ambiguity.
_START_MARKER_RE = re.compile(rf"^[ \t]*{re.escape(_START_MARKER)}[ \t]*$", re.MULTILINE)
_END_MARKER_RE = re.compile(rf"^[ \t]*{re.escape(_END_MARKER)}[ \t]*$", re.MULTILINE)

# Templates put an allowed-values hint comment right after a field (notably
# the trailing State hint). The last field's value runs to the end of the
# block, so it would otherwise swallow that comment and fail validation.
# Comments in the marker block are always hints, never field content.
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def _extract_block(text: str) -> str:
    """Return the substring strictly between the start and end markers.

    Raises ``WorkRecordParseError`` if either marker is missing or if
    multiple start/end markers appear on their own lines (single block
    per file by design; the local backend's read/write contract assumes
    exactly one).
    """
    starts = list(_START_MARKER_RE.finditer(text))
    ends = list(_END_MARKER_RE.finditer(text))
    if not starts:
        raise WorkRecordParseError(
            f"missing {_START_MARKER!r} — no Work Record block found"
        )
    if not ends:
        raise WorkRecordParseError(
            f"missing {_END_MARKER!r} — Work Record block is unterminated"
        )
    if len(starts) > 1 or len(ends) > 1:
        raise WorkRecordParseError(
            f"multiple Work Record blocks found "
            f"(start markers: {len(starts)}, end markers: {len(ends)}) — "
            "exactly one block per file is expected"
        )

    start_idx = starts[0].end()
    end_idx = ends[0].start()
    if end_idx < start_idx:
        raise WorkRecordParseError(
            "end marker precedes start marker — Work Record block is malformed"
        )
    return text[start_idx:end_idx]


# ---------------------------------------------------------------------------
# Field extraction
# ---------------------------------------------------------------------------


def _extract_fields(block: str) -> dict[str, str]:
    """Walk every ``**Label:**`` header in the block and capture values.

    Returns a mapping from the raw label (as it appears in the file) to
    the field value (stripped of surrounding whitespace). Detects
    duplicate labels and reports them as parse errors — duplicates would
    silently shadow each other otherwise.
    """
    matches = list(_FIELD_HEADER_RE.finditer(block))
    if not matches:
        raise WorkRecordParseError(
            "Work Record block contains no '**Label:**' field headers"
        )

    out: dict[str, str] = {}
    for i, match in enumerate(matches):
        label = match.group(1).strip()
        value_start = match.end()
        value_end = matches[i + 1].start() if i + 1 < len(matches) else len(block)
        value = _HTML_COMMENT_RE.sub("", block[value_start:value_end]).strip()
        if label in out:
            raise WorkRecordParseError(
                f"duplicate field {label!r} in Work Record block — "
                "each field may appear only once"
            )
        out[label] = value
    return out


def _validate_against_schema(
    found: dict[str, str],
    schema: tuple[tuple[str, str], ...],
    optional: frozenset[str],
    shape_name: str,
    optional_extra_fields: dict[str, str] | None = None,
) -> dict[str, str]:
    """Generic field validator used by both shapes.

    Returns a mapping from typed-dict key to value, in the schema's
    declared order. Raises :exc:`WorkRecordParseError` on:

    - missing required field labels
    - unknown extra field labels (likely a typo or a cross-shape field)
    - empty value for a field not listed in ``optional``

    Optional-extra fields are recognised when present but never demanded
    when absent. Used by the expanded shape to accept slice-F's
    ``Exceptions`` field without making it a required schema entry —
    existing records without an Exceptions field parse unchanged.

    The caller casts the result to its specific TypedDict.
    """
    optional_extra = optional_extra_fields or {}
    expected_labels = {label for label, _ in schema}
    allowed_labels = expected_labels | set(optional_extra.keys())
    found_labels = set(found)

    missing = expected_labels - found_labels
    extra = found_labels - allowed_labels
    if missing:
        raise WorkRecordParseError(
            f"Work Record block is missing required {shape_name}-path field(s): "
            + ", ".join(sorted(missing))
        )
    if extra:
        raise WorkRecordParseError(
            f"Work Record block contains unknown field(s) "
            f"({shape_name} path expects only the {shape_name} fields): "
            + ", ".join(sorted(extra))
        )

    record: dict[str, str] = {}
    for label, key in schema:
        value = found[label]
        if not value and key not in optional:
            raise WorkRecordParseError(
                f"Work Record field {label!r} is empty — "
                f"every required {shape_name}-path field must have content"
            )
        record[key] = value

    # Optional-extra fields land in the typed-dict only when present.
    # Empty values are tolerated regardless of the optional set (the
    # field is optional-extra; "—" or "" both mean absent).
    for label, key in optional_extra.items():
        if label in found:
            record[key] = found[label]

    return record


def _validate_routine_fields(found: dict[str, str]) -> WorkRecord:
    """Validate the routine-path field set. See :func:`_validate_against_schema`."""
    return _validate_against_schema(  # type: ignore[return-value]
        found, _FIELD_SCHEMA, _OPTIONAL_FIELDS, shape_name="routine",
        optional_extra_fields=_ROUTINE_OPTIONAL_EXTRA_FIELDS,
    )


def _validate_expanded_fields(found: dict[str, str]) -> ExpandedWorkRecord:
    """Validate the expanded-path field set. See :func:`_validate_against_schema`."""
    return _validate_against_schema(  # type: ignore[return-value]
        found,
        _EXPANDED_FIELD_SCHEMA,
        _EXPANDED_OPTIONAL_FIELDS,
        shape_name="expanded",
        optional_extra_fields=_EXPANDED_OPTIONAL_EXTRA_FIELDS,
    )


def _decide_shape(found: dict[str, str]) -> Shape:
    """Decide which shape this record claims, from its ``(Risk, Complexity)``.

    Both fields must be present and carry an allowed value before we
    can pick a shape. The shape selection rule is simple:

    - ``(Routine, Simple)`` → ``routine``.
    - anything else → ``expanded`` (the classification demands it).

    The shape decided here is just the *expected* shape; whether the
    record's actual fields match the shape's required set is the
    validator's job in the next step.
    """
    risk = found.get("Risk", "").strip()
    complexity = found.get("Complexity", "").strip()
    if not risk:
        raise WorkRecordParseError(
            "Work Record block is missing the **Risk:** field — cannot decide "
            "whether the routine or expanded shape applies"
        )
    if not complexity:
        raise WorkRecordParseError(
            "Work Record block is missing the **Complexity:** field — cannot "
            "decide whether the routine or expanded shape applies"
        )
    if risk not in ALLOWED_RISK:
        raise WorkRecordParseError(
            f"Risk value {risk!r} is not allowed; expected one of "
            + ", ".join(sorted(ALLOWED_RISK))
        )
    if complexity not in ALLOWED_COMPLEXITY:
        raise WorkRecordParseError(
            f"Complexity value {complexity!r} is not allowed; expected one of "
            + ", ".join(sorted(ALLOWED_COMPLEXITY))
        )
    if (risk, complexity) in _COMPACT_ALLOWED:
        return "routine"
    return "expanded"


# ---------------------------------------------------------------------------
# Requirement-integrity JSON
# ---------------------------------------------------------------------------

_BASELINE_KEYS = frozenset({
    "source",
    "outcome",
    "scope",
    "constraints",
    "completion_criteria",
})
_BEHAVIOR_CORE_KEYS = frozenset({
    "target",
    "classification",
    "before",
    "after",
    "reason",
})
_BEHAVIOR_CHANGE_KEYS = frozenset({
    "impact",
    "alternatives",
    "authority",
    "approval",
})
_AUTHORITY_KEYS = frozenset({"scope", "name"})
_APPROVAL_KEYS = frozenset({"by", "reference", "verbatim"})
_TASK_CONTEXT_TARGETS = frozenset(
    {
        "task-context.outcome",
        "task-context.scope",
        "task-context.constraints",
        "task-context.completion_criteria",
    }
)
_BEHAVIOR_CLASSIFICATIONS = frozenset(
    {"equivalent", "coverage-only", "requirement-change"}
)


def _json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Reject duplicate object keys instead of silently keeping the last one."""
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _load_integrity_json(text: str, label: str) -> object:
    try:
        return json.loads(
            text,
            object_pairs_hook=_json_object,
            parse_constant=lambda value: (_ for _ in ()).throw(
                ValueError(f"non-standard JSON constant {value!r}")
            ),
        )
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise WorkRecordParseError(f"{label} must be valid canonical JSON: {exc}") from exc


def _required_json_string(value: object, field: str) -> str:
    if not isinstance(value, str):
        raise WorkRecordParseError(f"{field} must be a JSON string")
    if not value.strip():
        raise WorkRecordParseError(f"{field} must be a non-empty string")
    return value


def _exact_keys(value: object, expected: frozenset[str], label: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise WorkRecordParseError(f"{label} must be a JSON object")
    actual = set(value)
    missing = expected - actual
    unknown = actual - expected
    if missing:
        raise WorkRecordParseError(
            f"{label} is missing required key(s): {', '.join(sorted(missing))}"
        )
    if unknown:
        raise WorkRecordParseError(
            f"{label} contains unknown key(s): {', '.join(sorted(unknown))}"
        )
    return value


def parse_requirement_baseline(text: str) -> RequirementBaseline:
    """Parse and validate a canonical Requirement baseline JSON object."""
    value = _exact_keys(
        _load_integrity_json(text, "Requirement baseline"),
        _BASELINE_KEYS,
        "Requirement baseline",
    )
    source = value["source"]
    if source is not None:
        source = _required_json_string(source, "Requirement baseline.source")
    return RequirementBaseline(
        source=source,
        outcome=_required_json_string(value["outcome"], "Requirement baseline.outcome"),
        scope=_required_json_string(value["scope"], "Requirement baseline.scope"),
        constraints=_required_json_string(value["constraints"], "Requirement baseline.constraints"),
        completion_criteria=_required_json_string(
            value["completion_criteria"], "Requirement baseline.completion_criteria"
        ),
    )


def _parse_behavior_entry(value: object, index: int) -> BehaviorChange:
    label = f"Behavior changes entry #{index}"
    if not isinstance(value, dict):
        raise WorkRecordParseError(f"{label} must be a JSON object")
    target_value = value.get("target")
    target = _required_json_string(target_value, f"{label}.target")
    classification = _required_json_string(
        value.get("classification"), f"{label}.classification"
    )
    if classification not in _BEHAVIOR_CLASSIFICATIONS:
        raise WorkRecordParseError(
            f"{label}.classification must be one of "
            + ", ".join(sorted(_BEHAVIOR_CLASSIFICATIONS))
        )
    expected = _BEHAVIOR_CORE_KEYS | {"path"}
    required = set(_BEHAVIOR_CORE_KEYS)
    if classification == "requirement-change":
        expected |= _BEHAVIOR_CHANGE_KEYS
        required |= {"impact", "alternatives", "authority"}
    missing = required - set(value)
    unknown = set(value) - expected
    if missing:
        raise WorkRecordParseError(
            f"{label} is missing required key(s): {', '.join(sorted(missing))}"
        )
    if unknown:
        raise WorkRecordParseError(
            f"{label} contains unknown key(s): {', '.join(sorted(unknown))}"
        )
    if target not in _TASK_CONTEXT_TARGETS and target != "repository-contract":
        raise WorkRecordParseError(f"{label}.target has an invalid shape: {target!r}")
    has_path = "path" in value
    path: str | None = None
    if target == "repository-contract":
        if not has_path:
            raise WorkRecordParseError(f"{label}.path is required for repository-contract")
        path = _required_json_string(value["path"], f"{label}.path")
    elif has_path:
        raise WorkRecordParseError(f"{label}.path is only valid for repository-contract")

    before = _required_json_string(value["before"], f"{label}.before")
    after = _required_json_string(value["after"], f"{label}.after")
    if before == after:
        raise WorkRecordParseError(f"{label} before and after must differ")
    reason = _required_json_string(value["reason"], f"{label}.reason")

    impact: str | None = None
    alternatives: str | None = None
    authority: BehaviorChangeAuthority | None = None
    approval: BehaviorChangeApproval | None = None
    if classification == "requirement-change":
        impact = _required_json_string(value["impact"], f"{label}.impact")
        alternatives = _required_json_string(value["alternatives"], f"{label}.alternatives")
        authority_value = _exact_keys(value["authority"], _AUTHORITY_KEYS, f"{label}.authority")
        authority_scope = _required_json_string(
            authority_value["scope"], f"{label}.authority.scope"
        )
        if authority_scope not in {"task", "repository"}:
            raise WorkRecordParseError(
                f"{label}.authority.scope must be 'task' or 'repository'"
            )
        authority = BehaviorChangeAuthority(
            scope=authority_scope,  # type: ignore[arg-type]
            name=_required_json_string(authority_value["name"], f"{label}.authority.name"),
        )
        if "approval" in value and value["approval"] is not None:
            approval_value = _exact_keys(
                value["approval"], _APPROVAL_KEYS, f"{label}.approval"
            )
            approval = BehaviorChangeApproval(
                by=_required_json_string(approval_value["by"], f"{label}.approval.by"),
                reference=_required_json_string(
                    approval_value["reference"], f"{label}.approval.reference"
                ),
                verbatim=_required_json_string(
                    approval_value["verbatim"], f"{label}.approval.verbatim"
                ),
            )
    return BehaviorChange(
        target=target,
        classification=classification,  # type: ignore[arg-type]
        before=before,
        after=after,
        reason=reason,
        path=path,
        impact=impact,
        alternatives=alternatives,
        authority=authority,
        approval=approval,
    )


def parse_behavior_changes(text: str) -> list[BehaviorChange]:
    """Parse and validate the canonical Behavior changes JSON array."""
    value = _load_integrity_json(text, "Behavior changes")
    if not isinstance(value, list):
        raise WorkRecordParseError("Behavior changes must be a JSON array")
    out = [_parse_behavior_entry(entry, index) for index, entry in enumerate(value, 1)]
    repository_paths = [entry.path for entry in out if entry.target == "repository-contract"]
    duplicates = {path for path in repository_paths if repository_paths.count(path) > 1}
    if duplicates:
        raise WorkRecordParseError(
            "Behavior changes contains duplicate repository-contract path(s): "
            + ", ".join(sorted(duplicates))
        )
    return out


def _parse_optional_integrity_fields(
    found: dict[str, str], record: dict[str, object]
) -> None:
    if "Requirement baseline" in found:
        record["requirement_baseline"] = parse_requirement_baseline(
            found["Requirement baseline"]
        )
    if "Behavior changes" in found:
        record["behavior_changes"] = parse_behavior_changes(found["Behavior changes"])


# ---------------------------------------------------------------------------
# Exceptions sub-parsing (slice F)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExceptionEntry:
    """One per-task exception recorded under the Exceptions field.

    SPEC §11 enumerates the fields: rule, reason, scope, approver,
    expiry (where relevant), compensating validation. The parser
    enforces structural presence of every required sub-field; the
    checker validates content (expiry against today, rule against the
    non-waivable set).
    """

    rule: str
    reason: str
    scope: str
    approver: str
    compensating_validation: str
    expiry: str | None  # ISO date 'YYYY-MM-DD' when set; None when absent


_EXCEPTION_REQUIRED_SUBFIELDS: tuple[str, ...] = (
    "rule",
    "reason",
    "scope",
    "approver",
    "compensating_validation",
)
_EXCEPTION_OPTIONAL_SUBFIELDS: tuple[str, ...] = ("expiry",)
_EXCEPTION_ALL_SUBFIELDS: frozenset[str] = frozenset(
    _EXCEPTION_REQUIRED_SUBFIELDS + _EXCEPTION_OPTIONAL_SUBFIELDS
)


def parse_exceptions(text: str) -> list[ExceptionEntry]:
    """Parse the Exceptions field value into a list of structured entries.

    The expected shape is one entry per dash-bullet, with sub-fields on
    indented `key: value` lines:

        - rule: risk.declared_not_below_detected
          reason: this PR is a temporary lift waived by approver X
          scope: this PR only
          approver: I123456
          expiry: 2026-07-01
          compensating_validation: manual smoke test on staging

    An empty input or one consisting only of a recognised "no content"
    sentinel (``—``, ``-``, ``--``, ``None``, ``N/A``; case-insensitive)
    produces ``[]``. The em-dash is the template canonical; the rest
    are common substitutes accepted to avoid rejecting Work Records
    over a punctuation typo. Whitespace before sub-field keys is
    tolerated. Unknown sub-field names raise :exc:`WorkRecordParseError`
    so typos are caught loudly.

    The parser's job is **structure** — that every entry carries the
    required sub-fields. It does not validate content (whether the
    `expiry` is in the past, whether the `rule` names a real predicate
    — those are the checker's job).
    """
    stripped = text.strip()
    if not stripped or stripped.lower() in _NONE_SENTINELS:
        return []

    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for raw_line in stripped.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        if line.lstrip().startswith("- "):
            # Start of a new entry. The leading dash carries the first
            # sub-field on the same line; e.g. "- rule: foo".
            if current is not None:
                entries.append(current)
            current = {}
            first = line.lstrip()[2:]  # strip "- "
            key, sep, value = first.partition(":")
            if not sep:
                raise WorkRecordParseError(
                    f"Exceptions entry: first line must be 'key: value', got {first!r}"
                )
            key = key.strip()
            if key not in _EXCEPTION_ALL_SUBFIELDS:
                raise WorkRecordParseError(
                    f"Exceptions entry: unknown sub-field {key!r}; expected one of "
                    + ", ".join(sorted(_EXCEPTION_ALL_SUBFIELDS))
                )
            current[key] = value.strip()
        else:
            # Continuation sub-field within the current entry.
            if current is None:
                raise WorkRecordParseError(
                    f"Exceptions content: sub-field line {line!r} appears before "
                    "any '- key: value' entry header"
                )
            key, sep, value = line.partition(":")
            if not sep:
                raise WorkRecordParseError(
                    f"Exceptions entry: continuation line must be 'key: value', got {line!r}"
                )
            key = key.strip()
            if key not in _EXCEPTION_ALL_SUBFIELDS:
                raise WorkRecordParseError(
                    f"Exceptions entry: unknown sub-field {key!r}; expected one of "
                    + ", ".join(sorted(_EXCEPTION_ALL_SUBFIELDS))
                )
            if key in current:
                raise WorkRecordParseError(
                    f"Exceptions entry: duplicate sub-field {key!r} in the same entry"
                )
            current[key] = value.strip()

    if current is not None:
        entries.append(current)

    out: list[ExceptionEntry] = []
    for i, entry in enumerate(entries):
        missing = [k for k in _EXCEPTION_REQUIRED_SUBFIELDS if k not in entry]
        if missing:
            raise WorkRecordParseError(
                f"Exceptions entry #{i + 1}: missing required sub-field(s): "
                + ", ".join(missing)
            )
        out.append(
            ExceptionEntry(
                rule=entry["rule"],
                reason=entry["reason"],
                scope=entry["scope"],
                approver=entry["approver"],
                compensating_validation=entry["compensating_validation"],
                expiry=entry.get("expiry"),
            )
        )
    return out


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------


def parse_record(text: str) -> ParsedRecord:
    """Parse a Markdown string into a :class:`ParsedRecord`.

    Reads the marker-bounded block, peeks at ``(Risk, Complexity)`` to
    decide which shape applies, then validates the field set against
    that shape's schema. Raises :exc:`WorkRecordParseError` on any
    malformed input — including when the declared classification
    demands the expanded shape but the field set is the routine set
    (or vice-versa).

    Callers that need the resulting record can read ``parsed.shape`` to
    branch; the ``parsed.record`` field is a :class:`WorkRecord` or
    :class:`ExpandedWorkRecord` depending on shape.
    """
    block = _extract_block(text)
    found = _extract_fields(block)
    shape = _decide_shape(found)
    if shape == "routine":
        record = _validate_routine_fields(found)
        _parse_optional_integrity_fields(found, record)
        return ParsedRecord(shape="routine", record=record)
    record = _validate_expanded_fields(found)
    _parse_optional_integrity_fields(found, record)
    return ParsedRecord(shape="expanded", record=record)


def parse(text: str) -> WorkRecord:
    """Parse a Markdown string into a routine :class:`WorkRecord`.

    Legacy entry point retained for backward compatibility with callers
    (the checker, the local backend) that pre-date the expanded shape.
    Returns the routine record when the input is routine; raises
    :exc:`WorkRecordParseError` when the input is expanded — those
    callers will migrate to :func:`parse_record` as the expanded
    checker predicates land.
    """
    parsed = parse_record(text)
    if parsed.shape != "routine":
        raise WorkRecordParseError(
            "Work Record is expanded shape (declared by its Risk/Complexity); "
            "use parse_record() to handle both shapes"
        )
    # mypy knows this is WorkRecord given the shape guard above.
    return parsed.record  # type: ignore[return-value]


def render(record: WorkRecord) -> str:
    """Render a routine :class:`WorkRecord` to a canonical marker block.

    Output is round-trip stable: ``parse(render(r)) == r`` for any valid
    routine WorkRecord. The local backend uses this on write for routine
    records; tests use it to verify the parser captures everything the
    renderer needs.

    Returns a single block followed by a trailing newline so the
    content can be embedded into a Markdown file without joining
    artifacts.
    """
    return _render_against(
        record, _FIELD_SCHEMA, optional_extra_fields=_ROUTINE_OPTIONAL_EXTRA_FIELDS
    )


def render_expanded(record: ExpandedWorkRecord) -> str:
    """Render an :class:`ExpandedWorkRecord` to a canonical marker block.

    Output is round-trip stable: ``parse_record(render_expanded(r)).record == r``
    for any valid expanded ExpandedWorkRecord. Optional-extra fields
    (``Exceptions``) are rendered after the schema fields when the
    record carries them, so a record that came in with an Exceptions
    field is written back with it; a record without the field is
    written without it.
    """
    return _render_against(
        record,
        _EXPANDED_FIELD_SCHEMA,
        optional_extra_fields=_EXPANDED_OPTIONAL_EXTRA_FIELDS,
    )


def render_record(parsed: ParsedRecord) -> str:
    """Render a :class:`ParsedRecord` to a canonical marker block.

    Dispatches on ``parsed.shape``. Use this when the caller has a
    :class:`ParsedRecord` and doesn't care which shape it is — the
    backend write path is the typical consumer.
    """
    if parsed.shape == "routine":
        return render(parsed.record)  # type: ignore[arg-type]
    return render_expanded(parsed.record)  # type: ignore[arg-type]


def _integrity_json_value(key: str, value: object) -> str:
    if key == "requirement_baseline":
        if not isinstance(value, RequirementBaseline):
            raise WorkRecordParseError("requirement_baseline must be a RequirementBaseline")
        data: object = {
            "source": value.source,
            "outcome": value.outcome,
            "scope": value.scope,
            "constraints": value.constraints,
            "completion_criteria": value.completion_criteria,
        }
    elif key == "behavior_changes":
        if not isinstance(value, list) or not all(
            isinstance(entry, BehaviorChange) for entry in value
        ):
            raise WorkRecordParseError(
                "behavior_changes must be a list of BehaviorChange entries"
            )
        entries: list[dict[str, object]] = []
        for entry in value:
            item: dict[str, object] = {
                "target": entry.target,
                "classification": entry.classification,
                "before": entry.before,
                "after": entry.after,
                "reason": entry.reason,
            }
            if entry.path is not None:
                item["path"] = entry.path
            if entry.classification == "requirement-change":
                item.update(
                    {
                        "impact": entry.impact,
                        "alternatives": entry.alternatives,
                        "authority": (
                            None
                            if entry.authority is None
                            else {
                                "scope": entry.authority.scope,
                                "name": entry.authority.name,
                            }
                        ),
                    }
                )
                if entry.approval is not None:
                    item["approval"] = {
                        "by": entry.approval.by,
                        "reference": entry.approval.reference,
                        "verbatim": entry.approval.verbatim,
                    }
            entries.append(item)
        data = entries
    else:
        raise WorkRecordParseError(f"unknown integrity JSON field {key!r}")
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _render_against(
    record: WorkRecord | ExpandedWorkRecord,
    schema: tuple[tuple[str, str], ...],
    optional_extra_fields: dict[str, str] | None = None,
) -> str:
    """Common rendering loop. Each schema entry contributes one line.

    Optional-extra fields (per ``optional_extra_fields``) emit only
    when the record carries the key — keeps the rendered block free of
    placeholder lines for fields that weren't set.
    """
    parts = [_START_MARKER]
    for label, key in schema:
        parts.append(f"**{label}:** {record[key]}")  # type: ignore[literal-required]
    extra = optional_extra_fields or {}
    # Render optional-extras after the State field would conflict —
    # State is the last schema entry in expanded, and Exceptions should
    # come BEFORE State (matches the template). Splice them in by
    # rebuilding: schema entries minus State, then extras, then State.
    if extra:
        # Re-build parts to keep State last while inserting optional-
        # extras before it.
        body_parts = parts[1:]  # everything after the start marker
        # Find State's position; State is always the last in our schemas.
        state_line = body_parts[-1]
        body_parts = body_parts[:-1]
        for label, key in extra.items():
            # ``record.get`` works because TypedDicts are dicts at runtime;
            # emit the field only when present.
            value = record.get(key)  # type: ignore[misc]
            if value is None or (key not in _OPTIONAL_JSON_FIELDS.values() and value == ""):
                continue
            rendered = (
                _integrity_json_value(key, value)
                if key in _OPTIONAL_JSON_FIELDS.values()
                else str(value)
            )
            line = f"**{label}:** {rendered}"
            if label == "Requirement baseline":
                completion = next(
                    i
                    for i, part in enumerate(body_parts)
                    if part.startswith("**Completion criteria:**")
                )
                body_parts.insert(completion + 1, line)
            else:
                body_parts.append(line)
        body_parts.append(state_line)
        parts = [parts[0]] + body_parts
    parts.append(_END_MARKER)
    return "\n".join(parts) + "\n"


# Backwards-compat alias for the test helper introduced in Step 1.
_render_for_roundtrip = render


# ---------------------------------------------------------------------------
# Block location (used by the local backend to splice writes into existing files)
# ---------------------------------------------------------------------------


def find_block_span(text: str) -> tuple[int, int] | None:
    """Return ``(start, end)`` indices of the marker block in ``text``.

    The span covers the start marker through the end marker, inclusive of
    both. Returns ``None`` when no block is present. Raises
    :exc:`WorkRecordParseError` for the same multi-block and
    end-before-start cases that ``parse`` rejects — the backend should
    refuse to overwrite a malformed file rather than guessing.

    Markers are matched on their own line (same rule as :func:`parse`);
    inline references in prose are ignored.
    """
    starts = list(_START_MARKER_RE.finditer(text))
    ends = list(_END_MARKER_RE.finditer(text))
    if not starts and not ends:
        return None
    if not starts:
        raise WorkRecordParseError(
            f"missing {_START_MARKER!r} — Work Record block is malformed"
        )
    if not ends:
        raise WorkRecordParseError(
            f"missing {_END_MARKER!r} — Work Record block is unterminated"
        )
    if len(starts) > 1 or len(ends) > 1:
        raise WorkRecordParseError(
            "multiple Work Record blocks found — exactly one block per file is expected"
        )

    start_idx = starts[0].start()
    end_idx = ends[0].end()
    if end_idx <= start_idx:
        raise WorkRecordParseError(
            "end marker precedes start marker — Work Record block is malformed"
        )
    return start_idx, end_idx


# ---------------------------------------------------------------------------
# Internal helpers (kept private)
# ---------------------------------------------------------------------------
