"""Real-Git coverage for the requirement-baseline history gate."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
GIT = shutil.which("git")
assert GIT is not None
RECORD = ".agent-workflow/tasks/example.md"
OLD = {"source": "request:1", "outcome": "O", "scope": "S", "constraints": "C", "completion_criteria": "D"}
NEW = {**OLD, "outcome": "changed"}


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        [GIT, *args], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()


def _record(baseline: dict | str | None, *, context: dict | None = None) -> str:
    context = context or (baseline if isinstance(baseline, dict) else OLD)
    baseline_text = (
        f"**Requirement baseline:**\n{json.dumps(baseline) if isinstance(baseline, dict) else baseline}\n\n"
        if baseline is not None else ""
    )
    return f"""<!-- agent-workflow:start -->
**Outcome:** {context["outcome"]}
**Target:** example
**Scope:** {context["scope"]}
**Constraints:** {context["constraints"]}
**Completion criteria:** {context["completion_criteria"]}
{baseline_text}**Risk:** Routine
**Complexity:** Simple
**Reason:** —
**Approach:** example
**Verification:** example
**State:** Ready to implement
<!-- agent-workflow:end -->
"""


def _commit(repo: Path, message: str, *, when: str | None = None) -> str:
    _git(repo, "add", "-A")
    env = dict(os.environ)
    if when:
        env.update(GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
    subprocess.run(
        [GIT, "commit", "-qm", message], cwd=repo, env=env, check=True, capture_output=True
    )
    return _git(repo, "rev-parse", "HEAD")


def _repo(
    tmp_path: Path,
    records: dict[str, dict | None] | None = None,
    *,
    task_path: str = ".agent-workflow/tasks/{slug}.md",
) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    config = (
        'version: 1\nproject: {name: example}\nworkRecord:\n  backend: local\n  local:\n'
        '    taskPath: "TASK_PATH"\nredline: optional\n'
    ).replace("TASK_PATH", task_path)
    (repo / "agent-workflow.yaml").write_text(config, encoding="utf-8")
    for path, baseline in (records or {}).items():
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(_record(baseline), encoding="utf-8")
    return repo, _commit(repo, "base")


def _check(
    repo: Path, base: str, head: str, paths: list[str], *, vendored: bool = False
) -> tuple[int, dict]:
    changed = repo / "changed-files.z"
    changed.write_bytes(b"\0".join(p.encode("utf-8") for p in paths) + b"\0")
    env = dict(os.environ, PYTHONPATH=str(ROOT))
    checker = (
        [sys.executable, str(ROOT / "dist/agent-workflow/scripts/agent-workflow-check.py")]
        if vendored else [sys.executable, "-m", "core.checker"]
    )
    result = subprocess.run(
        [*checker, "--repo-root", str(repo), "--changed-files-z", str(changed),
         "--base-ref", base, "--head-ref", head],
        cwd=ROOT, env=env, capture_output=True, text=True, check=False,
    )
    assert result.stdout, result.stderr
    return result.returncode, json.loads(result.stdout)


def _baseline_result(payload: dict, slug: str = "example") -> dict:
    record = next(r for r in payload["records"] if r["slug"] == slug)
    return next(p for p in record["predicates"] if p["name"] == "requirements.baseline_unchanged")


def test_new_record_first_commit_is_anchor_and_later_tampering_fails(tmp_path: Path) -> None:
    repo, base = _repo(tmp_path)
    target = repo / RECORD
    target.parent.mkdir(parents=True)
    target.write_text(_record(OLD), encoding="utf-8")
    first = _commit(repo, "add record")
    target.write_text(_record(NEW), encoding="utf-8")
    head = _commit(repo, "rewrite baseline")

    code, payload = _check(repo, base, head, [RECORD])
    assert code == 2
    assert _baseline_result(payload)["passed"] is False


def test_source_only_baseline_tampering_fails(tmp_path: Path) -> None:
    repo, base = _repo(tmp_path)
    target = repo / RECORD
    target.parent.mkdir(parents=True)
    target.write_text(_record(OLD), encoding="utf-8")
    _commit(repo, "add record")
    source_changed = {**OLD, "source": "request:2"}
    target.write_text(_record(source_changed, context=OLD), encoding="utf-8")
    head = _commit(repo, "rewrite baseline source only")

    code, payload = _check(repo, base, head, [RECORD])
    assert code == 2
    assert _baseline_result(payload)["passed"] is False


@pytest.mark.parametrize("first_baseline", [None, "not-json"])
def test_new_record_requires_valid_baseline_in_first_commit(
    tmp_path: Path, first_baseline: dict | str | None
) -> None:
    repo, base = _repo(tmp_path)
    target = repo / RECORD
    target.parent.mkdir(parents=True)
    target.write_text(_record(first_baseline), encoding="utf-8")
    _commit(repo, "add record with missing or malformed baseline")
    target.write_text(_record(OLD), encoding="utf-8")
    head = _commit(repo, "add valid baseline later")

    code, payload = _check(repo, base, head, [RECORD])
    assert code == 2
    assert _baseline_result(payload)["passed"] is False


def test_base_existing_record_tampering_fails_but_json_formatting_passes(tmp_path: Path) -> None:
    repo, base = _repo(tmp_path, {RECORD: OLD})
    target = repo / RECORD
    target.write_text(_record(OLD).replace(json.dumps(OLD), json.dumps(OLD).replace("{", "{ ").replace("}", " }")), encoding="utf-8")
    formatted = _commit(repo, "format baseline json")
    code, payload = _check(repo, base, formatted, [RECORD])
    assert code in (0, 1), json.dumps(payload, indent=2)
    assert _baseline_result(payload)["passed"] is True

    target.write_text(_record(NEW), encoding="utf-8")
    head = _commit(repo, "rewrite baseline")
    code, payload = _check(repo, base, head, [RECORD])
    assert code == 2
    assert _baseline_result(payload)["passed"] is False


def test_legacy_base_record_can_establish_once_then_tampering_fails(tmp_path: Path) -> None:
    repo, base = _repo(tmp_path, {RECORD: None})
    target = repo / RECORD
    target.write_text(_record(OLD), encoding="utf-8")
    established = _commit(repo, "establish legacy baseline")
    code, payload = _check(repo, base, established, [RECORD])
    assert code in (0, 1), json.dumps(payload, indent=2)
    assert _baseline_result(payload)["passed"] is True
    target.write_text(_record(NEW), encoding="utf-8")
    head = _commit(repo, "rewrite established baseline")

    code, payload = _check(repo, base, head, [RECORD])
    assert code == 2
    assert _baseline_result(payload)["passed"] is False


@pytest.mark.parametrize("refs", [(None, "HEAD"), ("HEAD", None), ("missing", "HEAD")])
def test_partial_or_invalid_history_refs_fail_closed(
    tmp_path: Path, refs: tuple[str | None, str | None]
) -> None:
    repo, base = _repo(tmp_path, {RECORD: OLD})
    target = repo / RECORD
    target.write_text(_record({**OLD, "scope": "changed"}), encoding="utf-8")
    head = _commit(repo, "touch record")
    changed = repo / "changed-files.z"
    changed.write_bytes((RECORD + "\0").encode())
    args = [sys.executable, "-m", "core.checker", "--repo-root", str(repo),
            "--changed-files-z", str(changed)]
    if refs[0] is not None:
        args += ["--base-ref", refs[0] if refs[0] != "missing" else "refs/heads/not-here"]
    if refs[1] is not None:
        args += ["--head-ref", refs[1] if refs[1] != "HEAD" else head]
    result = subprocess.run(args, cwd=ROOT, env=dict(os.environ, PYTHONPATH=str(ROOT)),
                            capture_output=True, text=True, check=False)
    payload = json.loads(result.stdout)
    assert result.returncode == 2
    predicate = _baseline_result(payload)
    assert predicate["passed"] is False


def test_custom_task_path_baseline_history_is_checked(tmp_path: Path) -> None:
    task_path = ".work/items/{slug}.record.md"
    record_path = ".work/items/alpha.record.md"
    repo, base = _repo(tmp_path, {record_path: OLD}, task_path=task_path)
    target = repo / record_path
    target.write_text(_record(NEW), encoding="utf-8")
    head = _commit(repo, "rewrite custom-path baseline")

    code, payload = _check(repo, base, head, [record_path])
    assert code == 2
    assert _baseline_result(payload, slug="alpha")["passed"] is False


def test_deleted_record_and_multiple_nul_paths_are_visible(tmp_path: Path) -> None:
    second = ".agent-workflow/tasks/second.md"
    repo, base = _repo(tmp_path, {RECORD: OLD, second: OLD})
    (repo / RECORD).unlink()
    (repo / second).write_text(_record(NEW), encoding="utf-8")
    head = _commit(repo, "delete one and rewrite another")

    code, payload = _check(repo, base, head, [RECORD, second, "notes/with\nnewline.md"])
    assert code == 2
    assert "example" in {r["slug"] for r in payload["records"]}
    assert "second" in {r["slug"] for r in payload["records"]}


def test_renamed_record_old_path_is_still_checked(tmp_path: Path) -> None:
    repo, base = _repo(tmp_path, {RECORD: OLD})
    renamed = ".agent-workflow/tasks/renamed.md"
    _git(repo, "mv", RECORD, renamed)
    (repo / renamed).write_text(_record(NEW), encoding="utf-8")
    head = _commit(repo, "rename and rewrite baseline")

    code, payload = _check(repo, base, head, [RECORD, renamed])
    assert code == 2
    assert "renamed" in {r["slug"] for r in payload["records"]}
    assert any(
        p["name"] == "workrecord.exists" and not p["passed"]
        for r in payload["records"] for p in r["predicates"]
    )

def test_unrelated_base_ref_fails_closed(tmp_path: Path) -> None:
    repo, base = _repo(tmp_path, {RECORD: OLD})
    target = repo / RECORD
    target.write_text(_record(NEW), encoding="utf-8")
    head = _commit(repo, "rewrite baseline")
    branch = _git(repo, "branch", "--show-current")
    _git(repo, "checkout", "--orphan", "unrelated")
    (repo / "unrelated.txt").write_text("unrelated history\n", encoding="utf-8")
    unrelated = _commit(repo, "unrelated root")
    _git(repo, "checkout", branch)

    code, payload = _check(repo, unrelated, head, [RECORD])
    assert code == 2
    assert _baseline_result(payload)["passed"] is False


def test_vendored_checker_cli_detects_baseline_rewrite(tmp_path: Path) -> None:
    repo, base = _repo(tmp_path)
    target = repo / RECORD
    target.parent.mkdir(parents=True)
    target.write_text(_record(OLD), encoding="utf-8")
    _commit(repo, "add record")
    target.write_text(_record(NEW), encoding="utf-8")
    head = _commit(repo, "rewrite baseline")

    code, payload = _check(repo, base, head, [RECORD], vendored=True)
    assert code == 2
    assert _baseline_result(payload)["passed"] is False


def test_synthetic_merge_head_uses_explicit_pr_head(tmp_path: Path) -> None:
    repo, base = _repo(tmp_path)
    base_branch = _git(repo, "branch", "--show-current")
    _git(repo, "checkout", "-qb", "feature")
    target = repo / RECORD
    target.parent.mkdir(parents=True)
    target.write_text(_record(OLD), encoding="utf-8")
    first = _commit(repo, "add record")
    target.write_text(_record(NEW), encoding="utf-8")
    pr_head = _commit(repo, "rewrite baseline")
    _git(repo, "checkout", "-q", base_branch)
    (repo / "main.txt").write_text("main\n", encoding="utf-8")
    _commit(repo, "main change")
    _git(repo, "merge", "--no-ff", "-qm", "synthetic merge", "feature")

    code, payload = _check(repo, base, pr_head, [RECORD])
    assert code == 2
    assert _baseline_result(payload)["passed"] is False


@pytest.mark.parametrize(
    ("initial", "later", "valid"),
    [
        (None, OLD, False),
        ("not-json", OLD, False),
        (OLD, NEW, False),
        (OLD, None, True),
    ],
)
@pytest.mark.parametrize("vendored", [False, True])
def test_merged_side_parent_preserves_first_baseline_commit(
    tmp_path: Path,
    initial: dict | str | None,
    later: dict | None,
    valid: bool,
    vendored: bool,
) -> None:
    repo, _ = _repo(tmp_path)
    main = _git(repo, "branch", "--show-current")
    _git(repo, "checkout", "-qb", "side")
    target = repo / RECORD
    target.parent.mkdir(parents=True)
    target.write_text(_record(initial), encoding="utf-8")
    _commit(repo, "first record", when="2030-01-01T12:00:00 +0000")
    if later is not None:
        target.write_text(_record(later), encoding="utf-8")
        _commit(repo, "later baseline", when="2020-01-01T12:00:00 +0000")
    _git(repo, "checkout", main)
    (repo / "main.txt").write_text("main\n", encoding="utf-8")
    pr_base = _commit(repo, "main change")
    _git(repo, "merge", "--no-ff", "-qm", "merge side", "side")
    pr_head = _git(repo, "rev-parse", "HEAD")

    code, payload = _check(repo, pr_base, pr_head, [RECORD], vendored=vendored)
    assert _baseline_result(payload)["passed"] is valid, json.dumps(payload, indent=2)
    assert (code in (0, 1)) is valid


def test_nested_project_root_resolves_git_blob_relative_to_cwd(tmp_path: Path) -> None:
    repo, base = _repo(tmp_path)
    nested = repo / "project"
    nested.mkdir()
    shutil.copyfile(repo / "agent-workflow.yaml", nested / "agent-workflow.yaml")
    target = nested / RECORD
    target.parent.mkdir(parents=True)
    target.write_text(_record(OLD), encoding="utf-8")
    first = _commit(repo, "add nested record")

    code, payload = _check(nested, base, first, [RECORD])
    assert code in (0, 1), json.dumps(payload, indent=2)
    assert _baseline_result(payload)["passed"] is True

    target.write_text(_record(NEW), encoding="utf-8")
    head = _commit(repo, "rewrite nested baseline")
    code, payload = _check(nested, base, head, [RECORD])
    assert code == 2
    assert _baseline_result(payload)["passed"] is False


SAFE_SOURCE = "User-approved source (privacy-redacted provenance)"
SAFE_CONSTRAINTS = "Approved public constraints"
SAFE_COMPLETION = "Approved public completion criteria"


def _receipt(anchor: str, path: str = RECORD) -> dict:
    return {"schema_version": 1, "record_path": path, "anchor_commit": anchor,
            "replacements": {"source": SAFE_SOURCE}, "reason": "Remove private provenance.",
            "approval": {"by": "user", "reference": "Maintainer approval of exact migration",
                         "verbatim": "Yes, approve the exact record, anchor and source replacement."}}


def _receipt_v2(anchor: str, path: str = RECORD) -> dict:
    return {"schema_version": 2, "record_path": path, "anchor_commit": anchor,
            "replacements": {"source": SAFE_SOURCE, "constraints": SAFE_CONSTRAINTS,
                             "completion_criteria": SAFE_COMPLETION},
            "reason": "Remove private provenance.",
            "approval": {"by": "user", "reference": "Maintainer approval of exact migration",
                         "verbatim": "Yes, approve the exact record, anchor and replacements."}}


def _privacy_record(receipt: dict | None, *, baseline: dict | str | None = None,
                    context: dict | None = None, chain: list | None = None) -> str:
    text = _record({**OLD, "source": SAFE_SOURCE} if baseline is None else baseline,
                   context=context or OLD)
    extra = "" if receipt is None else f"**Baseline privacy migration:** {json.dumps(receipt)}\n"
    if chain is not None:
        extra += f"**Behavior changes:** {json.dumps(chain)}\n"
    return text.replace("**State:**", extra + "**State:**")


def _privacy_record_v2(receipt: dict | None, *, baseline: dict | str | None = None,
                       context: dict | None = None, chain: list | None = None,
                       extra_fields: str = "") -> str:
    replacements = (receipt["replacements"] if receipt is not None else
                    {"source": SAFE_SOURCE, "constraints": SAFE_CONSTRAINTS,
                     "completion_criteria": SAFE_COMPLETION})
    baseline = {**OLD, **replacements} if baseline is None else baseline
    context = {**OLD, **{key: value for key, value in replacements.items() if key != "source"}} \
        if context is None else context
    text = _record(baseline, context=context)
    extra = "" if receipt is None else f"**Baseline privacy migration:** {json.dumps(receipt)}\n"
    if chain is not None:
        extra += f"**Behavior changes:** {json.dumps(chain)}\n"
    return text.replace("**State:**", extra + extra_fields + "**State:**")


def _with_expanded_approval(text: str, approval: str) -> str:
    text = text.replace("**Risk:** Routine", "**Risk:** High")
    text = text.replace("**Complexity:** Simple", "**Complexity:** Moderate")
    fields = (
        "**Discovery:** Synthetic discovery\n"
        "**Material assumptions:** Synthetic assumption\n"
        "**Plan:** Synthetic plan\n"
        "**Verification plan:** Synthetic verification\n"
        "**Plan review:** Synthetic review\n"
        f"**Approvals:** {approval}\n"
        "**Exceptions:** —\n"
    )
    return text.replace("**State:**", fields + "**State:**")


@pytest.mark.parametrize(("task_path", "path"), [
    (".agent-workflow/tasks/{slug}.md", RECORD),
    (".work/items/{slug}.md", ".work/items/example.md"),
])
@pytest.mark.parametrize("vendored", [False, True], ids=["source", "standalone"])
def test_v2_atomic_migration_in_configured_task_path_layouts(
    tmp_path: Path, task_path: str, path: str, vendored: bool,
) -> None:
    repo, base = _repo(tmp_path, {path: OLD}, task_path=task_path)
    receipt = _receipt_v2(base, path)
    target = repo / path
    pre_context = {**OLD, "scope": "Pre-migration scope"}
    pre_chain = [{"target": "task-context.scope", "classification": "equivalent",
                  "before": OLD["scope"], "after": pre_context["scope"],
                  "reason": "Clarify scope before migration."}]
    target.write_text(_record(OLD, context=pre_context).replace("**State:**",
        f"**Behavior changes:** {json.dumps(pre_chain)}\n**State:**"), encoding="utf-8")
    _commit(repo, "pre-migration scope clarification")
    target.write_text(_privacy_record_v2(
        receipt, context={**pre_context, "constraints": SAFE_CONSTRAINTS,
                          "completion_criteria": SAFE_COMPLETION}, chain=pre_chain,
    ), encoding="utf-8")
    migrated = _commit(repo, "approved paired baseline migration")
    code, payload = _check(repo, base, migrated, [path], vendored=vendored)
    assert code in (0, 1), json.dumps(payload, indent=2)
    assert _baseline_result(payload, Path(path).stem)["passed"]

    # Once retained at the selected base, ordinary later changes use the normal chain.
    later_chain = [*pre_chain, {"target": "task-context.constraints", "classification": "equivalent",
                    "before": SAFE_CONSTRAINTS, "after": "Later approved clarification",
                    "reason": "Clarify the current task."}]
    target.write_text(_privacy_record_v2(
        receipt, context={**pre_context, "constraints": "Later approved clarification",
                          "completion_criteria": SAFE_COMPLETION}, chain=later_chain,
    ), encoding="utf-8")
    later = _commit(repo, "ordinary later refinement")
    code, payload = _check(repo, migrated, later, [path], vendored=vendored)
    assert code in (0, 1), json.dumps(payload, indent=2)
    assert _baseline_result(payload, Path(path).stem)["passed"]


@pytest.mark.parametrize(("attack", "vendored"), [
    ("source-noop", False), ("constraints-noop", False), ("completion-noop", False),
    ("source-pair", False), ("constraints-pair", False), ("completion-pair", False),
    ("constraints-current", False), ("completion-current", False),
    ("pre-context-constraints", False), ("pre-context-completion", False),
    ("chain-constraints", False), ("chain-completion", False), ("target", False),
    ("approvals", False), ("relationships", False), ("chain-whitespace", False),
    ("path", False), ("anchor", False), ("approval", False),
    pytest.param("constraints-noop", True, id="constraints-noop-standalone"),
    pytest.param("constraints-pair", True, id="constraints-pair-standalone"),
    pytest.param("target", True, id="target-standalone"),
    pytest.param("approvals", True, id="approvals-standalone"),
    pytest.param("chain-whitespace", True, id="chain-whitespace-standalone"),
])
def test_v2_rejects_noops_mismatched_pairs_and_unrelated_changes(
    tmp_path: Path, attack: str, vendored: bool,
) -> None:
    repo, base = _repo(tmp_path, {RECORD: OLD})
    target = repo / RECORD
    receipt = _receipt_v2(base)
    baseline = {**OLD, **receipt["replacements"]}
    context = {**OLD, **{key: value for key, value in receipt["replacements"].items()
                         if key != "source"}}
    chain: list | None = None
    after_extra = ""

    if attack.endswith("-noop"):
        field = {"source-noop": "source", "constraints-noop": "constraints",
                 "completion-noop": "completion_criteria"}[attack]
        receipt["replacements"][field] = OLD[field]
        if field == "source":
            baseline[field] = OLD[field]
        else:
            baseline[field] = context[field] = OLD[field]
    elif attack == "source-pair":
        baseline["source"] = "A different approved-looking source"
    elif attack == "constraints-pair":
        baseline["constraints"] = "Mismatched constraints"
    elif attack == "completion-pair":
        baseline["completion_criteria"] = "Mismatched completion criteria"
    elif attack == "constraints-current":
        context["constraints"] = "Mismatched current constraints"
    elif attack == "completion-current":
        context["completion_criteria"] = "Mismatched current completion criteria"
    elif attack in {"pre-context-constraints", "pre-context-completion"}:
        field = "constraints" if attack.endswith("constraints") else "completion_criteria"
        label = "Constraints" if field == "constraints" else "Completion criteria"
        old_text = _record(OLD).replace(f"**{label}:** {OLD[field]}",
                                        f"**{label}:** Pre-transition mismatch")
        target.write_text(old_text, encoding="utf-8")
        _commit(repo, "pre-transition current-context edit")
    elif attack in {"chain-constraints", "chain-completion", "chain-whitespace"}:
        field = "constraints" if attack == "chain-constraints" else "completion_criteria"
        target_name = f"task-context.{field}"
        current = OLD[field]
        intermediate = "Synthetic intermediate value"
        chain = [] if attack == "chain-whitespace" else [
            {"target": target_name, "classification": "equivalent", "before": current,
             "after": intermediate, "reason": "Synthetic prior chain entry."},
            {"target": target_name, "classification": "equivalent", "before": intermediate,
             "after": current, "reason": "Synthetic restoring chain entry."},
        ]
        raw_chain = "[]   " if attack == "chain-whitespace" else json.dumps(chain)
        target.write_text(_record(OLD).replace("**State:**",
            f"**Behavior changes:** {raw_chain}\n**State:**"), encoding="utf-8")
        _commit(repo, "pre-transition change chain")
    elif attack in {"target", "approvals", "relationships"}:
        if attack == "target":
            target.write_text(_record(OLD).replace("**Target:** example", "**Target:** Before"), encoding="utf-8")
            _commit(repo, "pre-transition marker field edit")
        elif attack == "approvals":
            target.write_text(_with_expanded_approval(_record(OLD), "Synthetic reviewer A"), encoding="utf-8")
            _commit(repo, "pre-transition marker field edit")
        else:
            relationships = '{"schema_version":1,"sources":null,"pull_requests":[]}'
            target.write_text(_record(OLD).replace("**State:**",
                f"**Relationships:** {relationships}\n**State:**"), encoding="utf-8")
            _commit(repo, "pre-transition marker field edit")
            after_extra = '**Relationships:** {"schema_version":1,"sources":[],"pull_requests":[]}\n'
    elif attack == "path":
        receipt["record_path"] = ".agent-workflow/tasks/other.md"
    elif attack == "anchor":
        receipt["anchor_commit"] = "a" * 40
    elif attack == "approval":
        receipt["approval"]["by"] = "agent"

    migrated_text = _privacy_record_v2(receipt, baseline=baseline, context=context,
                                       chain=chain, extra_fields=after_extra)
    if attack == "approvals":
        migrated_text = _with_expanded_approval(migrated_text, "Synthetic reviewer B")
    target.write_text(migrated_text, encoding="utf-8")
    head = _commit(repo, "invalid paired-baseline migration")
    code, payload = _check(repo, base, head, [RECORD], vendored=vendored)
    assert code == 2
    assert not _baseline_result(payload)["passed"]


@pytest.mark.parametrize("vendored", [False, True], ids=["source", "standalone"])
def test_v2_merge_rejects_raw_parent_difference_omitted_by_history_snapshot(
    tmp_path: Path, vendored: bool,
) -> None:
    repo, base = _repo(tmp_path, {RECORD: OLD})
    main = _git(repo, "branch", "--show-current")
    target = repo / RECORD
    _git(repo, "checkout", "-qb", "side")
    target.write_text(_record(OLD).replace("**Target:** example", "**Target:** side value"), encoding="utf-8")
    _commit(repo, "side changes only Target")
    _git(repo, "checkout", main)
    (repo / "main.txt").write_text("main\n", encoding="utf-8")
    _commit(repo, "main changes only an unrelated file")
    _git(repo, "merge", "--no-commit", "--no-ff", "-s", "ours", "side")
    target.write_text(_privacy_record_v2(_receipt_v2(base)), encoding="utf-8")
    head = _commit(repo, "attempt v2 migration from unequal raw parents")
    code, payload = _check(repo, base, head, [RECORD], vendored=vendored)
    assert code == 2
    result = _baseline_result(payload)
    assert not result["passed"]
    assert "pre-redaction identity" in result["detail"]


@pytest.mark.parametrize("existing", [False, True])
def test_approved_source_only_migration_and_later_retention(tmp_path: Path, existing: bool) -> None:
    repo, base = _repo(tmp_path, {RECORD: OLD} if existing else None)
    target = repo / RECORD
    if existing:
        anchor = base
    else:
        target.parent.mkdir(parents=True)
        target.write_text(_record(OLD), encoding="utf-8")
        anchor = _commit(repo, "first baseline")
    # A valid pre-existing chain must survive intact; compare with the immediate parent.
    chain = [{"target": "task-context.scope", "classification": "equivalent",
              "before": "S", "after": "Refined S", "reason": "Clarify scope."}]
    context = {**OLD, "scope": "Refined S"}
    target.write_text(_record(OLD, context=context).replace("**State:**",
                      f"**Behavior changes:** {json.dumps(chain)}\n**State:**"), encoding="utf-8")
    _commit(repo, "refine before migration")
    receipt = _receipt(anchor)
    target.write_text(_privacy_record(receipt, context=context, chain=chain), encoding="utf-8")
    migrated = _commit(repo, "approved source redaction")
    code, payload = _check(repo, base, migrated, [RECORD])
    assert _baseline_result(payload)["passed"], json.dumps(payload, indent=2)
    assert code in (0, 1)
    # The original anchor stays fixed when a future PR uses a newer authoritative base.
    later_chain = [*chain, {"target": "task-context.constraints", "classification": "equivalent",
                           "before": "C", "after": "Clarified C", "reason": "Clarify constraints."}]
    target.write_text(_privacy_record(receipt, context={**context, "constraints": "Clarified C"},
                                      chain=later_chain), encoding="utf-8")
    later = _commit(repo, "ordinary later refinement")
    code, payload = _check(repo, migrated, later, [RECORD])
    assert _baseline_result(payload)["passed"], json.dumps(payload, indent=2)
    assert code in (0, 1)


@pytest.mark.parametrize("attack", ["path", "anchor", "replacement", "noop", "null-source",
    "functional", "context", "chain", "malformed-before", "arbitrary-ancestor"])
def test_privacy_migration_rejects_invalid_transition(tmp_path: Path, attack: str) -> None:
    old = {**OLD, "source": None} if attack == "null-source" else OLD
    repo, initial = _repo(tmp_path, {RECORD: old})
    (repo / "notes.txt").write_text("new base\n", encoding="utf-8")
    base = _commit(repo, "authoritative PR base")
    receipt = _receipt(base)
    if attack == "path":
        receipt["record_path"] = ".agent-workflow/tasks/other.md"
    if attack == "anchor":
        receipt["anchor_commit"] = "a" * 40
    if attack == "arbitrary-ancestor":
        receipt["anchor_commit"] = initial
    if attack == "replacement":
        receipt["replacements"]["source"] = "Different public source"
    target = repo / RECORD
    if attack == "malformed-before":
        target.write_text(_record("not-json"), encoding="utf-8")
        _commit(repo, "malformed historical baseline")
    baseline = {**OLD, "source": SAFE_SOURCE}
    if attack == "noop":
        receipt["replacements"]["source"] = OLD["source"]
        baseline = OLD
    if attack == "functional":
        baseline["constraints"] = "changed"
    context = {**OLD, "scope": "changed"} if attack == "context" else OLD
    chain = [{"target": "task-context.scope", "classification": "equivalent", "before": "S",
              "after": "changed", "reason": "Inserted during redaction."}] if attack == "chain" else None
    target.write_text(_privacy_record(receipt, baseline=baseline, context=context, chain=chain), encoding="utf-8")
    head = _commit(repo, "invalid migration")
    code, payload = _check(repo, base, head, [RECORD])
    assert code == 2
    assert not _baseline_result(payload)["passed"]
    assert "request:1" not in _baseline_result(payload)["detail"]


@pytest.mark.parametrize("version", [1, 2], ids=["v1", "v2"])
@pytest.mark.parametrize("attack", ["remove", "tamper", "second-source", "delete", "rename"])
def test_privacy_receipt_history_cannot_be_repaired_by_restoration(
    tmp_path: Path, attack: str, version: int,
) -> None:
    repo, base = _repo(tmp_path, {RECORD: OLD})
    target = repo / RECORD
    receipt = _receipt(base) if version == 1 else _receipt_v2(base)
    make_record = _privacy_record if version == 1 else _privacy_record_v2
    good = make_record(receipt)
    target.write_text(good, encoding="utf-8")
    _commit(repo, "approved migration")
    if attack == "remove":
        target.write_text(make_record(None), encoding="utf-8")
    elif attack == "tamper":
        target.write_text(make_record({**receipt, "reason": "Changed receipt"}), encoding="utf-8")
    elif attack == "second-source":
        changed = {**OLD, **receipt["replacements"], "source": "Another source"}
        target.write_text(make_record(receipt, baseline=changed), encoding="utf-8")
    elif attack == "delete":
        target.unlink()
    else:
        _git(repo, "mv", RECORD, ".agent-workflow/tasks/renamed.md")
    _commit(repo, "intermediate invalid change")
    if attack == "rename":
        _git(repo, "mv", ".agent-workflow/tasks/renamed.md", RECORD)
    target.write_text(good, encoding="utf-8")
    head = _commit(repo, "restore migration")
    code, payload = _check(repo, base, head, [RECORD])
    assert code == 2
    assert not _baseline_result(payload)["passed"]


@pytest.mark.parametrize("version", [1, 2], ids=["v1", "v2"])
def test_removed_historical_receipt_is_detected_without_current_receipt(
    tmp_path: Path, version: int,
) -> None:
    repo, base = _repo(tmp_path, {RECORD: OLD})
    target = repo / RECORD
    receipt = _receipt(base) if version == 1 else _receipt_v2(base)
    make_record = _privacy_record if version == 1 else _privacy_record_v2
    target.write_text(make_record(receipt), encoding="utf-8")
    _commit(repo, "approved migration")
    target.write_text(_record(OLD), encoding="utf-8")
    head = _commit(repo, "remove all migration evidence from current record")
    _, payload = _check(repo, base, head, [RECORD])
    assert not _baseline_result(payload)["passed"]


def test_v1_receipt_cannot_be_upgraded_to_v2(tmp_path: Path) -> None:
    repo, base = _repo(tmp_path, {RECORD: OLD})
    target = repo / RECORD
    target.write_text(_privacy_record(_receipt(base)), encoding="utf-8")
    _commit(repo, "approved source-only migration")
    target.write_text(_privacy_record_v2(_receipt_v2(base)), encoding="utf-8")
    head = _commit(repo, "attempt receipt upgrade")
    code, payload = _check(repo, base, head, [RECORD])
    assert code == 2
    assert not _baseline_result(payload)["passed"]


@pytest.mark.parametrize("nested", [False, True])
def test_privacy_migration_custom_path_and_nested_root(tmp_path: Path, nested: bool) -> None:
    template = ".work/items/{slug}.record.md"
    path = ".work/items/alpha.record.md"
    repo, base = _repo(tmp_path, None if nested else {path: OLD}, task_path=template)
    root = repo
    if nested:
        root = repo / "project"
        root.mkdir()
        shutil.copyfile(repo / "agent-workflow.yaml", root / "agent-workflow.yaml")
        (root / path).parent.mkdir(parents=True)
        (root / path).write_text(_record(OLD), encoding="utf-8")
        base = _commit(repo, "nested baseline")
    (root / path).write_text(_privacy_record(_receipt(base, path)), encoding="utf-8")
    head = _commit(repo, "approved migration")
    code, payload = _check(root, base, head, [path])
    assert code in (0, 1), json.dumps(payload, indent=2)
    assert _baseline_result(payload, "alpha")["passed"]


def test_privacy_migration_requires_supplied_history_even_locally(tmp_path: Path) -> None:
    repo, base = _repo(tmp_path, {RECORD: OLD})
    (repo / RECORD).write_text(_privacy_record(_receipt(base)), encoding="utf-8")
    _commit(repo, "approved migration")
    result = subprocess.run([sys.executable, "-m", "core.checker", "--repo-root", str(repo), "--slug", "example"],
                            cwd=ROOT, env=dict(os.environ, PYTHONPATH=str(ROOT)), capture_output=True, text=True)
    assert result.returncode == 2
    assert not _baseline_result(json.loads(result.stdout))["passed"]


def test_ordinary_history_does_not_parse_unrelated_old_behavior_schema(tmp_path: Path) -> None:
    repo, base = _repo(tmp_path, {RECORD: OLD})
    target = repo / RECORD
    target.write_text(_record(OLD).replace("**State:**", "**Behavior changes:** legacy-not-json\n**State:**"), encoding="utf-8")
    _commit(repo, "legacy unrelated behavior field")
    target.write_text(_record(OLD), encoding="utf-8")
    head = _commit(repo, "current record")
    _, payload = _check(repo, base, head, [RECORD])
    assert _baseline_result(payload)["passed"]


def test_ambiguous_merge_cannot_introduce_privacy_migration(tmp_path: Path) -> None:
    repo, base = _repo(tmp_path, {RECORD: OLD})
    main = _git(repo, "branch", "--show-current")
    target = repo / RECORD
    _git(repo, "checkout", "-qb", "side")
    target.write_text(_record(OLD, context={**OLD, "scope": "Different parent scope"}), encoding="utf-8")
    _commit(repo, "different pre-redaction context")
    _git(repo, "checkout", main)
    (repo / "main.txt").write_text("main\n", encoding="utf-8")
    _commit(repo, "main change")
    _git(repo, "merge", "--no-commit", "--no-ff", "-s", "ours", "side")
    target.write_text(_privacy_record(_receipt(base)), encoding="utf-8")
    head = _commit(repo, "ambiguous merge migration")
    _, payload = _check(repo, base, head, [RECORD])
    assert not _baseline_result(payload)["passed"]


def test_parallel_pre_migration_branch_is_not_receipt_removal(tmp_path: Path) -> None:
    repo, base = _repo(tmp_path, {RECORD: OLD})
    main = _git(repo, "branch", "--show-current")
    target = repo / RECORD
    _git(repo, "checkout", "-qb", "side")
    target.write_text(_record(OLD).replace("**Approach:** example", "**Approach:** clarified"), encoding="utf-8")
    _commit(repo, "parallel pre-migration record")
    _git(repo, "checkout", main)
    good = _privacy_record(_receipt(base))
    target.write_text(good, encoding="utf-8")
    _commit(repo, "approved migration")
    _git(repo, "merge", "--no-commit", "--no-ff", "-s", "ours", "side")
    head = _commit(repo, "merge parallel history")
    _, payload = _check(repo, base, head, [RECORD])
    assert _baseline_result(payload)["passed"], json.dumps(payload, indent=2)


@pytest.mark.parametrize(("path", "source"), [
    (RECORD, SAFE_SOURCE),
    (".agent-workflow/tasks/board-appearance.md",
     "User-approved appearance design (privacy-redacted source)"),
])
def test_vendored_checker_accepts_approved_source_migration(tmp_path: Path, path: str, source: str) -> None:
    repo, base = _repo(tmp_path, {path: OLD})
    receipt = _receipt(base, path)
    receipt["replacements"]["source"] = source
    (repo / path).write_text(_privacy_record(receipt, baseline={**OLD, "source": source}), encoding="utf-8")
    head = _commit(repo, "approved migration")
    for vendored in (False, True):
        code, payload = _check(repo, base, head, [path], vendored=vendored)
        assert code in (0, 1), json.dumps(payload, indent=2)
        assert _baseline_result(payload, Path(path).stem)["passed"]


@pytest.mark.parametrize("renamed", [False, True])
@pytest.mark.parametrize("version", [1, 2], ids=["v1", "v2"])
def test_privacy_migration_cannot_repair_pre_migration_identity_loss(
    tmp_path: Path, renamed: bool, version: int,
) -> None:
    repo, anchor = _repo(tmp_path, {RECORD: OLD})
    target = repo / RECORD
    other_path = ".agent-workflow/tasks/temporary.md"
    if renamed:
        _git(repo, "mv", RECORD, other_path)
    else:
        target.unlink()
    _commit(repo, "remove original record identity")
    if renamed:
        _git(repo, "mv", other_path, RECORD)
    else:
        target.write_text(_record(OLD), encoding="utf-8")
    _commit(repo, "restore exact old baseline")
    receipt = _receipt(anchor) if version == 1 else _receipt_v2(anchor)
    make_record = _privacy_record if version == 1 else _privacy_record_v2
    target.write_text(make_record(receipt), encoding="utf-8")
    head = _commit(repo, "attempt source migration after identity loss")
    code, payload = _check(repo, anchor, head, [RECORD])
    assert code == 2
    predicate = _baseline_result(payload)
    assert not predicate["passed"]
    assert "deleted or renamed" in predicate["detail"]


def test_privacy_migration_identity_check_starts_at_authoritative_anchor(tmp_path: Path) -> None:
    repo, _ = _repo(tmp_path, {RECORD: OLD})
    target = repo / RECORD
    target.unlink()
    _commit(repo, "old deletion before authoritative baseline")
    target.write_text(_record(OLD), encoding="utf-8")
    anchor = _commit(repo, "new authoritative PR base")
    target.write_text(_privacy_record(_receipt(anchor)), encoding="utf-8")
    head = _commit(repo, "approved migration from current authority")
    code, payload = _check(repo, anchor, head, [RECORD])
    assert code in (0, 1), json.dumps(payload, indent=2)
    assert _baseline_result(payload)["passed"]


@pytest.mark.parametrize("intermediate", [
    None,
    {**OLD, "source": "Temporary synthetic source"},
    {**OLD, "scope": "Temporary baseline scope"},
], ids=["missing-baseline", "changed-source", "changed-functional-baseline"])
@pytest.mark.parametrize("version", [1, 2], ids=["v1", "v2"])
def test_privacy_migration_cannot_repair_restored_pre_migration_baseline(
    tmp_path: Path, intermediate: dict | None, version: int,
) -> None:
    repo, anchor = _repo(tmp_path, {RECORD: OLD})
    target = repo / RECORD
    target.write_text(_record(intermediate, context=OLD), encoding="utf-8")
    _commit(repo, "temporarily remove or change baseline")
    target.write_text(_record(OLD), encoding="utf-8")
    _commit(repo, "restore exact old baseline")
    receipt = _receipt(anchor) if version == 1 else _receipt_v2(anchor)
    make_record = _privacy_record if version == 1 else _privacy_record_v2
    target.write_text(make_record(receipt), encoding="utf-8")
    head = _commit(repo, "attempt source migration after baseline restoration")
    code, payload = _check(repo, anchor, head, [RECORD])
    assert code == 2
    predicate = _baseline_result(payload)
    assert not predicate["passed"]
    assert "pre-redaction baseline" in predicate["detail"]


@pytest.mark.parametrize("whitespace", ["\t", "\u2003", "\n"], ids=["tab", "em-space", "newline"])
@pytest.mark.parametrize("vendored", [False, True], ids=["source", "vendored"])
def test_privacy_receipt_label_whitespace_history(tmp_path: Path, whitespace: str, vendored: bool) -> None:
    repo, base = _repo(tmp_path, {RECORD: OLD})
    target = repo / RECORD
    migrated = _privacy_record(_receipt(base)).replace("**Baseline privacy migration:**",
        f"**{whitespace}Baseline privacy migration{whitespace}:**")
    target.write_text(migrated, encoding="utf-8")
    head = _commit(repo, "approved migration with parser-supported label whitespace")
    code, payload = _check(repo, base, head, [RECORD], vendored=vendored)
    assert code in (0, 1), json.dumps(payload, indent=2)
    assert _baseline_result(payload)["passed"]
    target.write_text(_record(OLD), encoding="utf-8")
    head = _commit(repo, "remove receipt and restore original baseline")
    code, payload = _check(repo, base, head, [RECORD], vendored=vendored)
    assert code == 2
    assert not _baseline_result(payload)["passed"]


def test_receipt_prose_candidate_does_not_parse_old_behavior_schema(tmp_path: Path) -> None:
    repo, base = _repo(tmp_path, {RECORD: OLD})
    target = repo / RECORD
    text = _record(OLD).replace("**State:**", "**Behavior changes:** legacy-not-json\n**State:**")
    target.write_text(text + "\nMention Baseline privacy migration in ordinary prose.\n", encoding="utf-8")
    _commit(repo, "prose mention with unrelated legacy behavior schema")
    target.write_text(_record(OLD), encoding="utf-8")
    head = _commit(repo, "current ordinary record")
    _, payload = _check(repo, base, head, [RECORD])
    assert _baseline_result(payload)["passed"]


def test_malformed_receipt_label_requires_history_without_refs(tmp_path: Path) -> None:
    repo, _ = _repo(tmp_path, {RECORD: OLD})
    text = _record(OLD).replace("**State:**", "**\u2003Baseline privacy migration\u2003:** not-json\n**State:**")
    (repo / RECORD).write_text(text, encoding="utf-8")
    result = subprocess.run([sys.executable, "-m", "core.checker", "--repo-root", str(repo), "--slug", "example"],
                            cwd=ROOT, env=dict(os.environ, PYTHONPATH=str(ROOT)), capture_output=True, text=True)
    assert result.returncode == 2
    predicate = _baseline_result(json.loads(result.stdout))
    assert not predicate["passed"]
    assert "requires valid PR base/head history" in predicate["detail"]


@pytest.mark.parametrize("vendored", [False, True], ids=["source", "vendored"])
@pytest.mark.parametrize("version", [1, 2], ids=["v1", "v2"])
def test_unambiguous_merge_can_introduce_privacy_receipt(
    tmp_path: Path, vendored: bool, version: int,
) -> None:
    repo, base = _repo(tmp_path, {RECORD: OLD})
    main = _git(repo, "branch", "--show-current")
    _git(repo, "checkout", "-qb", "side")
    (repo / "side.txt").write_text("side\n", encoding="utf-8")
    _commit(repo, "side change preserving record identity")
    _git(repo, "checkout", main)
    (repo / "main.txt").write_text("main\n", encoding="utf-8")
    _commit(repo, "main change preserving record identity")
    _git(repo, "merge", "--no-commit", "--no-ff", "side")
    receipt = _receipt(base) if version == 1 else _receipt_v2(base)
    make_record = _privacy_record if version == 1 else _privacy_record_v2
    (repo / RECORD).write_text(make_record(receipt), encoding="utf-8")
    head = _commit(repo, "unambiguous merge migration")
    code, payload = _check(repo, base, head, [RECORD], vendored=vendored)
    assert code in (0, 1), json.dumps(payload, indent=2)
    assert _baseline_result(payload)["passed"]


@pytest.mark.parametrize("activation", ["markers", "delimiters", "nul-prose"])
@pytest.mark.parametrize("vendored", [False, True], ids=["source", "vendored"])
def test_receipt_activation_without_phrase_change(tmp_path: Path, activation: str, vendored: bool) -> None:
    repo, base = _repo(tmp_path, {RECORD: OLD})
    target = repo / RECORD
    receipt_json = json.dumps(_receipt(base))
    end = "<!-- agent-workflow:end -->"
    outside_prose = "\nSynthetic outside prose with NUL: \x00\n" if activation == "nul-prose" else ""
    if activation == "nul-prose":
        before = _record(OLD) + outside_prose
        activated = _privacy_record(_receipt(base)) + outside_prose
    elif activation == "markers":
        before = _record(OLD) + f"**Baseline privacy migration:** {receipt_json}\n"
        activated = before.replace(end + "\n", "") + end + "\n"
    else:
        before = _record(OLD).replace("**State:**",
            f"**\nBaseline privacy migration\n!! {receipt_json}\n**State:**")
        activated = before.replace("\n!! ", "\n:** ")
    target.write_text(before, encoding="utf-8")
    _commit(repo, "prepare unchanged phrase outside a receipt field")
    activated = activated.replace(json.dumps(OLD), json.dumps({**OLD, "source": SAFE_SOURCE}))
    target.write_text(activated, encoding="utf-8")
    head = _commit(repo, "activate receipt by marker or delimiter change")
    code, payload = _check(repo, base, head, [RECORD], vendored=vendored)
    assert code in (0, 1), json.dumps(payload, indent=2)
    assert _baseline_result(payload)["passed"]
    target.write_text(_record(OLD) + outside_prose, encoding="utf-8")
    head = _commit(repo, "remove activated receipt and restore original baseline")
    code, payload = _check(repo, base, head, [RECORD], vendored=vendored)
    assert code == 2
    assert not _baseline_result(payload)["passed"]


@pytest.mark.parametrize("vendored", [False, True], ids=["source", "vendored"])
def test_privacy_history_uses_literal_configured_path(tmp_path: Path, vendored: bool) -> None:
    path = ".work/[items]/example.md"
    repo, base = _repo(tmp_path, {path: OLD}, task_path=".work/[items]/{slug}.md")
    target = repo / path
    target.write_text(_privacy_record(_receipt(base, path)), encoding="utf-8")
    head = _commit(repo, "approved migration at literal bracket path")
    code, payload = _check(repo, base, head, [path], vendored=vendored)
    assert code in (0, 1), json.dumps(payload, indent=2)
    assert _baseline_result(payload)["passed"]
    target.write_text(_record(OLD), encoding="utf-8")
    head = _commit(repo, "remove receipt and restore literal-path baseline")
    code, payload = _check(repo, base, head, [path], vendored=vendored)
    assert code == 2
    assert not _baseline_result(payload)["passed"]
