"""Tests for the verdict-comment formatter.

The formatter renders the sticky PR comment. The dev-friendly rewrite
serves three render shapes:

- **Clean** — workflow checks passed.
- **Action required** — at least one blocking predicate failed.
- **No Work Records** — PR didn't touch any task file.

Plus action consolidation across records, skip-summarisation by
group, and jargon translation. The tests pin each shape and the
crosscut behaviours.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "format-verdict-comment.py"

# Load the script as a module so we can call format_comment() directly.
# The filename contains '-' which is not a valid Python identifier; use
# importlib.util to bypass the import system's name munging.
_spec = importlib.util.spec_from_file_location("_format_verdict_comment", SCRIPT)
_mod = importlib.util.module_from_spec(_spec)
sys.modules["_format_verdict_comment"] = _mod
_spec.loader.exec_module(_mod)
format_comment = _mod.format_comment


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _pred(name: str, passed: bool = True, blocking: bool = True, detail: str = "ok") -> dict:
    return {"name": name, "passed": passed, "blocking": blocking, "detail": detail}


def _skipped(name: str, detail_reason: str) -> dict:
    """A predicate that passed because it didn't apply (cascade or irrelevance)."""
    return _pred(name, passed=True, blocking=True, detail=f"skipped — {detail_reason}")


def _full_passing_predicates() -> list[dict]:
    """A complete passing-routine predicate list mirroring the real predicate set."""
    return [
        _pred("workrecord.exists", detail="Work Record located at '.agent-workflow/tasks/demo.md'."),
        _pred("workrecord.markers_present", detail="marker pair found, single block."),
        _pred("risk.declared", detail="Risk = 'Routine'."),
        _pred("complexity.declared", detail="Complexity = 'Simple'."),
        _pred("workrecord.shape_matches_classification", detail="routine shape matches the declared classification."),
        _pred("workrecord.routine_fields_present", detail="all required routine-path fields present and non-empty."),
        _pred("workrecord.state_valid", detail="state 'Ready for review' is valid."),
        _skipped("risk.redline_findings_available", "redline verdict missing (advisory — redline: optional)."),
        _skipped("risk.boundary_violation_absent", "redline verdict unavailable."),
        _skipped("risk.declared_not_below_detected", "redline verdict unavailable."),
    ]


def _record(slug: str, status: str = "clean", predicates: list[dict] | None = None) -> dict:
    return {
        "slug": slug,
        "status": status,
        "exit_code": 0 if status == "clean" else 2,
        "predicates": predicates or _full_passing_predicates(),
    }


# ---------------------------------------------------------------------------
# Clean shape
# ---------------------------------------------------------------------------


def test_clean_single_record_renders_headline_scope_and_audit_details() -> None:
    """Clean single-record: headline, scope line, one record-line, audit collapsed."""
    verdict = {
        "status": "clean",
        "exit_code": 0,
        "records": [_record("demo", "clean")],
    }
    out = format_comment(verdict)
    assert "Workflow checks passed — 1 task file" in out
    assert "**Scope:**" in out
    assert "1 Routine" in out
    # Record line shows slug, risk, state
    assert "[`demo`]" in out
    assert "Risk: Routine" in out
    assert "State: Ready for review" in out
    # Audit detail collapsed in a <details>
    assert "<details>" in out
    assert "Audit detail" in out


def test_clean_multi_record_lists_each_record() -> None:
    verdict = {
        "status": "clean",
        "exit_code": 0,
        "records": [_record(slug, "clean") for slug in ("task-a", "task-b", "task-c")],
    }
    out = format_comment(verdict)
    assert "Workflow checks passed — 3 task files" in out
    assert "[`task-a`]" in out
    assert "[`task-b`]" in out
    assert "[`task-c`]" in out
    assert "3 Routine" in out


def test_clean_headline_never_says_action_required() -> None:
    """Regression guard against headlines that imply action when there's none."""
    verdict = {"status": "clean", "exit_code": 0, "records": [_record("demo")]}
    out = format_comment(verdict)
    assert "Action required" not in out


# ---------------------------------------------------------------------------
# Action-required shape
# ---------------------------------------------------------------------------


def _failing_review_predicate(checkpoint_id: str = "architecture-review", satisfy: str = "CODEOWNER approval, label `architecture-reviewed`") -> dict:
    """Real-shape failing review.checkpoints_satisfied detail."""
    return _pred(
        "review.checkpoints_satisfied",
        passed=False,
        blocking=True,
        detail=f"unsatisfied checkpoint '{checkpoint_id}' — red-zone change: src/.../X.java; satisfy by: {satisfy}",
    )


def _failing_risk_too_low() -> dict:
    return _pred(
        "risk.declared_not_below_detected",
        passed=False,
        blocking=True,
        detail="declared 'Routine' is below detected 'Elevated'; raise the Work Record's Risk to at least 'Elevated'.",
    )


def _failing_missing_fields(fields: str = "Outcome, Plan") -> dict:
    return _pred(
        "workrecord.expanded_fields_present",
        passed=False,
        blocking=True,
        detail=f"Work Record block is missing required expanded-path field(s): {fields}",
    )


def test_action_required_single_record_headline_names_the_action() -> None:
    """Single blocking action: the headline names what to do."""
    preds = _full_passing_predicates() + [_failing_review_predicate()]
    verdict = {
        "status": "blocking",
        "exit_code": 2,
        "records": [_record("demo", "blocking", preds)],
    }
    out = format_comment(verdict)
    # Headline names the architecture-review action in plain prose
    assert "Action required: Get an architecture review on this PR" in out
    assert "**Why:**" in out
    assert "**How:**" in out


def test_action_required_consolidates_same_action_across_records() -> None:
    """Two records, same blocking predicate + same satisfy options → one action block."""
    preds_a = _full_passing_predicates() + [_failing_review_predicate()]
    preds_b = _full_passing_predicates() + [_failing_review_predicate()]
    verdict = {
        "status": "blocking",
        "exit_code": 2,
        "records": [
            _record("task-a", "blocking", preds_a),
            _record("task-b", "blocking", preds_b),
        ],
    }
    out = format_comment(verdict)
    # One consolidated action block — affects both records
    assert "**Affects:**" in out
    assert "`task-a`" in out
    assert "`task-b`" in out
    # Architecture-review action appears only once (as the action headline)
    assert out.count("Get an architecture review on this PR") == 1
    # Headline reflects "N of M" since multiple records are blocking
    assert "Action required on 2 of 2 task files" in out


def test_action_required_different_actions_per_record_renders_separate_blocks() -> None:
    """Different blocking predicates → separate action blocks, headline aggregates."""
    preds_a = _full_passing_predicates() + [_failing_review_predicate()]
    preds_b = _full_passing_predicates() + [_failing_risk_too_low()]
    verdict = {
        "status": "blocking",
        "exit_code": 2,
        "records": [
            _record("task-a", "blocking", preds_a),
            _record("task-b", "blocking", preds_b),
        ],
    }
    out = format_comment(verdict)
    # Headline says 2 of 2
    assert "Action required on 2 of 2 task files" in out
    # Both action blocks present
    assert "Get an architecture review on this PR" in out
    assert "Bump Risk in the task file from `Routine` to `Elevated`" in out
    # Each action block lists only its own record (no "Affects:" since
    # each bucket has one record).
    assert "**Affects:**" not in out


def test_missing_fields_action_names_specific_fields() -> None:
    preds = _full_passing_predicates() + [_failing_missing_fields("Outcome, Plan")]
    verdict = {
        "status": "blocking",
        "exit_code": 2,
        "records": [_record("demo", "blocking", preds)],
    }
    out = format_comment(verdict)
    assert "Fill missing fields in the task file: `Outcome`, `Plan`" in out


def test_missing_fields_does_not_consolidate_when_fields_differ() -> None:
    """Two records missing different fields → separate action blocks (different signature)."""
    preds_a = _full_passing_predicates() + [_failing_missing_fields("Outcome")]
    preds_b = _full_passing_predicates() + [_failing_missing_fields("Plan")]
    verdict = {
        "status": "blocking",
        "exit_code": 2,
        "records": [
            _record("task-a", "blocking", preds_a),
            _record("task-b", "blocking", preds_b),
        ],
    }
    out = format_comment(verdict)
    # Each missing-field set gets its own action block
    assert "Fill missing fields in the task file: `Outcome`" in out
    assert "Fill missing fields in the task file: `Plan`" in out
    assert "**Affects:**" not in out  # neither bucket has >1 record


# ---------------------------------------------------------------------------
# Audit detail (groups, skips)
# ---------------------------------------------------------------------------


def test_audit_block_groups_by_concern() -> None:
    """Predicates from same first-segment cluster together as one group line."""
    verdict = {
        "status": "clean",
        "exit_code": 0,
        "records": [_record("demo")],
    }
    out = format_comment(verdict)
    # Group names appear in the audit detail
    assert "**Work Record structure**" in out
    assert "**Risk classification**" in out


def test_audit_block_skip_summarisation_collapses_irrelevant_groups() -> None:
    """All-skipped group renders as one summary line, not N rows.

    Plan approvals on a Routine record is the cleanest example: all three
    approval predicates skip with "only applies at Risk=…" details.
    """
    preds = _full_passing_predicates() + [
        _skipped("approval.elevated_clean_context_review_present", "only applies at Risk=Elevated (record is Risk='Routine')."),
        _skipped("approval.high_risk_approval_recorded", "only applies at Risk=High (record is Risk='Routine')."),
        _skipped("approval.clean_context_does_not_satisfy_human", "only applies at Risk=High (record is Risk='Routine')."),
    ]
    verdict = {
        "status": "clean",
        "exit_code": 0,
        "records": [_record("demo", "clean", preds)],
    }
    out = format_comment(verdict)
    # The Plan approvals group renders as one "skipped" line — not three rows.
    assert "**Plan approvals** — skipped" in out
    # And the individual predicate names don't appear in the audit
    # block (they collapsed).
    audit_section = out.split("<details>", 1)[-1]
    assert "approval.elevated_clean_context_review_present" not in audit_section


def test_audit_block_failing_group_expands_inline() -> None:
    """A group with a failing predicate expands inline so the failing row is visible."""
    preds = _full_passing_predicates() + [_failing_review_predicate()]
    verdict = {
        "status": "blocking",
        "exit_code": 2,
        "records": [_record("demo", "blocking", preds)],
    }
    out = format_comment(verdict)
    # Required reviews group expands; the failing row visible
    assert "**Required reviews**" in out
    assert "`review.checkpoints_satisfied`" in out


# ---------------------------------------------------------------------------
# Jargon translation
# ---------------------------------------------------------------------------


def test_jargon_predicate_word_not_in_headline_or_action() -> None:
    """The word 'predicate' must not appear anywhere visible to the developer.

    Allowed in the audit-detail `<details>` block where dotted predicate
    names are surfaced for greppability, but never in headlines, action
    blocks, or scope lines.
    """
    preds = _full_passing_predicates() + [_failing_review_predicate()]
    verdict = {
        "status": "blocking",
        "exit_code": 2,
        "records": [_record("demo", "blocking", preds)],
    }
    out = format_comment(verdict)
    # Split into "above the details" and "inside the details" — the
    # word `predicate` is allowed inside the audit block (it's used as
    # a column header / context label). Above the block, it must be
    # absent.
    above = out.split("<details>", 1)[0]
    assert "predicate" not in above.lower()


def test_jargon_satisfy_by_translated_to_to_fix_this() -> None:
    preds = _full_passing_predicates() + [_failing_review_predicate()]
    verdict = {
        "status": "blocking",
        "exit_code": 2,
        "records": [_record("demo", "blocking", preds)],
    }
    out = format_comment(verdict)
    # The action block reproduces the satisfy-by options as "To fix this: ..."
    assert "To fix this:" in out


def test_jargon_marker_block_translated() -> None:
    """`marker block` is translated to plain prose."""
    fail = _pred(
        "workrecord.markers_present",
        passed=False,
        blocking=True,
        detail="marker block malformed: unterminated start marker",
    )
    preds = _full_passing_predicates()[:1] + [fail] + _full_passing_predicates()[2:]
    verdict = {
        "status": "blocking",
        "exit_code": 2,
        "records": [_record("demo", "blocking", preds)],
    }
    out = format_comment(verdict)
    assert "marker block" not in out
    assert "structured block in the task file" in out


# ---------------------------------------------------------------------------
# No-records advisory
# ---------------------------------------------------------------------------


def test_no_records_renders_one_line_advisory() -> None:
    verdict = {"status": "clean", "exit_code": 0, "records": []}
    out = format_comment(verdict)
    assert "No task file changed in this PR" in out
    # No audit `<details>` for the empty case
    assert "<details>" not in out


# ---------------------------------------------------------------------------
# Headlines
# ---------------------------------------------------------------------------


def test_advisory_headline_says_non_blocking_findings() -> None:
    """A pure advisory verdict surfaces clearly without claiming action required."""
    advisory_pred = _pred(
        "risk.redline_findings_available",
        passed=False,
        blocking=False,
        detail="redline verdict missing (advisory — redline: optional).",
    )
    preds = _full_passing_predicates()[:-1] + [advisory_pred]
    verdict = {
        "status": "advisory",
        "exit_code": 1,
        "records": [_record("demo", "advisory", preds)],
    }
    out = format_comment(verdict)
    assert "Advisory: workflow checks have non-blocking findings" in out
    assert "Action required" not in out


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------


def test_footer_renders_when_commit_sha_in_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENT_WORKFLOW_COMMIT_SHA", "abcdef1234567890")
    verdict = {"status": "clean", "exit_code": 0, "records": [_record("demo")]}
    out = format_comment(verdict)
    assert "abcdef12" in out


def test_footer_omits_when_no_commit_sha(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AGENT_WORKFLOW_COMMIT_SHA", raising=False)
    monkeypatch.delenv("GITHUB_SHA", raising=False)
    verdict = {"status": "clean", "exit_code": 0, "records": [_record("demo")]}
    out = format_comment(verdict)
    assert "Updated against commit" not in out


# ---------------------------------------------------------------------------
# Effective rules (preserved through the rewrite)
# ---------------------------------------------------------------------------


def test_effective_rules_render_inside_audit_block() -> None:
    """Effective-rules block survives the rewrite — nested under audit detail."""
    rec = _record("demo")
    rec["effective_rules"] = [
        {"name": "workrecord.exists", "source": "core"},
        {"name": "risk.boundary_violation_absent", "source": "default"},
    ]
    verdict = {"status": "clean", "exit_code": 0, "records": [rec]}
    out = format_comment(verdict)
    assert "Effective rules" in out
    assert "`workrecord.exists`" in out
    assert "`core`" in out
    assert "`default`" in out
