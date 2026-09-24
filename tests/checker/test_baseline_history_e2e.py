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


def _commit(repo: Path, message: str) -> str:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", message)
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
