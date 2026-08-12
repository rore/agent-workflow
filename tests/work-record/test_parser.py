"""Tests for the routine Work Record parser.

Exercises the happy path (round-trip on the routine-pass fixture) plus
the error paths the slice's checker (Step 4) needs to surface as named
predicate failures.

Run via the layer harness:

    bash tests/work-record/run.sh

or directly:

    python -m pytest tests/work-record/test_parser.py -v
"""

from __future__ import annotations

from pathlib import Path

import pytest

from core.work_record import WorkRecord, WorkRecordParseError, parse
from core.work_record.parser import _render_for_roundtrip

REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTINE_PASS = REPO_ROOT / "tests" / "fixtures" / "work-record" / "routine-pass" / "work-record.md"


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_routine_pass_fixture_parses() -> None:
    """The routine-pass fixture parses into a complete WorkRecord."""
    record = parse(ROUTINE_PASS.read_text(encoding="utf-8"))

    # Every routine field is present and non-empty (Reason may be empty).
    expected_keys = {
        "outcome",
        "target",
        "scope",
        "constraints",
        "completion_criteria",
        "risk",
        "complexity",
        "reason",
        "approach",
        "verification",
        "state",
    }
    assert set(record.keys()) == expected_keys
    for key, value in record.items():
        if key == "reason":
            # Reason is optional on the routine path; the fixture
            # populates it but other records may leave it empty.
            continue
        assert value, f"field {key!r} parsed to empty string"

    # Sanity-check a couple of fields against the fixture's content. We
    # only assert anchor substrings, not exact equality — the fixture
    # may evolve and we don't want every prose tweak to break this.
    assert "wallet" in record["outcome"].lower()
    assert "wallet-service" in record["target"]
    assert "Ready for review" in record["state"]


def test_round_trip_is_stable() -> None:
    """parse -> render -> parse yields an equal WorkRecord.

    Round-trip stability is what makes the parser safe to use as the
    Step 3 backend's read half: the backend will preserve original
    formatting on write, but tests want to know the parser captures
    everything the renderer needs to reconstruct.
    """
    first = parse(ROUTINE_PASS.read_text(encoding="utf-8"))
    rendered = _render_for_roundtrip(first)
    second = parse(rendered)
    assert first == second


# ---------------------------------------------------------------------------
# Error paths — these become named predicate failures in the Step 4 checker
# ---------------------------------------------------------------------------


def _block(*lines: str) -> str:
    """Wrap field lines in the marker pair. Helper for compact test cases."""
    return "<!-- agent-workflow:start -->\n" + "\n".join(lines) + "\n<!-- agent-workflow:end -->\n"


def test_missing_start_marker_raises() -> None:
    with pytest.raises(WorkRecordParseError, match="missing.*start"):
        parse("**Outcome:** anything\n<!-- agent-workflow:end -->\n")


def test_missing_end_marker_raises() -> None:
    with pytest.raises(WorkRecordParseError, match="missing.*end"):
        parse("<!-- agent-workflow:start -->\n**Outcome:** anything\n")


def test_multiple_blocks_raise() -> None:
    text = _block("**Outcome:** a") + _block("**Outcome:** b")
    with pytest.raises(WorkRecordParseError, match="multiple"):
        parse(text)


def test_end_before_start_raises() -> None:
    text = "<!-- agent-workflow:end -->\n**Outcome:** x\n<!-- agent-workflow:start -->\n"
    with pytest.raises(WorkRecordParseError, match="precedes"):
        parse(text)


def test_missing_required_field_raises() -> None:
    # Drop the Target field; everything else present.
    text = _block(
        "**Outcome:** o",
        "**Scope:** s",
        "**Constraints:** c",
        "**Completion criteria:** cc",
        "**Risk:** Routine",

        "**Complexity:** Simple",

        "**Reason:** reason",
        "**Approach:** a",
        "**Verification:** v",
        "**State:** Ready to implement",
    )
    with pytest.raises(WorkRecordParseError, match="missing.*Target"):
        parse(text)


def test_unknown_field_raises() -> None:
    # An expanded-path field accidentally written into a routine record.
    text = _block(
        "**Outcome:** o",
        "**Target:** t",
        "**Scope:** s",
        "**Constraints:** c",
        "**Completion criteria:** cc",
        "**Risk:** Routine",

        "**Complexity:** Simple",

        "**Reason:** —",
        "**Approach:** a",
        "**Verification:** v",
        "**State:** Ready to implement",
        "**Material assumptions:** something only expanded-path records carry",
    )
    with pytest.raises(WorkRecordParseError, match="unknown field"):
        parse(text)


def test_duplicate_field_raises() -> None:
    text = _block(
        "**Outcome:** first",
        "**Outcome:** second",
        "**Target:** t",
        "**Scope:** s",
        "**Constraints:** c",
        "**Completion criteria:** cc",
        "**Risk:** Routine",

        "**Complexity:** Simple",

        "**Reason:** —",
        "**Approach:** a",
        "**Verification:** v",
        "**State:** Ready to implement",
    )
    with pytest.raises(WorkRecordParseError, match="duplicate"):
        parse(text)


def test_empty_field_value_raises() -> None:
    text = _block(
        "**Outcome:**",  # no value
        "**Target:** t",
        "**Scope:** s",
        "**Constraints:** c",
        "**Completion criteria:** cc",
        "**Risk:** Routine",

        "**Complexity:** Simple",

        "**Reason:** —",
        "**Approach:** a",
        "**Verification:** v",
        "**State:** Ready to implement",
    )
    with pytest.raises(WorkRecordParseError, match="empty"):
        parse(text)


def test_no_fields_raises() -> None:
    with pytest.raises(WorkRecordParseError, match="no '\\*\\*Label:\\*\\*'"):
        parse(_block("just some prose, no field headers"))


# ---------------------------------------------------------------------------
# Whitespace tolerance
# ---------------------------------------------------------------------------


def test_field_values_may_span_multiple_lines() -> None:
    text = _block(
        "**Outcome:** first line",
        "  continuation line",
        "  another continuation",
        "**Target:** t",
        "**Scope:** s",
        "**Constraints:** c",
        "**Completion criteria:** cc",
        "**Risk:** Routine",

        "**Complexity:** Simple",

        "**Reason:** —",
        "**Approach:** a",
        "**Verification:** v",
        "**State:** Ready to implement",
    )
    record = parse(text)
    assert "first line" in record["outcome"]
    assert "continuation line" in record["outcome"]
    assert "another continuation" in record["outcome"]


def test_prose_outside_markers_is_ignored() -> None:
    """Notes above and below the marker block must not affect parsing."""
    inner = _block(
        "**Outcome:** o",
        "**Target:** t",
        "**Scope:** s",
        "**Constraints:** c",
        "**Completion criteria:** cc",
        "**Risk:** Routine",

        "**Complexity:** Simple",

        "**Reason:** —",
        "**Approach:** a",
        "**Verification:** v",
        "**State:** Ready to implement",
    )
    text = "# Heading\n\nSome prose with **bold** in it.\n\n" + inner + "\nTrailing notes.\n"
    record: WorkRecord = parse(text)
    assert record["outcome"] == "o"


def test_inline_marker_token_in_prose_is_not_a_marker() -> None:
    """Markers in inline prose must not be treated as block boundaries.

    Real case: a Work Record explained what the markers are and used
    `<!-- agent-workflow:start --> ... :end -->` inline as documentation.
    The parser counted that as a second start marker and rejected the
    file. Markers are line-anchored — only marker tokens that appear on
    their own line bound a block.
    """
    inner = _block(
        "**Outcome:** o",
        "**Target:** t",
        "**Scope:** s",
        "**Constraints:** c",
        "**Completion criteria:** cc",
        "**Risk:** Routine",

        "**Complexity:** Simple",

        "**Reason:** —",
        "**Approach:** a",
        "**Verification:** v",
        "**State:** Ready to implement",
    )
    prose_with_inline_markers = (
        "## Findings\n\n"
        "The marker pair is `<!-- agent-workflow:start -->` ... `<!-- agent-workflow:end -->`. "
        "References like this inline must not bound a block.\n"
    )
    text = inner + "\n" + prose_with_inline_markers
    record = parse(text)
    assert record["outcome"] == "o"


# ---------------------------------------------------------------------------
# Expanded shape — parse_record dispatcher
# ---------------------------------------------------------------------------


from core.work_record import ExpandedWorkRecord, parse_record  # noqa: E402

EXPANDED_PASS = REPO_ROOT / "tests" / "fixtures" / "work-record" / "expanded-pass" / "work-record.md"


def test_expanded_pass_fixture_parses_via_dispatcher() -> None:
    """The expanded fixture parses as the expanded shape and carries the §9.4 fields."""
    parsed = parse_record(EXPANDED_PASS.read_text(encoding="utf-8"))
    assert parsed.shape == "expanded"
    record = parsed.record
    expected_keys = {
        "outcome",
        "target",
        "scope",
        "constraints",
        "completion_criteria",
        "risk",
        "complexity",
        "reason",
        "discovery",
        "material_assumptions",
        "plan",
        "verification_plan",
        "plan_review",
        "approvals",
        "state",
    }
    assert set(record.keys()) == expected_keys
    # Required fields are non-empty; approvals is optional and is
    # populated here as a literal "Not required at this risk level."
    for key, value in record.items():
        if key == "approvals":
            continue
        assert value, f"field {key!r} parsed to empty string"
    assert record["risk"] == "Elevated"
    assert record["complexity"] == "Moderate"


def test_routine_pass_fixture_parses_via_dispatcher() -> None:
    """The routine fixture parses as the routine shape through the dispatcher."""
    parsed = parse_record(ROUTINE_PASS.read_text(encoding="utf-8"))
    assert parsed.shape == "routine"
    # The dispatcher's routine branch returns a plain WorkRecord, with
    # the same keys parse() (legacy) returns.
    assert "approach" in parsed.record  # routine-specific field
    assert "discovery" not in parsed.record  # expanded-only field


def test_legacy_parse_rejects_expanded_input() -> None:
    """parse() (routine-only legacy entry) raises on expanded records.

    Callers that pre-date the expanded shape (today: the checker, the
    local backend) keep working unchanged for routine input but get a
    clear failure when fed an expanded record, instead of silently
    losing the expanded fields.
    """
    text = EXPANDED_PASS.read_text(encoding="utf-8")
    with pytest.raises(WorkRecordParseError, match="expanded shape"):
        parse(text)


def test_shape_mismatch_compact_with_elevated_is_rejected() -> None:
    """A compact record declaring (Elevated, _) is rejected.

    The fields are the compact set, but (Elevated, Simple) demands the
    expanded shape. The dispatcher routes to the expanded validator,
    which finds the expanded-only fields missing.
    """
    text = _block(
        "**Outcome:** o",
        "**Target:** t",
        "**Scope:** s",
        "**Constraints:** c",
        "**Completion criteria:** cc",
        "**Risk:** Elevated",
        "**Complexity:** Simple",
        "**Reason:** something",
        "**Approach:** a",
        "**Verification:** v",
        "**State:** Ready to implement",
    )
    with pytest.raises(WorkRecordParseError, match="expanded-path"):
        parse_record(text)


def test_shape_mismatch_expanded_at_routine_simple_is_rejected() -> None:
    """An expanded-field record declaring (Routine, Simple) is rejected.

    The dispatcher routes to the routine validator. Routine-only fields
    are missing (Approach, Verification) and expanded-only fields are
    unknown (Discovery, etc.) — the validator reports the missing
    fields first, which is enough to reject the record.
    """
    text = _block(
        "**Outcome:** o",
        "**Target:** t",
        "**Scope:** s",
        "**Constraints:** c",
        "**Completion criteria:** cc",
        "**Risk:** Routine",
        "**Complexity:** Simple",
        "**Reason:** —",
        "**Discovery:** d",
        "**Material assumptions:** a",
        "**Plan:** p",
        "**Verification plan:** vp",
        "**Plan review:** self",
        "**Approvals:** —",
        "**State:** Ready to implement",
    )
    with pytest.raises(WorkRecordParseError, match="missing required routine-path field"):
        parse_record(text)


def test_invalid_risk_value_is_rejected() -> None:
    text = _block(
        "**Outcome:** o",
        "**Target:** t",
        "**Scope:** s",
        "**Constraints:** c",
        "**Completion criteria:** cc",
        "**Risk:** SortOfRisky",
        "**Complexity:** Simple",
        "**Reason:** —",
        "**Approach:** a",
        "**Verification:** v",
        "**State:** Ready to implement",
    )
    with pytest.raises(WorkRecordParseError, match="Risk value.*not allowed"):
        parse_record(text)


def test_invalid_complexity_value_is_rejected() -> None:
    text = _block(
        "**Outcome:** o",
        "**Target:** t",
        "**Scope:** s",
        "**Constraints:** c",
        "**Completion criteria:** cc",
        "**Risk:** Routine",
        "**Complexity:** Trivial",
        "**Reason:** —",
        "**Approach:** a",
        "**Verification:** v",
        "**State:** Ready to implement",
    )
    with pytest.raises(WorkRecordParseError, match="Complexity value.*not allowed"):
        parse_record(text)
