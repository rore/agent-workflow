"""Unit tests for scripts/agent-workflow-tune.py.

Regression guards for two defects found during the payments pilot:

  1. `gh api --paginate --jq '[...]'` emits one JSON array per page, so
     `json.loads` crashed on PRs touching >30 files. `_merge_paginated_arrays`
     must flatten the concatenated pages.
  2. `_path_matches_rule` used `PurePosixPath.match()`, which does not treat
     `**` as recursive, so every glob-based red rule reported 0% firing. It
     must match the redline reporter's `**`/`*` semantics.

Fixture-mode tests (tests/tuner/run.sh) exercise the calibration and
CODEOWNERS layers end to end; these units cover the two code paths that
fixture mode bypasses (the live `gh` parse path) or under-specifies (glob
edge cases + reporter parity).
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# The script has a hyphenated name — load it by path, mirroring
# core/agent-redline/tests/reporter/test_tune_suggest.py.
_spec = importlib.util.spec_from_file_location(
    "agent_workflow_tune",
    REPO_ROOT / "scripts" / "agent-workflow-tune.py",
)
tune = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tune)

# The redline reporter is the source of truth for glob semantics; import it
# to assert the tuner's ported matcher stays in agreement (Material
# assumption #2 in the Work Record).
sys.path.insert(0, str(REPO_ROOT / "core" / "agent-redline"))
from core.reporter import reporter as redline_reporter  # noqa: E402


# ---------------------------------------------------------------------------
# Bug 2 — recursive glob matching
# ---------------------------------------------------------------------------

# (path, glob, expected) — the external/controller cases returned False under
# the old PurePosixPath.match() while the real CI checker classified them RED.
_GLOB_CASES = [
    (
        "src/main/java/com/acme/payments/infrastructure/external/ExternalExceptionMapper.java",
        "src/main/java/**/infrastructure/external/**",
        True,
    ),
    (
        "src/main/java/com/acme/payments/inbound/card/CardController.java",
        "src/main/java/**/*Controller.java",
        True,
    ),
    ("src/main/resources/db/migration/V1__init.sql", "src/main/resources/db/migration/**", True),
    # `**` spans zero components too.
    ("src/main/java/Foo.java", "src/main/java/**", True),
    # `*` does NOT span a path separator.
    ("src/main/java/a/b/Foo.java", "src/main/java/*.java", False),
    # literal, root-anchored — matches at root, not when nested (deliberate
    # alignment with reporter semantics; see Work Record Plan note).
    ("agent-redline-policy.yaml", "agent-redline-policy.yaml", True),
    ("nested/dir/agent-redline-policy.yaml", "agent-redline-policy.yaml", False),
    ("docs/architecture/overview.md", "src/main/java/**/*Controller.java", False),
]


@pytest.mark.parametrize("path,glob,expected", _GLOB_CASES)
def test_path_matches_recursive_glob(path, glob, expected):
    assert tune._path_matches_rule(path, glob) is expected


@pytest.mark.parametrize("path,glob,_expected", _GLOB_CASES)
def test_matcher_agrees_with_redline_reporter(path, glob, _expected):
    """The ported matcher must agree with the reporter for every case, so
    tuner firing-rates line up with CI zone classification."""
    assert tune._path_matches_rule(path, glob) == redline_reporter.matches(path, glob)


# ---------------------------------------------------------------------------
# Bug 1 — paginated-response parsing
# ---------------------------------------------------------------------------


def test_merge_paginated_arrays_flattens_pages():
    """Concatenated per-page arrays (what --paginate emits) flatten to one list."""
    raw = '["a.java", "b.java"]\n["c.java"]'
    assert tune._merge_paginated_arrays(raw) == ["a.java", "b.java", "c.java"]


def test_merge_paginated_arrays_single_page():
    assert tune._merge_paginated_arrays('["x"]') == ["x"]


def test_merge_paginated_arrays_empty():
    assert tune._merge_paginated_arrays("") == []
    assert tune._merge_paginated_arrays("   \n  ") == []


def test_merge_paginated_arrays_raises_on_garbage():
    with pytest.raises(json.JSONDecodeError):
        tune._merge_paginated_arrays("not json")


def _completed(stdout: str) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=["gh"], returncode=0, stdout=stdout, stderr="")


def test_pr_changed_files_survives_multipage_response():
    """Before the fix, a >30-file PR (two --paginate pages) crashed json.loads.
    The runner must now return one flat file list."""
    runner = tune.GhRunner(gh_host="github.example.com")
    two_pages = '["src/A.java", "src/B.java"]\n["src/C.java"]'
    with patch.object(tune.subprocess, "run", return_value=_completed(two_pages)):
        files = runner.pr_changed_files("org/repo", 42)
    assert files == ["src/A.java", "src/B.java", "src/C.java"]


def test_pr_approvers_dedupes_across_pages():
    """pr_approvers now paginates; `unique` is per-page, so cross-page dupes
    must be removed in Python."""
    runner = tune.GhRunner(gh_host="github.example.com")
    two_pages = '["alice", "bob"]\n["bob", "carol"]'
    with patch.object(tune.subprocess, "run", return_value=_completed(two_pages)):
        approvers = runner.pr_approvers("org/repo", 7)
    assert approvers == ["alice", "bob", "carol"]
