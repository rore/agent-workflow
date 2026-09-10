from __future__ import annotations

import importlib.util
import io
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "scripts" / "agent-workflow-runtime.py"
GIT = shutil.which("git")
assert GIT


def _run_git(repo: Path, *args: str) -> None:
    subprocess.run([GIT, *args], cwd=repo, check=True, capture_output=True)


def _record() -> str:
    return (ROOT / "tests" / "fixtures" / "work-record" / "expanded-pass" / "work-record.md").read_text(encoding="utf-8")


def _config(task_path: str = ".agent-workflow/tasks/{slug}.md", *, direct_default_allowed: bool = False) -> str:
    return f'''version: 1
project:
  name: runtime-test
workRecord:
  backend: local
  local:
    taskPath: "{task_path}"
redline: required
redlineVerdictPath: redline-verdict.json
applicability:
  documentationOnly:
    paths:
      - "docs/"
      - "README.md"
    workflowRequired: false
    directDefaultBranchAllowed: {str(direct_default_allowed).lower()}
'''


def _policy() -> str:
    return '''version: 1
project:
  name: runtime-test
zones:
  red:
    - path: agent-workflow.yaml
      reason: workflow configuration
      checkpoint: architecture-review
  blue:
    - path: docs/**
      reason: documentation
    - path: README.md
      reason: documentation
    - path: src/**
      reason: implementation fixture
excludes:
  - .agent-workflow/**
  - .work/**
modes:
  default: shadow
  perCheck:
    boundary_violation: binding
'''


def _repo(tmp_path: Path, *, task_path: str = ".agent-workflow/tasks/{slug}.md", direct_default_allowed: bool = False) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "scripts").mkdir()
    (repo / "core").mkdir()
    shutil.copy2(RUNTIME, repo / "scripts" / RUNTIME.name)
    shutil.copytree(ROOT / "core" / "checker", repo / "core" / "checker")
    shutil.copytree(ROOT / "core" / "config", repo / "core" / "config")
    shutil.copytree(ROOT / "core" / "schema", repo / "core" / "schema")
    shutil.copytree(ROOT / "core" / "work_record", repo / "core" / "work_record")
    shutil.copytree(ROOT / "core" / "agent-redline", repo / "core" / "agent-redline")
    (repo / "agent-workflow.yaml").write_text(_config(task_path, direct_default_allowed=direct_default_allowed), encoding="utf-8")
    (repo / "agent-redline-policy.yaml").write_text(_policy(), encoding="utf-8")
    (repo / "README.md").write_text("baseline\n", encoding="utf-8")
    _run_git(repo, "init", "-q", "-b", "main")
    _run_git(repo, "config", "user.email", "test@example.com")
    _run_git(repo, "config", "user.name", "Runtime Test")
    _run_git(repo, "add", ".")
    _run_git(repo, "commit", "-qm", "baseline")
    origin = tmp_path / "origin.git"
    _run_git(tmp_path, "init", "--bare", "-q", str(origin))
    _run_git(repo, "remote", "add", "origin", str(origin))
    _run_git(repo, "push", "-q", "origin", "main")
    _run_git(origin, "symbolic-ref", "HEAD", "refs/heads/main")
    _run_git(repo, "fetch", "-q", "origin")
    _run_git(repo, "switch", "-qc", "feat/runtime-guard")
    return repo


def _invoke(repo: Path, runtime: str, payload: object, *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(repo / "scripts" / RUNTIME.name), "--runtime", runtime],
        cwd=repo,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )


def _invoke_default(
    repo: Path, payload: object, status: str, monkeypatch: pytest.MonkeyPatch
) -> int:
    spec = importlib.util.spec_from_file_location("runtime_guard_under_test", RUNTIME)
    assert spec and spec.loader
    runtime = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runtime)
    verdict = {
        "records": [{
            "slug": "<documentation-only>",
            "predicates": [{
                "name": "workflow.applicability",
                "passed": True,
                "detail": "Direct-default-branch is allowed by the fresh unprotected result.",
            }],
        }]
    }
    def checker_decision(_root: Path, paths: list[str], _slug: str, _is_default: bool):
        documentation_only = all(
            path.startswith("docs/") or path == "README.md" for path in paths
        )
        return (0, verdict) if status == "unprotected" and documentation_only else (2, {})

    monkeypatch.setattr(runtime, "_checker_decision", checker_decision)
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    return runtime.main(["--runtime", "codex"])


def _payload(repo: Path, path: str, *, cwd: Path | None = None) -> dict:
    return {
        "tool_name": "write",
        "cwd": str(cwd or repo),
        "tool_input": {"file_path": str(repo / path)},
    }


def _patch_payload(repo: Path, patch: str, *, cwd: Path | None = None) -> dict:
    return {
        "tool_name": "apply_patch",
        "cwd": str(cwd or repo),
        "tool_input": {"patchText": patch},
    }


@pytest.mark.parametrize("runtime", ["claude", "codex", "opencode"])
@pytest.mark.parametrize("state,expected", [("missing", 2), ("not-ready", 2), ("ready", 0)])
def test_all_runtimes_share_missing_not_ready_ready_decisions(
    tmp_path: Path, runtime: str, state: str, expected: int
) -> None:
    repo = _repo(tmp_path)
    record = repo / ".agent-workflow" / "tasks" / "runtime-guard.md"
    if state == "not-ready":
        record.parent.mkdir(parents=True)
        record.write_text(_record().replace("Ready to implement", "Planning"), encoding="utf-8")
    elif state == "ready":
        record.parent.mkdir(parents=True)
        record.write_text(_record(), encoding="utf-8")
    result = _invoke(repo, runtime, _payload(repo, "src/app.py"))
    assert result.returncode == expected, result.stderr


@pytest.mark.parametrize("runtime", ["claude", "codex", "opencode"])
def test_work_record_recovery_only_allowed_but_mixed_recovery_and_code_denied(
    tmp_path: Path, runtime: str
) -> None:
    repo = _repo(tmp_path)
    record = ".agent-workflow/tasks/runtime-guard.md"
    allowed = _invoke(repo, runtime, _payload(repo, record))
    assert allowed.returncode == 0
    mixed = _invoke(
        repo,
        runtime,
        _patch_payload(
            repo,
            "*** Begin Patch\n"
            "*** Add File: .agent-workflow/tasks/runtime-guard.md\n"
            "+repair\n"
            "*** Add File: src/app.py\n"
            "+code\n"
            "*** End Patch",
        ),
    )
    assert mixed.returncode == 2


def test_documentation_only_is_allowed_but_governance_mix_is_denied(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    result = _invoke(repo, "codex", _payload(repo, "docs/guide.md"))
    assert result.returncode == 0
    result = _invoke(
        repo,
        "codex",
        _patch_payload(
            repo,
            "*** Begin Patch\n"
            "*** Add File: docs/guide.md\n"
            "+docs\n"
            "*** Update File: agent-workflow.yaml\n"
            "*** End Patch",
        ),
    )
    assert result.returncode == 2


def test_custom_task_path_and_nested_cwd_are_resolved(tmp_path: Path) -> None:
    repo = _repo(tmp_path, task_path=".work/items/{slug}.record.md")
    record = repo / ".work" / "items" / "runtime-guard.record.md"
    record.parent.mkdir(parents=True)
    record.write_text(_record(), encoding="utf-8")
    nested = repo / "nested" / "cwd"
    nested.mkdir(parents=True)
    result = _invoke(repo, "opencode", _payload(repo, "src/app.py", cwd=nested))
    assert result.returncode == 0


def test_apply_patch_extracts_update_and_move_paths(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    payload = _patch_payload(repo, "*** Begin Patch\n*** Update File: docs/a.md\n*** Move to: docs/b.md\n*** End Patch")
    result = _invoke(repo, "claude", payload)
    assert result.returncode == 0


def test_malformed_supported_payload_degrades_fail_open(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    result = _invoke(repo, "codex", {"tool_name": "write", "cwd": str(repo), "tool_input": {}})
    assert result.returncode == 0
    assert "DEGRADED" in result.stderr


@pytest.mark.parametrize(
    "status,expected",
    [("unprotected", 0), ("protected", 2), ("unavailable", 2)],
)
def test_default_branch_documentation_requires_fresh_unprotected_result(
    tmp_path: Path, status: str, expected: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _repo(tmp_path, direct_default_allowed=True)
    _run_git(repo, "switch", "-q", "main")
    result = _invoke_default(repo, _payload(repo, "docs/guide.md"), status, monkeypatch)
    assert result == expected


def test_default_branch_scope_includes_unpublished_code(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _repo(tmp_path, direct_default_allowed=True)
    _run_git(repo, "switch", "-q", "main")
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    _run_git(repo, "add", "src/app.py")
    _run_git(repo, "commit", "-qm", "unpublished code")
    result = _invoke_default(
        repo, _payload(repo, "docs/guide.md"), "unprotected", monkeypatch
    )
    assert result == 2


def test_default_branch_ready_record_never_allows_code(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _repo(tmp_path, direct_default_allowed=True)
    _run_git(repo, "switch", "-q", "main")
    record = repo / ".agent-workflow" / "tasks" / "runtime-guard.md"
    record.parent.mkdir(parents=True)
    record.write_text(_record(), encoding="utf-8")
    result = _invoke_default(
        repo, _payload(repo, "src/app.py"), "unprotected", monkeypatch
    )
    assert result == 2


def test_unrelated_ready_record_does_not_satisfy_current_branch(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    unrelated = repo / ".agent-workflow" / "tasks" / "unrelated.md"
    unrelated.parent.mkdir(parents=True)
    unrelated.write_text(_record(), encoding="utf-8")
    result = _invoke(repo, "codex", _payload(repo, "src/app.py"))
    assert result.returncode == 2


def test_non_ascii_documentation_path_survives_shared_input(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    result = _invoke(repo, "codex", _payload(repo, "docs/מדריך.md"))
    assert result.returncode == 0


def test_unknown_actual_default_branch_denies_documentation_only(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path, direct_default_allowed=True)
    _run_git(repo, "remote", "remove", "origin")
    _run_git(repo, "switch", "-q", "-c", "trunk")
    result = _invoke(repo, "codex", _payload(repo, "docs/guide.md"))
    assert result.returncode == 2
    assert "DEGRADED" not in result.stderr


def test_missing_merge_base_denies_incomplete_committed_scope(tmp_path: Path) -> None:
    repo = _repo(tmp_path, direct_default_allowed=True)
    (repo / "src").mkdir()
    (repo / "src" / "committed.py").write_text("x = 1\n", encoding="utf-8")
    _run_git(repo, "add", "src/committed.py")
    _run_git(repo, "commit", "-qm", "committed code")
    _run_git(repo, "branch", "-D", "main")
    result = _invoke(repo, "codex", _payload(repo, "docs/guide.md"))
    assert result.returncode == 2
    assert "DEGRADED" not in result.stderr


def test_nested_cwd_resolves_relative_patch_under_src_and_denies_it(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path)
    nested = repo / "src"
    nested.mkdir()
    result = _invoke(
        repo,
        "codex",
        _patch_payload(
            repo,
            "*** Begin Patch\n"
            "*** Add File: docs/guide.md\n"
            "+code-adjacent docs\n"
            "*** End Patch",
            cwd=nested,
        ),
    )
    assert result.returncode == 2


@pytest.mark.parametrize("config_state", ["missing", "invalid", "schema-invalid"])
def test_missing_or_invalid_workflow_config_denies_not_degrades(
    tmp_path: Path, config_state: str
) -> None:
    repo = _repo(tmp_path)
    config = repo / "agent-workflow.yaml"
    if config_state == "missing":
        config.unlink()
    elif config_state == "invalid":
        config.write_text("not: [valid\n", encoding="utf-8")
    else:
        config.write_text(_config().replace("version: 1", "version: 999"), encoding="utf-8")
    result = _invoke(repo, "codex", _payload(repo, "src/app.py"))
    assert result.returncode == 2
    assert "DEGRADED" not in result.stderr


def test_missing_redline_policy_denies_not_degrades(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    (repo / "agent-redline-policy.yaml").unlink()
    result = _invoke(repo, "codex", _payload(repo, "src/app.py"))
    assert result.returncode == 2
    assert "DEGRADED" not in result.stderr


def test_implementation_readiness_cannot_be_waived(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    record = repo / ".agent-workflow" / "tasks" / "runtime-guard.md"
    record.parent.mkdir(parents=True)
    record.write_text(
        _record().replace(
            "**State:** Ready to implement",
            "**Exceptions:**\n"
            "- rule: workrecord.implementation_ready\n"
            "  reason: test waiver\n"
            "  scope: this test\n"
            "  approver: reviewer\n"
            "  compensating_validation: none\n\n"
            "**State:** Ready for review",
        ),
        encoding="utf-8",
    )
    result = _invoke(repo, "codex", _payload(repo, "src/app.py"))
    assert result.returncode == 2


def test_checker_failure_after_evaluation_starts_denies(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    repo = _repo(tmp_path)
    spec = importlib.util.spec_from_file_location("runtime_guard_under_test", RUNTIME)
    assert spec and spec.loader
    runtime = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runtime)
    monkeypatch.setattr(
        runtime,
        "_checker_decision",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("checker crashed")),
    )
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(_payload(repo, "src/app.py"))))
    assert runtime.main(["--runtime", "codex"]) == 2
    assert "DENY: workflow evaluation failed: checker crashed" in capsys.readouterr().err


def test_invalid_checker_verdict_is_evidence_error() -> None:
    spec = importlib.util.spec_from_file_location("runtime_guard_under_test", RUNTIME)
    assert spec and spec.loader
    runtime = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runtime)
    checked = subprocess.CompletedProcess([], 0, stdout="{}", stderr="")
    with pytest.raises(runtime.EvidenceError):
        runtime._checked_payload(checked)


def test_git_scope_collection_failure_is_evidence_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spec = importlib.util.spec_from_file_location("runtime_guard_under_test", RUNTIME)
    assert spec and spec.loader
    runtime = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runtime)
    failed = subprocess.CompletedProcess([], 1, stdout=b"", stderr=b"fatal")
    monkeypatch.setattr(runtime.subprocess, "run", lambda *args, **kwargs: failed)
    with pytest.raises(runtime.EvidenceError):
        runtime._git_z(tmp_path, ["status", "--porcelain=v1", "-z"])


def test_complete_scope_union_includes_committed_dirty_untracked_and_prospective(
    tmp_path: Path,
) -> None:
    repo = _repo(tmp_path)
    (repo / "docs" ).mkdir()
    (repo / "docs" / "committed.md").write_text("committed\n", encoding="utf-8")
    _run_git(repo, "add", "docs/committed.md")
    _run_git(repo, "commit", "-qm", "docs change")
    (repo / "README.md").write_text("dirty\n", encoding="utf-8")
    (repo / "docs" / "untracked.md").write_text("untracked\n", encoding="utf-8")
    (repo / "agent-workflow.yaml").write_text(
        _config(direct_default_allowed=False) + "# dirty governance\n", encoding="utf-8"
    )
    result = _invoke(repo, "codex", _payload(repo, "docs/prospective.md"))
    assert result.returncode == 2
