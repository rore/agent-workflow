"""Focused applicability config and evaluator tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.config import (
    ConfigError,
    DocumentationOnlyConfig,
    evaluate_applicability,
    load,
)


def rule(
    paths: tuple[str, ...] = ("docs/",),
    *,
    workflow_required: bool = False,
    direct: bool = True,
) -> DocumentationOnlyConfig:
    return DocumentationOnlyConfig(paths, workflow_required, direct)


def decide(
    changed: tuple[str, ...],
    *,
    risk: str = "low",
    protection: str = "unprotected",
    protected: tuple[str, ...] = (),
    config: DocumentationOnlyConfig | None = rule(),
):
    return evaluate_applicability(changed, risk, protection, protected, config)


def test_docs_only_change_is_exempt_and_direct_branch_is_allowed() -> None:
    result = decide(("docs/guide.md",))
    assert result.workflow_required is False
    assert result.direct_default_branch_allowed is True
    assert result.matched_rule == "documentationOnly"
    assert result.paths == ("docs/guide.md",)
    assert "documentation_only" in result.reason_codes


def test_multiple_approved_paths_use_all_path_semantics() -> None:
    result = decide(("docs/guide.md", "README.md"), config=rule(("docs/", "README.md")))
    assert result.workflow_required is False
    assert result.matched_rule == "documentationOnly"


def test_mixed_path_denies_the_whole_change() -> None:
    result = decide(("docs/guide.md", "src/app.py"))
    assert result.workflow_required is True
    assert result.direct_default_branch_allowed is False
    assert "path_not_approved" in result.reason_codes


def test_protected_path_denies_even_under_an_approved_prefix() -> None:
    result = decide(("docs/SPEC.md",), protected=("docs/SPEC.md",))
    assert result.workflow_required is True
    assert result.direct_default_branch_allowed is False
    assert "protected_path" in result.reason_codes


@pytest.mark.parametrize("risk", ["risky", "unavailable"])
def test_non_low_risk_denies_both_permissions(risk: str) -> None:
    result = decide(("docs/guide.md",), risk=risk)
    assert result.workflow_required is True
    assert result.direct_default_branch_allowed is False
    assert "risk_not_low" in result.reason_codes


@pytest.mark.parametrize("protection", ["protected", "unavailable"])
def test_branch_protection_only_denies_direct_branch(protection: str) -> None:
    result = decide(("docs/guide.md",), protection=protection)
    assert result.workflow_required is False
    assert result.direct_default_branch_allowed is False


def test_direct_branch_can_be_disabled_without_requiring_workflow() -> None:
    result = decide(("docs/guide.md",), config=rule(direct=False))
    assert result.workflow_required is False
    assert result.direct_default_branch_allowed is False


def test_workflow_required_config_disables_exemption() -> None:
    result = decide(("docs/guide.md",), config=rule(workflow_required=True))
    assert result.workflow_required is True
    assert result.direct_default_branch_allowed is False


@pytest.mark.parametrize(
    "changed",
    [(), ("",), ("/docs/a.md",), ("docs\\a.md",), ("docs/../a.md",), ("docs/*.md",)],
)
def test_empty_or_malformed_paths_fail_closed(changed: tuple[str, ...]) -> None:
    result = decide(changed)
    assert result.workflow_required is True
    assert result.direct_default_branch_allowed is False


def test_spaces_and_unicode_are_lossless() -> None:
    path = "docs/用户 指南/README — v2.md"
    result = decide((path,))
    assert result.workflow_required is False
    assert result.paths == (path,)


def test_invalid_config_fails_closed() -> None:
    result = decide(
        ("docs/guide.md",),
        config=DocumentationOnlyConfig(("../docs/",), False, True),
    )
    assert result.workflow_required is True
    assert result.direct_default_branch_allowed is False
    assert "invalid_applicability_config" in result.reason_codes


def test_no_config_preserves_current_behavior() -> None:
    result = decide(("docs/guide.md",), config=None)
    assert result.workflow_required is True
    assert result.direct_default_branch_allowed is False
    assert "no_applicability_config" in result.reason_codes


def test_decision_is_immutable() -> None:
    result = decide(("docs/guide.md",))
    with pytest.raises(AttributeError):
        result.workflow_required = True  # type: ignore[misc]


def test_loader_exposes_typed_optional_shape(tmp_path: Path) -> None:
    config = tmp_path / "agent-workflow.yaml"
    config.write_text(
        """
version: 1
project: {name: example}
workRecord:
  backend: local
  local:
    taskPath: ".agent-workflow/tasks/{slug}.md"
applicability:
  documentationOnly:
    paths: [docs/, README.md]
    workflowRequired: false
    directDefaultBranchAllowed: true
""",
        encoding="utf-8",
    )
    cfg = load(config)
    assert cfg.applicability is not None
    assert cfg.applicability.documentation_only == rule(("docs/", "README.md"))


@pytest.mark.parametrize(
    "path", ["", "/docs/", "C:/docs/", "docs\\", "docs/../", "docs/*.md"]
)
def test_schema_rejects_invalid_approved_paths(tmp_path: Path, path: str) -> None:
    config = tmp_path / "agent-workflow.yaml"
    config.write_text(
        f"""
version: 1
project: {{name: example}}
workRecord:
  backend: local
  local:
    taskPath: ".agent-workflow/tasks/{{slug}}.md"
applicability:
  documentationOnly:
    paths: ['{path}']
    workflowRequired: false
    directDefaultBranchAllowed: false
""",
        encoding="utf-8",
    )
    with pytest.raises(ConfigError, match="config invalid"):
        load(config)