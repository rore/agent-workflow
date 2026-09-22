"""Behavioral requirement integrity: task baselines and repository contracts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.checker import run_checker
from core.checker.checker import main


_CONTEXT = {
    "outcome": "Automatically wake an unloaded recipient.",
    "scope": "Loaded and unloaded recipients.",
    "constraints": "Recipient workspace remains unchanged.",
    "completion_criteria": "An unloaded recipient wakes without manual resume.",
}


def _record(
    *,
    context: dict[str, str] | None = None,
    changes: list[dict[str, object]] | None = None,
    verification: str = "focused unit tests",
    baseline: bool = True,
) -> str:
    current = dict(_CONTEXT if context is None else context)
    lines = [
        "<!-- agent-workflow:start -->",
        f"**Outcome:** {current['outcome']}",
        "**Target:** relay",
        f"**Scope:** {current['scope']}",
        f"**Constraints:** {current['constraints']}",
        f"**Completion criteria:** {current['completion_criteria']}",
    ]
    if baseline:
        value = {"source": "task-request@initial", **_CONTEXT}
        lines.append(
            "**Requirement baseline:** "
            + json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        )
    lines.extend([
        "**Risk:** Routine",
        "**Complexity:** Simple",
        "**Reason:** Local and reversible.",
        "**Approach:** Preserve the required behavior.",
        f"**Verification:** {verification}",
    ])
    if changes is not None:
        lines.append(
            "**Behavior changes:** "
            + json.dumps(changes, ensure_ascii=False, separators=(",", ":"))
        )
    lines.extend(["**State:** Ready for review", "<!-- agent-workflow:end -->", ""])
    return "\n\n".join(lines)


def _repo(tmp_path: Path, *, task_path: str = ".agent-workflow/tasks/{slug}.md") -> Path:
    (tmp_path / "agent-workflow.yaml").write_text(
        "version: 1\n"
        "project: {name: relay}\n"
        "workRecord:\n"
        "  backend: local\n"
        "  local:\n"
        f'    taskPath: "{task_path}"\n'
        "redline: optional\n",
        encoding="utf-8",
    )
    return tmp_path


def _write_record(repo: Path, relative: str, text: str) -> None:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _predicate(payload: dict, name: str) -> dict:
    return next(
        predicate
        for record in payload["records"]
        for predicate in record["predicates"]
        if predicate["name"] == name
    )


def _task_change(target: str, before: str, after: str, *, approved: bool = False) -> dict[str, object]:
    change: dict[str, object] = {
        "target": target,
        "classification": "requirement-change",
        "before": before,
        "after": after,
        "reason": "The original behavior is not currently implementable.",
        "impact": "The product commitment changes.",
        "alternatives": "Keep the task blocked while investigating.",
        "authority": {"scope": "task", "name": "task-owner"},
    }
    if approved:
        change["approval"] = {
            "by": "user",
            "reference": "conversation:approval-1",
            "verbatim": "I approve this exact change.",
        }
    return change


def test_legacy_record_remains_parseable_but_cannot_advance(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    _write_record(repo, ".agent-workflow/tasks/demo.md", _record(baseline=False))
    verdict = run_checker(repo, "demo").to_dict()
    assert _predicate(verdict, "requirements.baseline_present")["passed"] is False
    assert verdict["status"] == "blocking"


@pytest.mark.parametrize(
    "target,before,after",
    [
        (
            "task-context.completion_criteria",
            _CONTEXT["completion_criteria"],
            "Delivery waits until the recipient is manually resumed.",
        ),
        (
            "task-context.scope",
            _CONTEXT["scope"],
            "Loaded recipients only.",
        ),
        (
            "task-context.constraints",
            _CONTEXT["constraints"],
            "Recipient workspace should normally remain unchanged.",
        ),
        (
            "task-context.outcome",
            _CONTEXT["outcome"],
            "Wake unloaded recipients on Windows and Linux.",
        ),
    ],
)
def test_pr167_erosion_and_broader_obligations_block_without_approval(
    tmp_path: Path, target: str, before: str, after: str
) -> None:
    repo = _repo(tmp_path)
    _write_record(
        repo,
        ".agent-workflow/tasks/demo.md",
        _record(changes=[_task_change(target, before, after)]),
    )
    verdict = run_checker(repo, "demo").to_dict()
    assert _predicate(verdict, "requirements.requirement_changes_authorized")["passed"] is False
    assert verdict["status"] == "blocking"


def test_exact_approved_task_change_advances_chain_without_shape_migration(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    current = dict(_CONTEXT)
    current["scope"] = "Loaded recipients only."
    change = _task_change(
        "task-context.scope", _CONTEXT["scope"], current["scope"], approved=True
    )
    _write_record(repo, ".agent-workflow/tasks/demo.md", _record(context=current, changes=[change]))
    verdict = run_checker(repo, "demo").to_dict()
    for name in (
        "requirements.baseline_present",
        "requirements.behavior_changes_well_formed",
        "requirements.task_context_traceable",
        "requirements.requirement_changes_authorized",
    ):
        assert _predicate(verdict, name)["passed"] is True
    assert _predicate(verdict, "workrecord.shape_matches_classification")["passed"] is True


def test_equivalent_task_refinement_needs_no_human_approval(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    current = dict(_CONTEXT)
    current["scope"] = "Loaded recipients and unloaded recipients."
    change = {
        "target": "task-context.scope",
        "classification": "equivalent",
        "before": _CONTEXT["scope"],
        "after": current["scope"],
        "reason": "Terminology-only clarification.",
    }
    _write_record(repo, ".agent-workflow/tasks/demo.md", _record(context=current, changes=[change]))
    verdict = run_checker(repo, "demo").to_dict()
    assert _predicate(verdict, "requirements.task_context_traceable")["passed"] is True
    assert _predicate(verdict, "requirements.requirement_changes_authorized")["passed"] is True


@pytest.mark.parametrize("tamper", ["before", "final", "order"])
def test_task_change_chain_tampering_blocks(tmp_path: Path, tamper: str) -> None:
    repo = _repo(tmp_path)
    current = dict(_CONTEXT)
    if tamper == "before":
        changes = [{
            "target": "task-context.scope",
            "classification": "equivalent",
            "before": "Different scope.",
            "after": _CONTEXT["scope"],
            "reason": "Tampered start.",
        }]
    elif tamper == "final":
        changes = [{
            "target": "task-context.scope",
            "classification": "equivalent",
            "before": _CONTEXT["scope"],
            "after": "Clarified scope.",
            "reason": "Clarification not reflected in current context.",
        }]
    else:
        current["scope"] = "Final scope."
        changes = [
            {
                "target": "task-context.scope",
                "classification": "equivalent",
                "before": "Intermediate scope.",
                "after": "Final scope.",
                "reason": "Second change placed first.",
            },
            {
                "target": "task-context.scope",
                "classification": "equivalent",
                "before": _CONTEXT["scope"],
                "after": "Intermediate scope.",
                "reason": "First change placed second.",
            },
        ]
    _write_record(repo, ".agent-workflow/tasks/demo.md", _record(context=current, changes=changes))
    verdict = run_checker(repo, "demo").to_dict()
    assert _predicate(verdict, "requirements.task_context_traceable")["passed"] is False


def _contract_config(
    repo: Path,
    *,
    pattern: str,
    task_path: str = ".agent-workflow/tasks/{slug}.md",
    applicability: bool = False,
) -> None:
    app = (
        "applicability:\n"
        "  documentationOnly:\n"
        "    paths: [contracts/]\n"
        "    workflowRequired: false\n"
        "    directDefaultBranchAllowed: false\n"
        if applicability
        else ""
    )
    (repo / "agent-redline-policy.yaml").write_text(
        "version: 1\nproject: {name: relay}\n"
        "zones:\n  blue:\n    - path: src/**\n      reason: source\n"
        "behaviorContracts:\n"
        f"  paths: [{pattern}]\n"
        "  verification: relay-behavior-contracts\n"
        "  checkpoint: behavior-review\n"
        "checkpoints:\n  behavior-review:\n"
        "    satisfiedBy: [codeownerApproval]\n",
        encoding="utf-8",
    )
    (repo / "agent-workflow.yaml").write_text(
        "version: 1\nproject: {name: relay}\n"
        "workRecord:\n  backend: local\n  local:\n"
        f'    taskPath: "{task_path}"\n'
        "redline: required\n"
        "redlineVerdictPath: build/redline-verdict.json\n"
        f"{app}",
        encoding="utf-8",
    )


def _write_contract_redline(
    repo: Path,
    contract_paths: list[str],
    *,
    owners: list[str] | None = None,
    red_paths: list[str] | None = None,
) -> None:
    owners = ["@relay-owners"] if owners is None else owners
    red_paths = contract_paths if red_paths is None else red_paths
    payload = {
        "verdict": "RED" if contract_paths else "BLUE",
        "summary": "Behavior contract changed." if contract_paths else "No contract changed.",
        "zones": {
            "blue": [],
            "gray": [],
            "red": red_paths,
            "watch": [],
        },
        "boundaryViolations": [],
        "checkpoints": (
            [
                {
                    "id": "behavior-review",
                    "reason": f"Behavior contract changed: {contract_paths[0]}",
                    "satisfied": True,
                    "satisfy_by": ["CODEOWNER approval"],
                }
            ]
            if contract_paths
            else []
        ),
        "apiChanges": {"detected": False},
        "schemaChanges": {"detected": False},
        "securityChanges": {"detected": False},
        "runtimeConfigChanges": {"detected": False},
        "prSize": {"verdict": "pass"},
        "exitCode": 0,
        "recommendedAction": "none",
        "modes": {"default": "shadow", "perCheck": {}},
        "suppressions": [],
        "behaviorContractChanges": {
            "version": 1,
            "detected": bool(contract_paths),
            "paths": [
                {"path": path, "owners": owners}
                for path in contract_paths
            ],
            "verification": "relay-behavior-contracts",
            "checkpoint": "behavior-review",
        },
    }
    build = repo / "build"
    build.mkdir(exist_ok=True)
    (build / "redline-verdict.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )


def _contract_change(path: str, *, classification: str = "coverage-only", authority: str = "@relay-owners") -> dict[str, object]:
    change: dict[str, object] = {
        "target": "repository-contract",
        "path": path,
        "classification": classification,
        "before": "Original relay behavior.",
        "after": "Refactored coverage of the same relay behavior.",
        "reason": "Preserve behavior while changing verification mechanics.",
    }
    if classification == "requirement-change":
        change.update({
            "impact": "Repository behavior changes.",
            "alternatives": "Keep the contract unchanged.",
            "authority": {"scope": "repository", "name": authority},
            "approval": {
                "by": authority,
                "reference": "PR-review-7",
                "verbatim": "Approved this exact repository contract change.",
            },
        })
    return change


def _run_contract(
    repo: Path,
    capsys: pytest.CaptureFixture[str],
    *,
    record_paths: dict[str, str],
    changed_paths: list[str],
    contract_paths: list[str],
    trusted: bool = True,
    owners: list[str] | None = None,
    red_paths: list[str] | None = None,
) -> tuple[int, dict]:
    for relative, text in record_paths.items():
        _write_record(repo, relative, text)
    _write_contract_redline(
        repo,
        contract_paths,
        owners=owners,
        red_paths=red_paths,
    )
    changed = repo / ("changed.z" if trusted else "changed.txt")
    if trusted:
        changed.write_bytes(
            b"\0".join(path.encode("utf-8") for path in changed_paths) + b"\0"
        )
        flag = "--changed-files-z"
    else:
        changed.write_text("\n".join(changed_paths) + "\n", encoding="utf-8")
        flag = "--changed-files"
    code = main(
        [
            "--repo-root",
            str(repo),
            flag,
            str(changed),
            "--redline-verdict",
            str(repo / "build" / "redline-verdict.json"),
        ]
    )
    return code, json.loads(capsys.readouterr().out)


@pytest.mark.parametrize(
    "task_path,record_path,pattern,contract_paths,classification",
    [
        (
            ".agent-workflow/tasks/{slug}.md",
            ".agent-workflow/tasks/demo.md",
            "contracts/exact wake.md",
            ["contracts/exact wake.md"],
            "equivalent",
        ),
        (
            ".work/items/{slug}.record.md",
            ".work/items/demo.record.md",
            "specs/relay/**",
            ["specs/relay/old wake.md", "specs/relay/新 wake.md"],
            "coverage-only",
        ),        (
            ".agent-workflow/tasks/{slug}.md",
            ".agent-workflow/tasks/demo.md",
            "behavior/**",
            ["behavior/approved.md"],
            "requirement-change",
        ),
    ],
)
def test_contract_gate_handles_exact_and_descendant_layouts_rename_delete_unicode(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    task_path: str,
    record_path: str,
    pattern: str,
    contract_paths: list[str],
    classification: str,
) -> None:
    _contract_config(tmp_path, pattern=pattern, task_path=task_path)
    record = _record(
        changes=[_contract_change(path, classification=classification) for path in contract_paths],
        verification="relay-behavior-contracts",
    )
    _, payload = _run_contract(
        tmp_path,
        capsys,
        record_paths={record_path: record},
        changed_paths=[record_path, *contract_paths],
        contract_paths=contract_paths,
    )
    contract = next(record for record in payload["records"] if record["slug"] == "<behavior-contracts>")
    assert contract["status"] == "clean"
    assert all(predicate["passed"] for predicate in contract["predicates"])


@pytest.mark.parametrize("case", ["missing", "wrong-authority", "wrong-codeowner", "verification-substring"])
def test_contract_gate_blocks_missing_classification_authority_or_verification(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], case: str
) -> None:
    path = "contracts/wake.md"
    _contract_config(tmp_path, pattern="contracts/**")
    changes = None
    verification = "relay-behavior-contracts"
    if case == "wrong-authority":
        change = _contract_change(path, classification="requirement-change")
        change["authority"] = {"scope": "task", "name": "task-owner"}
        change["approval"] = {
            "by": "user",
            "reference": "task-approval",
            "verbatim": "Approved only for this task.",
        }
        changes = [change]
    elif case == "wrong-codeowner":
        change = _contract_change(path, classification="requirement-change")
        change["authority"] = {"scope": "repository", "name": "@other-owner"}
        change["approval"]["by"] = "@other-owner"
        changes = [change]
    elif case == "verification-substring":
        changes = [_contract_change(path)]
        verification = "relay-behavior-contracts-extra"
    record_path = ".agent-workflow/tasks/demo.md"
    _, payload = _run_contract(
        tmp_path,
        capsys,
        record_paths={record_path: _record(changes=changes, verification=verification)},
        changed_paths=[record_path, path],
        contract_paths=[path],
    )
    assert next(record for record in payload["records"] if record["slug"] == "<behavior-contracts>")["status"] == "blocking"


def test_contract_gate_does_not_reuse_unchanged_branch_record(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = "contracts/wake.md"
    _contract_config(tmp_path, pattern=path)
    record_path = ".agent-workflow/tasks/demo.md"
    _write_record(
        tmp_path,
        record_path,
        _record(changes=[_contract_change(path)], verification="relay-behavior-contracts"),
    )
    changed = tmp_path / "changed.z"
    changed.write_bytes(path.encode("utf-8") + b"\0")
    _write_contract_redline(tmp_path, [path])
    main([
        "--repo-root",
        str(tmp_path),
        "--changed-files-z",
        str(changed),
        "--slug",
        "demo",
    ])
    payload = json.loads(capsys.readouterr().out)
    assert _predicate(
        payload, "behavior_contracts.changed_paths_classified"
    )["passed"] is False


def test_contract_gate_rejects_duplicate_classification_across_records(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = "contracts/wake.md"
    _contract_config(tmp_path, pattern=path)
    records = {
        ".agent-workflow/tasks/one.md": _record(changes=[_contract_change(path)], verification="relay-behavior-contracts"),
        ".agent-workflow/tasks/two.md": _record(changes=[_contract_change(path)], verification="relay-behavior-contracts"),
    }
    _, payload = _run_contract(
        tmp_path,
        capsys,
        record_paths=records,
        changed_paths=[*records, path],
        contract_paths=[path],
    )
    assert _predicate(payload, "behavior_contracts.changed_paths_classified")["passed"] is False


def test_contract_gate_requires_trusted_safe_paths_and_denies_documentation_exemption(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _contract_config(tmp_path, pattern="contracts/**", applicability=True)
    _, legacy = _run_contract(
        tmp_path,
        capsys,
        record_paths={},
        changed_paths=["contracts/wake.md"],
        contract_paths=["contracts/wake.md"],
        trusted=False,
    )
    assert _predicate(legacy, "behavior_contracts.changed_paths_complete")["passed"] is False

    incomplete = tmp_path / "incomplete.z"
    incomplete.write_bytes(b"contracts/wake.md")
    _write_contract_redline(tmp_path, ["contracts/wake.md"])
    main(["--repo-root", str(tmp_path), "--changed-files-z", str(incomplete)])
    incomplete_payload = json.loads(capsys.readouterr().out)
    assert _predicate(
        incomplete_payload, "behavior_contracts.redline_evidence_complete"
    )["passed"] is False

    _, unsafe = _run_contract(
        tmp_path,
        capsys,
        record_paths={},
        changed_paths=["../contracts/wake.md"],
        contract_paths=["../contracts/wake.md"],
    )
    assert _predicate(unsafe, "behavior_contracts.redline_evidence_complete")["passed"] is False

    _, protected = _run_contract(
        tmp_path,
        capsys,
        record_paths={},
        changed_paths=["contracts/wake.md"],
        contract_paths=["contracts/wake.md"],
    )
    names = [
        predicate["name"]
        for record in protected["records"]
        for predicate in record["predicates"]
    ]
    assert "workrecord.required_for_branch_changes" in names
    assert "workflow.applicability" in names
    assert "behavior_contracts.changed_paths_classified" in names


@pytest.mark.parametrize("case", ["missing-detail", "omitted-current", "wrong-controls"])
def test_contract_gate_correlates_current_redline_policy_and_detail(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    case: str,
) -> None:
    path = "contracts/wake.md"
    _contract_config(tmp_path, pattern="contracts/**")
    _write_contract_redline(tmp_path, [path])
    verdict_path = tmp_path / "build" / "redline-verdict.json"
    payload = json.loads(verdict_path.read_text(encoding="utf-8"))
    if case == "missing-detail":
        del payload["behaviorContractChanges"]
    elif case == "omitted-current":
        payload["behaviorContractChanges"]["detected"] = False
        payload["behaviorContractChanges"]["paths"] = []
    else:
        payload["behaviorContractChanges"]["verification"] = "stale-check"
    verdict_path.write_text(json.dumps(payload), encoding="utf-8")
    changed = tmp_path / "changed.z"
    changed.write_bytes(path.encode("utf-8") + b"\0")
    main([
        "--repo-root", str(tmp_path),
        "--changed-files-z", str(changed),
        "--redline-verdict", str(verdict_path),
    ])
    result = json.loads(capsys.readouterr().out)
    assert _predicate(
        result, "behavior_contracts.redline_evidence_complete"
    )["passed"] is False


def test_contract_gate_rejects_duplicate_changed_path_evidence(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _contract_config(tmp_path, pattern="contracts/**")
    _, payload = _run_contract(
        tmp_path,
        capsys,
        record_paths={},
        changed_paths=["contracts/wake.md", "contracts/wake.md"],
        contract_paths=["contracts/wake.md"],
    )
    assert _predicate(
        payload, "behavior_contracts.changed_paths_complete"
    )["passed"] is False


def test_complete_non_contract_diff_adds_no_contract_gate(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _contract_config(tmp_path, pattern="contracts/**")
    _, payload = _run_contract(
        tmp_path,
        capsys,
        record_paths={},
        changed_paths=["src/app.py"],
        contract_paths=[],
    )
    assert all(record["slug"] != "<behavior-contracts>" for record in payload["records"])

@pytest.mark.parametrize("case", ["ownerless", "non-red", "out-of-diff"])
def test_contract_gate_rejects_inconsistent_redline_evidence(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    case: str,
) -> None:
    path = "contracts/wake.md"
    _contract_config(tmp_path, pattern="contracts/**")
    changed_paths = [path]
    owners = ["@relay-owners"]
    red_paths = [path]
    if case == "ownerless":
        owners = []
    elif case == "non-red":
        red_paths = []
    else:
        changed_paths = ["src/app.py"]
    _, payload = _run_contract(
        tmp_path,
        capsys,
        record_paths={},
        changed_paths=changed_paths,
        contract_paths=[path],
        owners=owners,
        red_paths=red_paths,
    )
    assert next(
        record
        for record in payload["records"]
        if record["slug"] == "<behavior-contracts>"
    )["status"] == "blocking"
