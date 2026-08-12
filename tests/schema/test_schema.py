"""Tests for the config schema and loader.

Exercises the happy path (the repo's own ``agent-workflow.yaml`` plus
the minimal-local fixture) and the error paths the schema rules out
(missing required field, bad enum value, conditional-required missing).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from core.config import Config, ConfigError, load

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "config"


# ---------------------------------------------------------------------------
# Happy paths
# ---------------------------------------------------------------------------


def test_repo_own_config_loads() -> None:
    """The dev repo's own agent-workflow.yaml validates and loads."""
    cfg = load(REPO_ROOT / "agent-workflow.yaml")
    assert isinstance(cfg, Config)
    assert cfg.version == 1
    assert cfg.project_name == "agent-workflow"
    assert cfg.work_record.backend == "local"
    assert cfg.work_record.local is not None
    assert cfg.work_record.local.task_path == ".agent-workflow/tasks/{slug}.md"


def test_minimal_local_fixture_loads() -> None:
    cfg = load(FIXTURES / "minimal-local.yaml")
    assert cfg.work_record.backend == "local"
    assert cfg.work_record.local is not None
    assert "{slug}" in cfg.work_record.local.task_path


# ---------------------------------------------------------------------------
# Schema-rejected invalid configs
# ---------------------------------------------------------------------------


def test_missing_taskpath_when_backend_is_local() -> None:
    with pytest.raises(ConfigError, match="config invalid"):
        load(FIXTURES / "invalid-local-missing-taskpath.yaml")


def test_unknown_backend_rejected() -> None:
    with pytest.raises(ConfigError, match="config invalid"):
        load(FIXTURES / "invalid-bad-backend.yaml")


def test_missing_project_rejected() -> None:
    with pytest.raises(ConfigError, match="config invalid"):
        load(FIXTURES / "invalid-missing-project.yaml")


# ---------------------------------------------------------------------------
# File-level errors
# ---------------------------------------------------------------------------


def test_missing_file_raises() -> None:
    with pytest.raises(ConfigError, match="not found"):
        load(FIXTURES / "this-file-does-not-exist.yaml")


def test_non_mapping_top_level_rejected(tmp_path: Path) -> None:
    bad = tmp_path / "config.yaml"
    bad.write_text("- just\n- a\n- list\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="must be a YAML mapping"):
        load(bad)


def test_empty_file_rejected(tmp_path: Path) -> None:
    empty = tmp_path / "config.yaml"
    empty.write_text("", encoding="utf-8")
    with pytest.raises(ConfigError, match="empty"):
        load(empty)


def test_invalid_yaml_rejected(tmp_path: Path) -> None:
    bad = tmp_path / "config.yaml"
    bad.write_text("version: 1\nproject: {name: x\n", encoding="utf-8")  # unclosed brace
    with pytest.raises(ConfigError, match="not valid YAML"):
        load(bad)


# ---------------------------------------------------------------------------
# Forward compatibility
# ---------------------------------------------------------------------------


def test_unknown_top_level_field_is_tolerated(tmp_path: Path) -> None:
    """Unknown top-level fields stay readable in cfg.raw for forward compat.

    The schema's ``additionalProperties: true`` at the root lets us add
    fields incrementally without breaking existing configs. The loader
    exposes the raw mapping so non-yet-typed fields are accessible.
    """
    cfg_text = """
version: 1
project:
  name: x
workRecord:
  backend: local
  local:
    taskPath: ".agent-workflow/tasks/{slug}.md"
notYetTypedField: surprise
"""
    p = tmp_path / "config.yaml"
    p.write_text(cfg_text, encoding="utf-8")
    cfg = load(p)
    assert cfg.raw.get("notYetTypedField") == "surprise"


def test_hooks_guarded_paths_validates(tmp_path: Path) -> None:
    """A config carrying hooks.guardedPaths validates and stays readable."""
    cfg_text = """
version: 1
project:
  name: x
workRecord:
  backend: local
  local:
    taskPath: ".agent-workflow/tasks/{slug}.md"
hooks:
  guardedPaths:
    - "core/"
    - "scripts/"
"""
    p = tmp_path / "config.yaml"
    p.write_text(cfg_text, encoding="utf-8")
    cfg = load(p)
    assert cfg.raw["hooks"]["guardedPaths"] == ["core/", "scripts/"]


def test_hooks_guarded_paths_wrong_type_rejected(tmp_path: Path) -> None:
    """guardedPaths must be an array of non-empty strings, not a scalar."""
    cfg_text = """
version: 1
project:
  name: x
workRecord:
  backend: local
  local:
    taskPath: ".agent-workflow/tasks/{slug}.md"
hooks:
  guardedPaths: "core/"
"""
    p = tmp_path / "config.yaml"
    p.write_text(cfg_text, encoding="utf-8")
    with pytest.raises(ConfigError, match="config invalid"):
        load(p)


def test_config_without_hooks_still_loads(tmp_path: Path) -> None:
    """Legacy configs (no hooks key) validate unchanged — backward compatible."""
    cfg_text = """
version: 1
project:
  name: x
workRecord:
  backend: local
  local:
    taskPath: ".agent-workflow/tasks/{slug}.md"
"""
    p = tmp_path / "config.yaml"
    p.write_text(cfg_text, encoding="utf-8")
    cfg = load(p)
    assert "hooks" not in cfg.raw


# ---------------------------------------------------------------------------
# Slice B: redline + redlineVerdictPath + riskTriggers
# ---------------------------------------------------------------------------


def test_redline_defaults_when_absent(tmp_path: Path) -> None:
    """A config without the redline fields gets the documented defaults."""
    cfg_text = """
version: 1
project:
  name: x
workRecord:
  backend: local
  local:
    taskPath: ".agent-workflow/tasks/{slug}.md"
"""
    p = tmp_path / "config.yaml"
    p.write_text(cfg_text, encoding="utf-8")
    cfg = load(p)
    assert cfg.redline.required is True
    assert cfg.redline.verdict_path == "build/redline-verdict.json"


def test_redline_optional_loads(tmp_path: Path) -> None:
    cfg_text = """
version: 1
project:
  name: x
workRecord:
  backend: local
  local:
    taskPath: ".agent-workflow/tasks/{slug}.md"
redline: optional
redlineVerdictPath: ci/redline.json
"""
    p = tmp_path / "config.yaml"
    p.write_text(cfg_text, encoding="utf-8")
    cfg = load(p)
    assert cfg.redline.required is False
    assert cfg.redline.verdict_path == "ci/redline.json"


def test_redline_bad_enum_rejected() -> None:
    with pytest.raises(ConfigError, match="config invalid"):
        load(FIXTURES / "invalid-redline-bad-enum.yaml")
