"""Caller-level applicability matrix: lossless diff input -> checker verdict."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from core.checker.checker import discover_slugs_from_changed_files, main


def _config(*, workflow_required: bool = False) -> str:
    return f"""version: 1
project: {{name: example}}
workRecord:
  backend: local
  local:
    taskPath: ".agent-workflow/tasks/{{slug}}.md"
redline: required
redlineVerdictPath: redline-verdict.json
applicability:
  documentationOnly:
    paths: [docs/, roadmap/, README.md]
    workflowRequired: {str(workflow_required).lower()}
    directDefaultBranchAllowed: true
"""


def _redline(paths: list[str]) -> dict:
    return {
        "verdict": "BLUE",
        "zones": {"blue": paths, "gray": [], "red": [], "watch": []},
        "boundaryViolations": [],
        "checkpoints": [],
        "apiChanges": {"detected": False},
        "schemaChanges": {"detected": False},
        "securityChanges": {"detected": False},
        "runtimeConfigChanges": {"detected": False},
    }


def _run(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    paths: list[str],
    *,
    verdict: dict | None = None,
    workflow_required: bool = False,
    legacy: bool = False,
    check_protection: bool = False,
) -> tuple[int, dict]:
    (tmp_path / "agent-workflow.yaml").write_text(
        _config(workflow_required=workflow_required), encoding="utf-8"
    )
    if verdict is not None:
        (tmp_path / "redline-verdict.json").write_text(
            json.dumps(verdict), encoding="utf-8"
        )
    changed = tmp_path / ("changed.txt" if legacy else "changed.z")
    if legacy:
        changed.write_text("\n".join(paths) + "\n", encoding="utf-8")
        option = "--changed-files"
    else:
        changed.write_bytes(b"\0".join(path.encode("utf-8") for path in paths) + b"\0")
        option = "--changed-files-z"
    args = ["--repo-root", str(tmp_path), option, str(changed)]
    if check_protection:
        args.append("--check-default-branch-protection")
    code = main(args)
    return code, json.loads(capsys.readouterr().out)


@pytest.mark.parametrize(
    "paths,expected",
    [
        (["docs/guide.md"], 0),
        (["README.md"], 0),
        (["roadmap/current.md"], 0),
        (["docs/old.md", "docs/new.md"], 0),
        (["docs/用户 guide/line\nbreak.md"], 0),
        (["docs/guide.md", "src/app.py"], 2),
        (["docs/SPEC.md"], 2),
        (["docs/guide.md", "AGENTS.md"], 2),
        (["docs/old.md", "src/new.py"], 2),
    ],
)
def test_complete_path_matrix(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    paths: list[str],
    expected: int,
) -> None:
    code, payload = _run(tmp_path, capsys, paths, verdict=_redline(paths))
    assert code == expected
    applicability = [
        predicate
        for record in payload["records"]
        for predicate in record["predicates"]
        if predicate["name"] == "workflow.applicability"
    ]
    assert applicability and applicability[0]["passed"] is (expected == 0)


@pytest.mark.parametrize("failure", ["missing", "partial", "watch"])
def test_risk_evidence_failures_deny_exemption(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    failure: str,
) -> None:
    paths = ["docs/guide.md"]
    verdict = None if failure == "missing" else _redline(paths)
    if failure == "partial":
        assert verdict is not None
        del verdict["schemaChanges"]
    if failure == "watch":
        assert verdict is not None
        verdict["zones"]["watch"] = paths
    code, _ = _run(tmp_path, capsys, paths, verdict=verdict)
    assert code == 2


def test_legacy_newline_input_never_grants_exemption(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    paths = ["docs/guide.md"]
    code, payload = _run(tmp_path, capsys, paths, verdict=_redline(paths), legacy=True)
    assert code == 2
    assert not any(
        predicate["name"] == "workflow.applicability" and predicate["passed"]
        for record in payload["records"] for predicate in record["predicates"]
    )


def test_workflow_required_setting_wins(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    paths = ["docs/guide.md"]
    code, _ = _run(
        tmp_path, capsys, paths, verdict=_redline(paths), workflow_required=True
    )
    assert code == 2


def test_duplicate_paths_deny_exemption(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    paths = ["docs/guide.md", "docs/guide.md"]
    code, _ = _run(tmp_path, capsys, paths, verdict=_redline(paths))
    assert code == 2


def test_incomplete_nul_input_fails_closed(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "agent-workflow.yaml").write_text(_config(), encoding="utf-8")
    changed = tmp_path / "changed.z"
    changed.write_bytes(b"docs/guide.md")
    code = main(["--repo-root", str(tmp_path), "--changed-files-z", str(changed)])
    payload = json.loads(capsys.readouterr().out)
    assert code == 2
    assert payload["records"][0]["predicates"][0]["name"] == "changed_paths.complete"


def test_custom_task_path_is_discovered(tmp_path: Path) -> None:
    record = tmp_path / ".work" / "items" / "alpha.record.md"
    record.parent.mkdir(parents=True)
    record.write_text("placeholder", encoding="utf-8")
    changed = tmp_path / "changed.z"
    changed.write_bytes(b".work/items/alpha.record.md\0")
    assert discover_slugs_from_changed_files(
        tmp_path,
        changed,
        ".work/items/{slug}.record.md",
        nul_delimited=True,
    ) == ["alpha"]

@pytest.mark.parametrize(
    "workflow",
    [
        Path(".github/workflows/agent-workflow.yml"),
        Path("core/templates/.github/workflows/agent-workflow.yml.template"),
    ],
)
def test_ci_uses_one_lossless_path_contract_and_validates_outputs(workflow: Path) -> None:
    text = workflow.read_text(encoding="utf-8")
    assert text.count("git diff --name-only -z --no-renames") == 2
    assert "--changed-files-z changed-files.z" in text
    assert "redline did not produce valid verdict JSON" in text
    assert "checker did not produce valid verdict JSON" in text

@pytest.mark.parametrize(
    "status,direct_allowed",
    [("unprotected", True), ("protected", False), ("unavailable", False)],
)
def test_live_protection_result_only_controls_lowest_priority_direct_branch(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    status: str,
    direct_allowed: bool,
) -> None:
    monkeypatch.setattr(
        "core.checker.checker._github_default_branch_protection", lambda _root: status
    )
    paths = ["docs/guide.md"]
    code, payload = _run(
        tmp_path, capsys, paths, verdict=_redline(paths), check_protection=True
    )
    assert code == 0
    detail = payload["records"][0]["predicates"][0]["detail"]
    assert ("is allowed" in detail) is direct_allowed


def test_live_protection_checks_actual_default_branch_and_rulesets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import subprocess
    from core.checker.checker import _github_default_branch_protection

    outputs = iter([
        {"nameWithOwner": "org/repo"},
        {"default_branch": "release/v2"},
        {"protected": False},
        [{"type": "pull_request"}],
    ])
    calls: list[list[str]] = []

    def fake_run(args, **_kwargs):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, json.dumps(next(outputs)), "")

    monkeypatch.setattr("core.checker.checker.subprocess.run", fake_run)
    assert _github_default_branch_protection(tmp_path) == "protected"
    assert calls[2][-1].endswith("branches/release%2Fv2")
    assert calls[3][-1].endswith("rules/branches/release%2Fv2")

def test_changed_deleted_record_under_approved_custom_layout_still_blocks(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "agent-workflow.yaml").write_text(
        """version: 1
project: {name: example}
workRecord:
  backend: local
  local:
    taskPath: ".work/items/{slug}.record.md"
redline: required
redlineVerdictPath: redline-verdict.json
applicability:
  documentationOnly:
    paths: [.work/]
    workflowRequired: false
    directDefaultBranchAllowed: true
""",
        encoding="utf-8",
    )
    paths = [".work/items/deleted.record.md"]
    (tmp_path / "changed.z").write_bytes(paths[0].encode() + b"\0")
    (tmp_path / "redline-verdict.json").write_text(
        json.dumps(_redline(paths)), encoding="utf-8"
    )
    code = main([
        "--repo-root", str(tmp_path), "--changed-files-z", str(tmp_path / "changed.z")
    ])
    payload = json.loads(capsys.readouterr().out)
    assert code == 2
    names = [p["name"] for r in payload["records"] for p in r["predicates"]]
    assert "workflow.applicability" in names
    assert "workrecord.required_for_branch_changes" in names

def test_local_actual_scope_includes_staged_unstaged_and_untracked(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "agent-workflow.yaml").write_text(_config(), encoding="utf-8")
    (repo / ".gitignore").write_text("redline-verdict.json\nchanged.z\n", encoding="utf-8")
    (repo / "docs").mkdir()
    (repo / "docs" / "tracked.md").write_text("old\n", encoding="utf-8")
    (repo / "README.md").write_text("old\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "baseline"], cwd=repo, check=True)

    (repo / "docs" / "tracked.md").write_text("unstaged\n", encoding="utf-8")
    (repo / "README.md").write_text("staged\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
    (repo / "roadmap").mkdir()
    (repo / "roadmap" / "new.md").write_text("untracked\n", encoding="utf-8")

    def actual_paths() -> list[str]:
        tracked = subprocess.run(
            ["git", "diff", "--name-only", "-z", "--no-renames", "HEAD"],
            cwd=repo, check=True, capture_output=True,
        ).stdout
        untracked = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "-z"],
            cwd=repo, check=True, capture_output=True,
        ).stdout
        raw = tracked + untracked
        (repo / "changed.z").write_bytes(raw)
        return [part.decode() for part in raw.split(b"\0") if part]

    paths = actual_paths()
    assert set(paths) == {"README.md", "docs/tracked.md", "roadmap/new.md"}
    (repo / "redline-verdict.json").write_text(json.dumps(_redline(paths)), encoding="utf-8")
    assert main(["--repo-root", str(repo), "--changed-files-z", str(repo / "changed.z")]) == 0
    capsys.readouterr()

    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    paths = actual_paths()
    (repo / "redline-verdict.json").write_text(json.dumps(_redline(paths)), encoding="utf-8")
    assert main(["--repo-root", str(repo), "--changed-files-z", str(repo / "changed.z")]) == 2
    capsys.readouterr()

def test_directory_or_submodule_path_is_not_treated_as_documentation(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    paths = ["docs/external"]
    (tmp_path / "docs" / "external").mkdir(parents=True)
    code, _ = _run(tmp_path, capsys, paths, verdict=_redline(paths))
    assert code == 2