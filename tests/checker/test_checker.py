"""Golden tests for the CI checker.

Each scenario lives in its own directory under ``tests/checker/``:

    tests/checker/<scenario>/
    ├── README.md            (human note describing the scenario)
    ├── repo/                (fixture repository the checker runs against)
    │   ├── agent-workflow.yaml
    │   └── .agent-workflow/tasks/<slug>.md   (may be absent for missing-record scenarios)
    └── expected-verdict.json

The expected verdict is structural — only the fields a regression
must lock are checked, not human-readable details. This keeps the
goldens readable and resilient to detail-message tweaks while still
catching real behaviour changes (status flipped, predicate added or
removed, exit code shifted).

Slice 0 reshaped the verdict from ``status + predicates[]`` to
``status + records[{slug, status, predicates[]}]``. Goldens carry the
new shape; legacy ``predicates`` at the top level is no longer accepted.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.checker import run_checker, run_checker_multi
from core.checker.checker import discover_slugs_from_changed_files

CHECKER_DIR = Path(__file__).resolve().parent
SCENARIO_ROOTS = sorted(
    p for p in CHECKER_DIR.iterdir()
    if p.is_dir() and (p / "expected-verdict.json").exists()
)


@pytest.mark.parametrize("scenario_dir", SCENARIO_ROOTS, ids=lambda p: p.name)
def test_scenario_matches_golden(scenario_dir: Path) -> None:
    expected = json.loads((scenario_dir / "expected-verdict.json").read_text(encoding="utf-8"))
    repo_root = scenario_dir / "repo"

    # Multi-record golden: the expected file lists ``slugs`` (a list)
    # rather than a single ``slug``. Single-record goldens keep the old
    # ``slug`` field — the test handles both so existing scenarios stay
    # one-record without bloating their JSON.
    if "slugs" in expected:
        slugs = list(expected["slugs"])
        actual = run_checker_multi(repo_root, slugs).to_dict()
    else:
        slug = expected["slug"]
        actual = run_checker(repo_root, slug).to_dict()

    # Top-level shape: status + exit_code.
    assert actual["status"] == expected["status"], (
        f"{scenario_dir.name}: status differed: "
        f"expected {expected['status']!r}, got {actual['status']!r}"
    )
    assert actual["exit_code"] == expected["exit_code"]

    # Records: same slugs in same order; for each record, predicate
    # list matches (names, passed, blocking — detail strings are not
    # compared so wording can refine without rewriting goldens).
    actual_records = [
        {
            "slug": r["slug"],
            "status": r["status"],
            "predicates": [
                {"name": p["name"], "passed": p["passed"], "blocking": p["blocking"]}
                for p in r["predicates"]
            ],
        }
        for r in actual["records"]
    ]
    assert actual_records == expected["records"], (
        f"{scenario_dir.name}: records differed.\n"
        f"expected: {json.dumps(expected['records'], indent=2)}\n"
        f"actual:   {json.dumps(actual_records, indent=2)}"
    )


def _dogfooded_slugs() -> list[str]:
    """Every per-task Work Record under .agent-workflow/tasks/ in this repo.

    Retained as a public helper for ad-hoc scripts that want to enumerate
    the dev repo's Work Records. The previous parametrised dogfood test
    (``test_dev_repos_own_work_record_passes_checker``) was removed per
    DECISIONS 2026-06-24: the curated scenarios under ``tests/checker/*/``
    already cover the predicate matrix (one fixture per shape × state ×
    representative predicate), and per-PR CI provides the live "this
    record passes the checker" gate. Live-globbing the tasks directory
    at test-collection time coupled the test surface to historical
    engineering activity and made schema evolution hostile to records
    that pre-dated a tightening.
    """
    repo_root = Path(__file__).resolve().parents[2]
    tasks_dir = repo_root / ".agent-workflow" / "tasks"
    if not tasks_dir.exists():
        return []
    return sorted(
        p.stem for p in tasks_dir.glob("*.md")
        if p.name.lower() != "readme.md"
    )


# ---------------------------------------------------------------------------
# discover_slugs_from_changed_files — slice 0
# ---------------------------------------------------------------------------


def test_discover_slugs_picks_up_changed_task_files(tmp_path: Path) -> None:
    """Standard case: two Work Records in the changed-files list."""
    tasks = tmp_path / ".agent-workflow" / "tasks"
    tasks.mkdir(parents=True)
    (tasks / "alpha.md").write_text("placeholder", encoding="utf-8")
    (tasks / "bravo.md").write_text("placeholder", encoding="utf-8")
    changed = tmp_path / "changed-files.txt"
    changed.write_text(
        ".agent-workflow/tasks/alpha.md\n"
        ".agent-workflow/tasks/bravo.md\n"
        "core/checker/checker.py\n",
        encoding="utf-8",
    )
    assert discover_slugs_from_changed_files(tmp_path, changed) == ["alpha", "bravo"]


def test_discover_slugs_filters_readme_and_dotfiles(tmp_path: Path) -> None:
    """README.md and dotfiles never count as Work Records."""
    tasks = tmp_path / ".agent-workflow" / "tasks"
    tasks.mkdir(parents=True)
    (tasks / "alpha.md").write_text("placeholder", encoding="utf-8")
    (tasks / "README.md").write_text("docs", encoding="utf-8")
    (tasks / ".hidden.md").write_text("hidden", encoding="utf-8")
    changed = tmp_path / "changed-files.txt"
    changed.write_text(
        ".agent-workflow/tasks/README.md\n"
        ".agent-workflow/tasks/.hidden.md\n"
        ".agent-workflow/tasks/alpha.md\n",
        encoding="utf-8",
    )
    assert discover_slugs_from_changed_files(tmp_path, changed) == ["alpha"]


def test_discover_slugs_skips_deleted_files(tmp_path: Path) -> None:
    """Deleted files appear in git diff output but should not be checked."""
    tasks = tmp_path / ".agent-workflow" / "tasks"
    tasks.mkdir(parents=True)
    (tasks / "alpha.md").write_text("placeholder", encoding="utf-8")
    # bravo.md is referenced as changed but does not exist on disk
    # (deleted in this PR).
    changed = tmp_path / "changed-files.txt"
    changed.write_text(
        ".agent-workflow/tasks/alpha.md\n"
        ".agent-workflow/tasks/bravo.md\n",
        encoding="utf-8",
    )
    assert discover_slugs_from_changed_files(tmp_path, changed) == ["alpha"]


def test_discover_slugs_dedups(tmp_path: Path) -> None:
    """A path listed twice produces one slug."""
    tasks = tmp_path / ".agent-workflow" / "tasks"
    tasks.mkdir(parents=True)
    (tasks / "alpha.md").write_text("placeholder", encoding="utf-8")
    changed = tmp_path / "changed-files.txt"
    changed.write_text(
        ".agent-workflow/tasks/alpha.md\n"
        ".agent-workflow/tasks/alpha.md\n",
        encoding="utf-8",
    )
    assert discover_slugs_from_changed_files(tmp_path, changed) == ["alpha"]


def test_discover_slugs_ignores_non_task_paths(tmp_path: Path) -> None:
    """Paths outside .agent-workflow/tasks/ are ignored."""
    tasks = tmp_path / ".agent-workflow" / "tasks"
    tasks.mkdir(parents=True)
    (tasks / "alpha.md").write_text("placeholder", encoding="utf-8")
    changed = tmp_path / "changed-files.txt"
    changed.write_text(
        "core/checker/checker.py\n"
        "docs/SPEC.md\n"
        ".agent-workflow/tasks/alpha.md\n",
        encoding="utf-8",
    )
    assert discover_slugs_from_changed_files(tmp_path, changed) == ["alpha"]


def test_discover_slugs_ignores_nested_subdirs(tmp_path: Path) -> None:
    """Tasks live flat under the directory; nested .md files are not records."""
    tasks = tmp_path / ".agent-workflow" / "tasks"
    nested = tasks / "subdir"
    nested.mkdir(parents=True)
    (tasks / "alpha.md").write_text("placeholder", encoding="utf-8")
    (nested / "beta.md").write_text("placeholder", encoding="utf-8")
    changed = tmp_path / "changed-files.txt"
    changed.write_text(
        ".agent-workflow/tasks/alpha.md\n"
        ".agent-workflow/tasks/subdir/beta.md\n",
        encoding="utf-8",
    )
    assert discover_slugs_from_changed_files(tmp_path, changed) == ["alpha"]


def test_discover_slugs_returns_empty_for_unrelated_changes(tmp_path: Path) -> None:
    """A PR that touches only code returns an empty slug list."""
    changed = tmp_path / "changed-files.txt"
    changed.write_text(
        "core/checker/checker.py\n"
        "docs/SPEC.md\n",
        encoding="utf-8",
    )
    assert discover_slugs_from_changed_files(tmp_path, changed) == []


# ---------------------------------------------------------------------------
# CLI fallback semantics — slice 0 (post-shakeout fix)
# ---------------------------------------------------------------------------


def _fixture_repo(tmp_path: Path) -> Path:
    """Build a minimal valid repo for CLI invocations."""
    (tmp_path / "agent-workflow.yaml").write_text(
        'version: 1\n'
        'project:\n  name: t\n'
        'workRecord:\n  backend: local\n  local:\n    taskPath: ".agent-workflow/tasks/{slug}.md"\n'
        'redline: optional\n',
        encoding="utf-8",
    )
    tasks = tmp_path / ".agent-workflow" / "tasks"
    tasks.mkdir(parents=True)
    return tmp_path


def test_cli_zero_records_no_matching_wr_stays_clean(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Zero records + no WR at the --slug path + opt-out → clean exit.

    F5: by default a code-only PR with no Work Record now blocks via the
    synthetic `workrecord.required_for_branch_changes` predicate. The
    "pure housekeeping" case requires an explicit opt-out via
    `workRecord.requiredForBranchChanges: false`. With the opt-out set,
    the previous behaviour (clean exit, no records) is preserved.
    """
    from core.checker.checker import main

    repo = _fixture_repo(tmp_path)
    # F5 opt-out so a vendored-checker bump or formatter pass doesn't
    # synthesise the missing-WR predicate.
    (repo / "agent-workflow.yaml").write_text(
        'version: 1\n'
        'project:\n  name: t\n'
        'workRecord:\n  backend: local\n  local:\n    taskPath: ".agent-workflow/tasks/{slug}.md"\n'
        '  requiredForBranchChanges: false\n'
        'redline: optional\n',
        encoding="utf-8",
    )
    changed = tmp_path / "changed-files.txt"
    changed.write_text("scripts/agent-workflow-check.py\n", encoding="utf-8")

    code = main([
        "--repo-root", str(repo),
        "--changed-files", str(changed),
        "--slug", "no-wr-at-this-slug",
    ])

    out = capsys.readouterr().out
    assert code == 0, f"expected clean exit, got {code}; verdict: {out}"
    verdict = json.loads(out)
    assert verdict["status"] == "clean"
    assert verdict["records"] == []


def test_cli_zero_records_with_code_changes_default_blocks_via_synthetic_predicate(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """F5: default-on. Code-only PR with no Work Record at the branch
    slug surfaces a blocking `workrecord.required_for_branch_changes`
    predicate naming the non-WR paths and the missing slug.
    """
    from core.checker.checker import main

    repo = _fixture_repo(tmp_path)
    changed = tmp_path / "changed-files.txt"
    changed.write_text(
        "src/main/java/com/example/Foo.java\n"
        "src/main/java/com/example/Bar.java\n",
        encoding="utf-8",
    )

    code = main([
        "--repo-root", str(repo),
        "--changed-files", str(changed),
        "--slug", "feat-no-wr",
    ])

    out = capsys.readouterr().out
    assert code == 2, f"expected blocking exit, got {code}; verdict: {out}"
    verdict = json.loads(out)
    assert verdict["status"] == "blocking"
    assert len(verdict["records"]) == 1
    rec = verdict["records"][0]
    assert rec["slug"] == "feat-no-wr"
    names = [p["name"] for p in rec["predicates"]]
    assert "workrecord.required_for_branch_changes" in names
    pred = next(
        p for p in rec["predicates"]
        if p["name"] == "workrecord.required_for_branch_changes"
    )
    assert pred["passed"] is False
    assert pred["blocking"] is True
    assert "Foo.java" in pred["detail"] or "Bar.java" in pred["detail"]
    assert "requiredForBranchChanges" in pred["detail"]


def test_cli_zero_records_with_only_wr_paths_stays_clean(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """F5: a PR that only touched files under the task-path prefix but
    none of them parsed as a Work Record (e.g. a README under
    `.agent-workflow/tasks/README.md`) should NOT synthesise the
    missing-WR predicate — there were no code paths to require a WR
    for. Stays clean by default."""
    from core.checker.checker import main

    repo = _fixture_repo(tmp_path)
    changed = tmp_path / "changed-files.txt"
    changed.write_text(".agent-workflow/tasks/README.md\n", encoding="utf-8")

    code = main([
        "--repo-root", str(repo),
        "--changed-files", str(changed),
        "--slug", "no-wr-at-this-slug",
    ])

    out = capsys.readouterr().out
    assert code == 0, f"expected clean exit, got {code}; verdict: {out}"
    verdict = json.loads(out)
    assert verdict["status"] == "clean"


def test_cli_zero_records_falls_back_when_wr_exists_at_slug(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Zero records but a WR exists at the --slug path → validate it.

    Closes the F1 hole: a code-only PR on a branch whose Work Record
    was committed in an earlier push still validates against that
    record. Without this fallback, the PR would ship with `records: []`
    and a green verdict regardless of whether the branch has a Work
    Record at all.
    """
    from core.checker.checker import main

    repo = _fixture_repo(tmp_path)
    # Pre-existing WR at the slug — landed on an earlier commit.
    (repo / ".agent-workflow" / "tasks" / "feature-x.md").write_text(
        "<!-- agent-workflow:start -->\n"
        "**Outcome:** o\n\n**Target:** t\n\n**Scope:** s\n\n"
        "**Constraints:** —\n\n**Completion criteria:** cc\n\n"
        "**Risk:** Routine\n\n**Complexity:** Simple\n\n**Reason:** —\n\n"
        "**Approach:** a\n\n**Verification:** v\n\n"
        "**State:** Ready for review\n"
        "<!-- agent-workflow:end -->\n",
        encoding="utf-8",
    )
    # This PR's diff: code only, no WR file in changed-files.
    changed = tmp_path / "changed-files.txt"
    changed.write_text("src/feature_x.py\n", encoding="utf-8")

    code = main([
        "--repo-root", str(repo),
        "--changed-files", str(changed),
        "--slug", "feature-x",
    ])

    out = capsys.readouterr().out
    verdict = json.loads(out)
    # Validates the WR. Verdict status depends on the record's content
    # — for the well-formed fixture above we expect at least one record
    # entry rather than the empty list of the housekeeping case.
    assert verdict["records"], (
        f"expected fallback to validate the WR at the --slug path; "
        f"got empty records (exit {code}): {out}"
    )
    assert verdict["records"][0]["slug"] == "feature-x"


def test_cli_falls_back_when_changed_files_path_missing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Missing --changed-files file (e.g. CI step crashed) → fall back to --slug.

    Distinguishes "discovery succeeded with zero" (the case above —
    legitimate) from "discovery couldn't run" (this case — broken
    signal, --slug is the safety net).
    """
    from core.checker.checker import main

    repo = _fixture_repo(tmp_path)
    (repo / ".agent-workflow" / "tasks" / "demo.md").write_text(
        "<!-- agent-workflow:start -->\n"
        "**Outcome:** o\n\n**Target:** t\n\n**Scope:** s\n\n"
        "**Constraints:** —\n\n**Completion criteria:** cc\n\n"
        "**Risk:** Routine\n\n**Complexity:** Simple\n\n**Reason:** —\n\n"
        "**Approach:** a\n\n**Verification:** v\n\n"
        "**State:** Ready for review\n"
        "<!-- agent-workflow:end -->\n",
        encoding="utf-8",
    )

    code = main([
        "--repo-root", str(repo),
        "--changed-files", str(tmp_path / "nonexistent.txt"),
        "--slug", "demo",
    ])

    captured = capsys.readouterr()
    out = captured.out
    err = captured.err
    assert code in (0, 1), f"expected clean or advisory, got {code}; verdict: {out}"
    verdict = json.loads(out)
    assert len(verdict["records"]) == 1
    assert verdict["records"][0]["slug"] == "demo"
    # Unreadable --changed-files must surface a stderr warning so the
    # caller can distinguish a broken signal from a legitimate empty
    # discovery (s19 finding from the 2026-06 behavior-validation run).
    assert "--changed-files" in err and "could not be read" in err


def test_cli_slug_only_validates_one_record(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Legacy single-slug mode (no --changed-files) still works."""
    from core.checker.checker import main

    repo = _fixture_repo(tmp_path)
    (repo / ".agent-workflow" / "tasks" / "demo.md").write_text(
        "<!-- agent-workflow:start -->\n"
        "**Outcome:** o\n\n**Target:** t\n\n**Scope:** s\n\n"
        "**Constraints:** —\n\n**Completion criteria:** cc\n\n"
        "**Risk:** Routine\n\n**Complexity:** Simple\n\n**Reason:** —\n\n"
        "**Approach:** a\n\n**Verification:** v\n\n"
        "**State:** Ready for review\n"
        "<!-- agent-workflow:end -->\n",
        encoding="utf-8",
    )

    code = main(["--repo-root", str(repo), "--slug", "demo"])

    out = capsys.readouterr().out
    assert code in (0, 1), f"expected clean or advisory, got {code}; verdict: {out}"
    verdict = json.loads(out)
    assert len(verdict["records"]) == 1
    assert verdict["records"][0]["slug"] == "demo"


# ---------------------------------------------------------------------------
# workrecord.commit_order — advisory commit-ordering signal
# ---------------------------------------------------------------------------


def _init_git_repo(repo_root: Path) -> None:
    """Initialise a minimal git repo with a 'main' branch + origin/main ref.

    The predicate walks ``origin/main..HEAD``; tests fake that by
    creating a local 'main' and aliasing origin/main to it via the
    refs/remotes/origin/main ref.
    """
    import subprocess
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo_root, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.t"], cwd=repo_root, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=repo_root, check=True)
    # Initial commit on main with the agent-workflow config so the
    # checker can load it.
    (repo_root / "agent-workflow.yaml").write_text(
        "version: 1\n"
        "project:\n"
        "  name: demo\n"
        "workRecord:\n"
        "  backend: local\n"
        "  local:\n"
        "    taskPath: \".agent-workflow/tasks/{slug}.md\"\n"
        "redline: optional\n",
        encoding="utf-8",
    )
    (repo_root / ".agent-workflow" / "tasks").mkdir(parents=True)
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=repo_root, check=True)
    # Fake origin/main pointing at the init commit. Predicate walks
    # `origin/main..HEAD` so this is the base.
    subprocess.run(
        ["git", "update-ref", "refs/remotes/origin/main", "HEAD"],
        cwd=repo_root, check=True,
    )


def _git_commit(repo_root: Path, message: str) -> str:
    import subprocess
    subprocess.run(["git", "add", "-A"], cwd=repo_root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", message], cwd=repo_root, check=True)
    sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo_root, check=True,
        capture_output=True, text=True,
    ).stdout.strip()
    return sha


def _make_wr(repo_root: Path, slug: str) -> Path:
    p = repo_root / ".agent-workflow" / "tasks" / f"{slug}.md"
    p.write_text(
        "<!-- agent-workflow:start -->\n"
        "**Outcome:** o\n\n**Target:** t\n\n**Scope:** s\n\n"
        "**Constraints:** —\n\n**Completion criteria:** cc\n\n"
        "**Risk:** Routine\n\n**Complexity:** Simple\n\n**Reason:** —\n\n"
        "**Approach:** a\n\n**Verification:** v\n\n"
        "**State:** Ready to implement\n"
        "<!-- agent-workflow:end -->\n",
        encoding="utf-8",
    )
    return p


def test_commit_order_wr_before_code_passes(tmp_path: Path) -> None:
    """The discipline-following case: WR committed in its own commit
    before any code commit. Predicate should pass clean."""
    from core.checker.checker import main
    from core.work_record.local_backend import LocalBackend
    from core.checker.predicates import workrecord_commit_order, CheckerContext

    _init_git_repo(tmp_path)
    _make_wr(tmp_path, "feature-x")
    _git_commit(tmp_path, "wr: open Work Record")
    (tmp_path / "src.py").write_text("x = 1\n", encoding="utf-8")
    _git_commit(tmp_path, "code: implement feature x")

    backend = LocalBackend(tmp_path, ".agent-workflow/tasks/{slug}.md")
    ctx = CheckerContext(
        backend=backend, slug="feature-x",
        record=None, shape=None, parse_error=None, raw_text="",
        redline_verdict=None, redline_required=False,
        redline_verdict_parse_error=None,
        repo_root=tmp_path,
    )
    result = workrecord_commit_order(ctx)
    assert result.passed is True, f"expected pass, got {result.detail}"
    assert result.blocking is False


def test_commit_order_wr_after_code_advisory_fails(tmp_path: Path) -> None:
    """The F4 anti-pattern: code lands first, WR commits retroactively.
    Predicate emits the advisory finding."""
    from core.work_record.local_backend import LocalBackend
    from core.checker.predicates import workrecord_commit_order, CheckerContext

    _init_git_repo(tmp_path)
    (tmp_path / "src.py").write_text("x = 1\n", encoding="utf-8")
    _git_commit(tmp_path, "code: write before plan")
    _make_wr(tmp_path, "feature-y")
    _git_commit(tmp_path, "wr: write the record after the fact")

    backend = LocalBackend(tmp_path, ".agent-workflow/tasks/{slug}.md")
    ctx = CheckerContext(
        backend=backend, slug="feature-y",
        record=None, shape=None, parse_error=None, raw_text="",
        redline_verdict=None, redline_required=False,
        redline_verdict_parse_error=None,
        repo_root=tmp_path,
    )
    result = workrecord_commit_order(ctx)
    assert result.passed is False, f"expected advisory fail, got {result.detail}"
    assert result.blocking is False
    assert "advisory" in result.detail.lower()
    assert "retroactively" in result.detail.lower() or "after" in result.detail.lower()


def test_commit_order_same_commit_advisory_fails(tmp_path: Path) -> None:
    """WR and code in the same commit also misses the discipline."""
    from core.work_record.local_backend import LocalBackend
    from core.checker.predicates import workrecord_commit_order, CheckerContext

    _init_git_repo(tmp_path)
    _make_wr(tmp_path, "feature-z")
    (tmp_path / "src.py").write_text("x = 1\n", encoding="utf-8")
    _git_commit(tmp_path, "wr+code: planning and code together")

    backend = LocalBackend(tmp_path, ".agent-workflow/tasks/{slug}.md")
    ctx = CheckerContext(
        backend=backend, slug="feature-z",
        record=None, shape=None, parse_error=None, raw_text="",
        redline_verdict=None, redline_required=False,
        redline_verdict_parse_error=None,
        repo_root=tmp_path,
    )
    result = workrecord_commit_order(ctx)
    assert result.passed is False
    assert result.blocking is False
    assert "same commit" in result.detail.lower()


def test_commit_order_no_wr_skipped(tmp_path: Path) -> None:
    """No WR file on the branch yet — skip cleanly."""
    from core.work_record.local_backend import LocalBackend
    from core.checker.predicates import workrecord_commit_order, CheckerContext

    _init_git_repo(tmp_path)
    (tmp_path / "src.py").write_text("x = 1\n", encoding="utf-8")
    _git_commit(tmp_path, "code only")

    backend = LocalBackend(tmp_path, ".agent-workflow/tasks/{slug}.md")
    ctx = CheckerContext(
        backend=backend, slug="missing-slug",
        record=None, shape=None, parse_error=None, raw_text="",
        redline_verdict=None, redline_required=False,
        redline_verdict_parse_error=None,
        repo_root=tmp_path,
    )
    result = workrecord_commit_order(ctx)
    assert result.passed is True
    assert "skipped" in result.detail.lower()


def test_commit_order_no_repo_root_skipped(tmp_path: Path) -> None:
    """Legacy callers that don't pass repo_root: skip cleanly."""
    from core.work_record.local_backend import LocalBackend
    from core.checker.predicates import workrecord_commit_order, CheckerContext

    backend = LocalBackend(tmp_path, ".agent-workflow/tasks/{slug}.md")
    ctx = CheckerContext(
        backend=backend, slug="x",
        record=None, shape=None, parse_error=None, raw_text="",
        redline_verdict=None, redline_required=False,
        redline_verdict_parse_error=None,
        repo_root=None,
    )
    result = workrecord_commit_order(ctx)
    assert result.passed is True
    assert "skipped" in result.detail.lower()
    assert "repo_root" in result.detail.lower()


def test_commit_order_recovers_from_per_commit_show_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Per-commit `git show` failures continue the walk instead of bailing.

    Review feedback on PR #32: a TimeoutExpired inside the per-commit
    loop previously returned None and aborted the predicate. With the
    refactor, transient failures on individual commits skip just that
    commit and the walk continues — the predicate can still classify
    the branch correctly as long as enough commits succeed.
    """
    import subprocess as _sub
    from core.work_record.local_backend import LocalBackend
    from core.checker.predicates import workrecord_commit_order, CheckerContext

    _init_git_repo(tmp_path)
    _make_wr(tmp_path, "feature-resilience")
    wr_sha = _git_commit(tmp_path, "wr: open Work Record")
    (tmp_path / "src.py").write_text("x = 1\n", encoding="utf-8")
    code_sha = _git_commit(tmp_path, "code: implement feature")

    # Wrap subprocess.run: succeed for `git log`, but raise
    # TimeoutExpired for the FIRST `git show` invocation. The
    # second `git show` (next commit) should succeed and let the
    # predicate finish.
    real_run = _sub.run
    state = {"show_call_count": 0}

    def flaky_run(args, *a, **kw):
        if isinstance(args, list) and len(args) > 1 and args[1] == "show":
            state["show_call_count"] += 1
            if state["show_call_count"] == 1:
                raise _sub.TimeoutExpired(cmd=args, timeout=15)
        return real_run(args, *a, **kw)

    monkeypatch.setattr(_sub, "run", flaky_run)

    backend = LocalBackend(tmp_path, ".agent-workflow/tasks/{slug}.md")
    ctx = CheckerContext(
        backend=backend, slug="feature-resilience",
        record=None, shape=None, parse_error=None, raw_text="",
        redline_verdict=None, redline_required=False,
        redline_verdict_parse_error=None,
        repo_root=tmp_path,
    )
    result = workrecord_commit_order(ctx)

    # The first commit's `git show` failed (the WR commit), so the
    # predicate doesn't see that commit's WR touch. It DOES see the
    # second commit (the code commit) — but that one touches only
    # `src.py`, no WR. With wr_first never set, the predicate skips
    # cleanly. The KEY assertion: the predicate must return a result
    # (not blow up with TimeoutExpired) and stay non-blocking.
    assert result.blocking is False
    assert result.passed is True  # graceful skip, not advisory fail
    # Predicate produced a verdict despite the timeout
    assert result.name == "workrecord.commit_order"


# ---------------------------------------------------------------------------
# RedlineVerdict.is_binding — shadow-mode disposition (F4)
# ---------------------------------------------------------------------------


def test_is_binding_defaults_to_true_when_modes_absent() -> None:
    """Verdicts from older reporters (no `modes` key) keep the previous
    hardcoded blocking behaviour. Forward-compat: missing modes => binding."""
    from core.checker.redline_verdict import RedlineVerdict
    v = RedlineVerdict(
        boundary_violations=[],
        zones={"blue": [], "gray": [], "red": [], "watch": []},
        checkpoints=[],
        api_changed=False,
        schema_changed=False,
        security_changed=False,
        runtime_config_changed=False,
    )
    assert v.is_binding("report") is True
    assert v.is_binding("boundary_violation") is True


def test_is_binding_reads_default_mode() -> None:
    """`modes.default` controls disposition for any check without a
    perCheck override."""
    from core.checker.redline_verdict import RedlineVerdict
    v = RedlineVerdict(
        boundary_violations=[],
        zones={"blue": [], "gray": [], "red": [], "watch": []},
        checkpoints=[],
        api_changed=False,
        schema_changed=False,
        security_changed=False,
        runtime_config_changed=False,
        modes={"default": "shadow", "perCheck": {}},
    )
    assert v.is_binding("report") is False
    v_binding = RedlineVerdict(
        boundary_violations=[],
        zones={"blue": [], "gray": [], "red": [], "watch": []},
        checkpoints=[],
        api_changed=False,
        schema_changed=False,
        security_changed=False,
        runtime_config_changed=False,
        modes={"default": "binding", "perCheck": {}},
    )
    assert v_binding.is_binding("report") is True


def test_is_binding_perCheck_overrides_default() -> None:
    """`perCheck.<name>` wins over `modes.default`."""
    from core.checker.redline_verdict import RedlineVerdict
    v = RedlineVerdict(
        boundary_violations=[],
        zones={"blue": [], "gray": [], "red": [], "watch": []},
        checkpoints=[],
        api_changed=False,
        schema_changed=False,
        security_changed=False,
        runtime_config_changed=False,
        modes={"default": "shadow", "perCheck": {"report": "binding"}},
    )
    assert v.is_binding("report") is True


def test_is_binding_boundary_violation_hardcoded_default() -> None:
    """`boundary_violation` defaults to binding even under
    `modes.default: shadow` — only an explicit perCheck override flips it."""
    from core.checker.redline_verdict import RedlineVerdict
    v = RedlineVerdict(
        boundary_violations=[],
        zones={"blue": [], "gray": [], "red": [], "watch": []},
        checkpoints=[],
        api_changed=False,
        schema_changed=False,
        security_changed=False,
        runtime_config_changed=False,
        modes={"default": "shadow", "perCheck": {}},
    )
    assert v.is_binding("boundary_violation") is True
    v_flipped = RedlineVerdict(
        boundary_violations=[],
        zones={"blue": [], "gray": [], "red": [], "watch": []},
        checkpoints=[],
        api_changed=False,
        schema_changed=False,
        security_changed=False,
        runtime_config_changed=False,
        modes={"default": "shadow", "perCheck": {"boundary_violation": "shadow"}},
    )
    assert v_flipped.is_binding("boundary_violation") is False
