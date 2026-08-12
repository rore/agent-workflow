"""Tests for the slice-F Exceptions sub-parser.

The Exceptions field of an expanded Work Record carries zero or more
structured exception entries per SPEC §11. parse_exceptions() decodes
the field's free-text into a list of ExceptionEntry; the checker
predicates then validate content.

This file exercises only structural parsing — empty / well-formed /
malformed cases. Validation against the non-waivable set and expiry-
in-past lives in the checker tests.
"""

from __future__ import annotations

import pytest

from core.work_record import ExceptionEntry, WorkRecordParseError, parse_exceptions


def test_empty_input_returns_empty_list() -> None:
    assert parse_exceptions("") == []
    assert parse_exceptions("   ") == []


def test_dash_only_input_returns_empty_list() -> None:
    """The agent writes ``—`` (em-dash) when explicitly declaring no exceptions."""
    assert parse_exceptions("—") == []
    assert parse_exceptions("  —  ") == []


def test_alternative_none_sentinels_return_empty_list() -> None:
    """Hyphen / 'None' / 'N/A' are accepted alongside em-dash.

    Agents on keyboards without an em-dash key commonly type ``-``,
    ``None``, or ``N/A``. The parser accepts all of these as
    semantically equivalent to "no exceptions recorded" so Work
    Records don't get rejected over a punctuation typo. The template
    canonical is still ``—``.
    """
    for sentinel in ("-", "--", "None", "none", "NONE", "N/A", "n/a", "NA", "na"):
        assert parse_exceptions(sentinel) == [], (
            f"sentinel {sentinel!r} should parse as no exceptions"
        )
        # Surrounding whitespace tolerated too.
        assert parse_exceptions(f"  {sentinel}  ") == [], (
            f"sentinel {sentinel!r} with whitespace should parse as no exceptions"
        )


def test_one_exception_with_all_fields() -> None:
    text = (
        "- rule: risk.declared_not_below_detected\n"
        "  reason: temporary deviation pending refactor\n"
        "  scope: this PR only\n"
        "  approver: I123456\n"
        "  expiry: 2026-12-31\n"
        "  compensating_validation: manual smoke run on staging\n"
    )
    result = parse_exceptions(text)
    assert result == [
        ExceptionEntry(
            rule="risk.declared_not_below_detected",
            reason="temporary deviation pending refactor",
            scope="this PR only",
            approver="I123456",
            compensating_validation="manual smoke run on staging",
            expiry="2026-12-31",
        )
    ]


def test_one_exception_without_expiry() -> None:
    """Expiry is optional; absent → expiry is None."""
    text = (
        "- rule: workrecord.expanded_fields_present\n"
        "  reason: experimental field intentionally blank for now\n"
        "  scope: this slice\n"
        "  approver: I123456\n"
        "  compensating_validation: review by another engineer\n"
    )
    result = parse_exceptions(text)
    assert len(result) == 1
    assert result[0].expiry is None


def test_multiple_exceptions() -> None:
    text = (
        "- rule: rule.a\n"
        "  reason: r1\n"
        "  scope: s1\n"
        "  approver: a1\n"
        "  compensating_validation: c1\n"
        "- rule: rule.b\n"
        "  reason: r2\n"
        "  scope: s2\n"
        "  approver: a2\n"
        "  expiry: 2027-01-01\n"
        "  compensating_validation: c2\n"
    )
    result = parse_exceptions(text)
    assert len(result) == 2
    assert result[0].rule == "rule.a"
    assert result[0].expiry is None
    assert result[1].rule == "rule.b"
    assert result[1].expiry == "2027-01-01"


def test_missing_required_subfield_raises() -> None:
    """An exception without a required sub-field is a parse error."""
    text = (
        "- rule: rule.a\n"
        "  reason: r\n"
        # scope missing
        "  approver: a\n"
        "  compensating_validation: c\n"
    )
    with pytest.raises(WorkRecordParseError, match="missing required sub-field"):
        parse_exceptions(text)


def test_missing_required_subfield_names_missing_one() -> None:
    """The error message names which sub-field is missing."""
    text = (
        "- rule: rule.a\n"
        "  reason: r\n"
        "  scope: s\n"
        "  approver: a\n"
        # compensating_validation missing
    )
    with pytest.raises(WorkRecordParseError, match="compensating_validation"):
        parse_exceptions(text)


def test_unknown_subfield_raises() -> None:
    """Typo-resistant: unknown sub-field names are rejected."""
    text = (
        "- rule: rule.a\n"
        "  reasn: r\n"  # typo
        "  scope: s\n"
        "  approver: a\n"
        "  compensating_validation: c\n"
    )
    with pytest.raises(WorkRecordParseError, match="unknown sub-field"):
        parse_exceptions(text)


def test_continuation_before_first_entry_raises() -> None:
    """A sub-field line before any '- key' header is malformed."""
    text = (
        "  reason: rogue continuation\n"
        "- rule: rule.a\n"
        "  scope: s\n"
        "  approver: a\n"
        "  compensating_validation: c\n"
    )
    with pytest.raises(WorkRecordParseError, match="before any '- key"):
        parse_exceptions(text)


def test_duplicate_subfield_in_one_entry_raises() -> None:
    text = (
        "- rule: rule.a\n"
        "  reason: r\n"
        "  reason: r2\n"
        "  scope: s\n"
        "  approver: a\n"
        "  compensating_validation: c\n"
    )
    with pytest.raises(WorkRecordParseError, match="duplicate sub-field"):
        parse_exceptions(text)


def test_expanded_record_with_exceptions_round_trips() -> None:
    """An expanded record carrying an Exceptions block renders + re-parses identically."""
    from core.work_record import parse_record, render_record

    text = (
        "<!-- agent-workflow:start -->\n"
        "**Outcome:** o\n\n"
        "**Target:** t\n\n"
        "**Scope:** s\n\n"
        "**Constraints:** c\n\n"
        "**Completion criteria:** cc\n\n"
        "**Risk:** Elevated\n\n"
        "**Complexity:** Moderate\n\n"
        "**Reason:** r\n\n"
        "**Discovery:** d\n\n"
        "**Material assumptions:** m\n\n"
        "**Plan:** p\n\n"
        "**Verification plan:** vp\n\n"
        "**Plan review:** pr\n\n"
        "**Approvals:** —\n\n"
        "**Exceptions:**\n"
        "- rule: rule.a\n"
        "  reason: r\n"
        "  scope: s\n"
        "  approver: a\n"
        "  compensating_validation: c\n"
        "\n"
        "**State:** Ready for review\n"
        "<!-- agent-workflow:end -->\n"
    )
    parsed = parse_record(text)
    assert parsed.shape == "expanded"
    rendered = render_record(parsed)
    re_parsed = parse_record(rendered)
    assert parsed.record == re_parsed.record


def test_expanded_record_without_exceptions_field_parses_unchanged() -> None:
    """Legacy expanded records (no Exceptions field) still parse cleanly."""
    from core.work_record import parse_record

    text = (
        "<!-- agent-workflow:start -->\n"
        "**Outcome:** o\n\n"
        "**Target:** t\n\n"
        "**Scope:** s\n\n"
        "**Constraints:** c\n\n"
        "**Completion criteria:** cc\n\n"
        "**Risk:** Elevated\n\n"
        "**Complexity:** Moderate\n\n"
        "**Reason:** r\n\n"
        "**Discovery:** d\n\n"
        "**Material assumptions:** m\n\n"
        "**Plan:** p\n\n"
        "**Verification plan:** vp\n\n"
        "**Plan review:** pr\n\n"
        "**Approvals:** —\n\n"
        "**State:** Ready for review\n"
        "<!-- agent-workflow:end -->\n"
    )
    parsed = parse_record(text)
    assert parsed.shape == "expanded"
    assert "exceptions" not in parsed.record  # not set when absent
