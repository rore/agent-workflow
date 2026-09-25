"""Structural agent-review gates; these attest evidence, not review quality."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.checker import run_checker


PLAN_AGENT = "Agent technical review: session/plan-123"
RESULT_AGENT = (
    "## Result review\n"
    "Agent technical review: session/result-456\n"
    "Reviewed revision: abc1234\n"
    "Verification adequacy: concurrent and boundary checks cover the criteria.\n"
)
HUMAN_APPROVAL = 'Approved by user 2026-09-25: "Proceed with this plan."'


def _predicates(
    tmp_path: Path,
    *,
    risk: str,
    state: str = "Ready to implement",
    plan_review: str = PLAN_AGENT,
    result_review: str = "",
) -> dict[str, bool]:
    (tmp_path / "agent-workflow.yaml").write_text(
        'version: 1\nproject:\n  name: review-test\n'
        'workRecord:\n  backend: local\n  local:\n'
        '    taskPath: ".agent-workflow/tasks/{slug}.md"\nredline: optional\n',
        encoding="utf-8",
    )
    tasks = tmp_path / ".agent-workflow" / "tasks"
    tasks.mkdir(parents=True, exist_ok=True)
    baseline = json.dumps({
        "source": "test-fixture-initial",
        "outcome": "Review the change.",
        "scope": "One code change.",
        "constraints": "Preserve existing behavior.",
        "completion_criteria": "The review gates distinguish evidence.",
    })
    record = (
        "<!-- agent-workflow:start -->\n"
        "**Outcome:** Review the change.\n\n"
        "**Target:** review-test.\n\n"
        "**Scope:** One code change.\n\n"
        "**Constraints:** Preserve existing behavior.\n\n"
        "**Completion criteria:** The review gates distinguish evidence.\n\n"
        f"**Requirement baseline:** {baseline}\n\n"
        f"**Risk:** {risk}\n\n"
        "**Complexity:** Moderate\n\n"
        "**Reason:** Focused review test.\n\n"
        "**Discovery:** Existing record.\n\n"
        "**Material assumptions:** None.\n\n"
        "**Plan:** Apply a focused change.\n\n"
        "**Verification plan:** Review gates distinguish evidence → checker test.\n\n"
        f"**Plan review:** {plan_review}\n\n"
        f"**Approvals:** {HUMAN_APPROVAL if risk == 'High' else 'Not required'}\n\n"
        "**Exceptions:** —\n\n"
        f"**State:** {state}\n"
        "<!-- agent-workflow:end -->\n\n"
        f"{result_review}"
    )
    (tasks / "task.md").write_text(record, encoding="utf-8")
    verdict = run_checker(tmp_path, "task").to_dict()
    return {p["name"]: p["passed"] for p in verdict["records"][0]["predicates"]}


@pytest.mark.parametrize("risk", ["Elevated", "High"])
def test_agent_plan_review_is_separate_from_human_approval(tmp_path: Path, risk: str) -> None:
    name = (
        "approval.elevated_clean_context_review_present"
        if risk == "Elevated" else "approval.high_clean_context_review_present"
    )
    assert _predicates(tmp_path, risk=risk)[name]
    assert not _predicates(
        tmp_path, risk=risk, plan_review=HUMAN_APPROVAL
    )[name]


@pytest.mark.parametrize("risk", ["Elevated", "High"])
def test_agent_result_review_requires_revision_and_adequacy(tmp_path: Path, risk: str) -> None:
    name = "review.agent_result_review_present"
    assert _predicates(
        tmp_path, risk=risk, state="Ready for review", result_review=RESULT_AGENT
    )[name]
    assert not _predicates(
        tmp_path, risk=risk, state="Ready for review",
        result_review="## Result review\nHuman review: approved.\nLabel: architecture-reviewed.\n",
    )[name]
    assert not _predicates(
        tmp_path, risk=risk, state="Ready for review",
        result_review=RESULT_AGENT.replace("abc1234", "pending"),
    )[name]
    assert not _predicates(
        tmp_path, risk=risk, state="Ready for review",
        result_review=RESULT_AGENT.replace("Verification adequacy:", "Notes:"),
    )[name]


def test_result_review_gate_waits_for_ready_state(tmp_path: Path) -> None:
    assert _predicates(tmp_path, risk="High")["review.agent_result_review_present"]


def test_routine_path_does_not_require_agent_review(tmp_path: Path) -> None:
    checks = _predicates(
        tmp_path, risk="Routine", state="Ready for review",
        plan_review="self", result_review="",
    )
    assert checks["approval.elevated_clean_context_review_present"]
    assert checks["approval.high_clean_context_review_present"]
    assert checks["review.agent_result_review_present"]


def test_legacy_plan_reference_is_parseable_but_not_sufficient(tmp_path: Path) -> None:
    checks = _predicates(
        tmp_path, risk="Elevated", plan_review="Clean-context review <link>",
    )
    assert checks["workrecord.expanded_fields_present"]
    assert not checks["approval.elevated_clean_context_review_present"]

@pytest.mark.parametrize("risk", ["Elevated", "High"])
def test_dotted_ready_state_still_requires_result_review(tmp_path: Path, risk: str) -> None:
    name = "review.agent_result_review_present"
    assert not _predicates(tmp_path, risk=risk, state="Ready for review.")[name]
    assert _predicates(
        tmp_path, risk=risk, state="Ready for review.", result_review=RESULT_AGENT
    )[name]


@pytest.mark.parametrize("risk", ["Elevated", "High"])
@pytest.mark.parametrize("reference", [
    "[review](https://example.com/review/123)",
    "<https://example.com/review/123>",
])
def test_markdown_review_links_are_valid_evidence(
    tmp_path: Path, risk: str, reference: str
) -> None:
    checks = _predicates(
        tmp_path,
        risk=risk,
        state="Ready for review",
        plan_review=f"Agent technical review: {reference}",
        result_review=RESULT_AGENT.replace("session/result-456", reference),
    )
    plan = (
        "approval.elevated_clean_context_review_present"
        if risk == "Elevated" else "approval.high_clean_context_review_present"
    )
    assert checks[plan]
    assert checks["review.agent_result_review_present"]


@pytest.mark.parametrize("risk", ["Elevated", "High"])
@pytest.mark.parametrize("reference", ["[pending]", "<source ref>"])
def test_placeholder_review_links_are_not_evidence(
    tmp_path: Path, risk: str, reference: str
) -> None:
    checks = _predicates(
        tmp_path,
        risk=risk,
        state="Ready for review",
        plan_review=f"Agent technical review: {reference}",
        result_review=RESULT_AGENT.replace("session/result-456", reference),
    )
    plan = (
        "approval.elevated_clean_context_review_present"
        if risk == "Elevated" else "approval.high_clean_context_review_present"
    )
    assert not checks[plan]
    assert not checks["review.agent_result_review_present"]


def test_agent_review_rules_report_core_provenance(tmp_path: Path) -> None:
    _predicates(tmp_path, risk="High", state="Ready for review", result_review=RESULT_AGENT)
    rules = {
        item["name"]: item["source"]
        for item in run_checker(tmp_path, "task").to_dict()["records"][0]["effective_rules"]
    }
    assert rules["approval.high_clean_context_review_present"] == "core"
    assert rules["review.agent_result_review_present"] == "core"

def test_new_review_gates_use_existing_exception_path(tmp_path: Path) -> None:
    _predicates(
        tmp_path, risk="High", state="Ready for review", plan_review="—"
    )
    path = tmp_path / ".agent-workflow" / "tasks" / "task.md"
    record = path.read_text(encoding="utf-8")
    exceptions = (
        "**Exceptions:**\n"
        "- rule: approval.high_clean_context_review_present\n"
        "  reason: fixture waiver\n"
        "  scope: this task\n"
        "  approver: fixture owner\n"
        "  expiry: 2099-12-31\n"
        "  compensating_validation: manual review\n"
        "- rule: review.agent_result_review_present\n"
        "  reason: fixture waiver\n"
        "  scope: this task\n"
        "  approver: fixture owner\n"
        "  expiry: 2099-12-31\n"
        "  compensating_validation: manual review"
    )
    path.write_text(record.replace("**Exceptions:** —", exceptions), encoding="utf-8")
    predicates = {
        item["name"]: item
        for item in run_checker(tmp_path, "task").to_dict()["records"][0]["predicates"]
    }
    for name in (
        "approval.high_clean_context_review_present",
        "review.agent_result_review_present",
    ):
        assert not predicates[name]["passed"]
        assert not predicates[name]["blocking"]