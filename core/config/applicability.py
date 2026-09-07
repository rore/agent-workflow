"""Pure, deny-overrides workflow applicability decisions."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, Literal


RiskStatus = Literal["low", "risky", "unavailable"]
ProtectionStatus = Literal["unprotected", "protected", "unavailable"]
_GLOB_CHARS = frozenset("*?[]{}")


@dataclass(frozen=True)
class DocumentationOnlyConfig:
    """One human-approved documentation-only rule."""

    paths: tuple[str, ...]
    workflow_required: bool
    direct_default_branch_allowed: bool


@dataclass(frozen=True)
class ApplicabilityConfig:
    """Optional applicability settings from the repository config."""

    documentation_only: DocumentationOnlyConfig | None


@dataclass(frozen=True)
class ApplicabilityDecision:
    """One fail-closed decision for a complete change set."""

    workflow_required: bool
    direct_default_branch_allowed: bool
    matched_rule: str | None
    paths: tuple[str, ...]
    reason_codes: tuple[str, ...]


def _valid_repo_path(path: object, *, allow_prefix: bool) -> bool:
    if not isinstance(path, str) or not path or "\x00" in path:
        return False
    if path.startswith("/") or re.match(r"^[A-Za-z]:", path):
        return False
    if "\\" in path or any(char in _GLOB_CHARS for char in path):
        return False
    parts = path.split("/")
    if allow_prefix and path.endswith("/"):
        parts = parts[:-1]
    return bool(parts) and all(part not in {"", ".", ".."} for part in parts)


def _path_tuple(value: object) -> tuple[tuple[str, ...], bool]:
    """Retain path bytes-as-text; never strip or repair caller evidence."""
    if isinstance(value, (str, bytes)):
        return (), False
    try:
        values = tuple(value)  # type: ignore[arg-type]
    except TypeError:
        return (), False
    if any(not isinstance(item, str) for item in values):
        return tuple(item for item in values if isinstance(item, str)), False
    paths = tuple(values)
    return paths, len(set(paths)) == len(paths)


def _matches(path: str, rule: str) -> bool:
    return path == rule or (rule.endswith("/") and path.startswith(rule))


def approve_documentation_only(
    discovered_paths: Iterable[str],
    approved_paths: Iterable[str],
    *,
    direct_default_branch_approved: bool,
    protection_status: ProtectionStatus | str,
) -> DocumentationOnlyConfig | None:
    """Persist only a valid human-approved subset of an inert proposal."""
    discovered, discovered_valid = _path_tuple(discovered_paths)
    approved, approved_valid = _path_tuple(approved_paths)
    if (
        not discovered_valid
        or not approved_valid
        or not discovered
        or any(not _valid_repo_path(path, allow_prefix=True) for path in discovered + approved)
        or not isinstance(direct_default_branch_approved, bool)
        or protection_status not in {"unprotected", "protected", "unavailable"}
    ):
        raise ValueError("invalid documentation-only proposal or approval")
    if any(path not in discovered for path in approved):
        raise ValueError("approval contains a path that was not proposed")
    if not approved:
        return None
    return DocumentationOnlyConfig(
        paths=approved,
        workflow_required=False,
        direct_default_branch_allowed=(
            direct_default_branch_approved and protection_status == "unprotected"
        ),
    )


def evaluate_applicability(
    changed_paths: Iterable[str],
    risk_status: RiskStatus | str,
    protection_status: ProtectionStatus | str,
    protected_paths: Iterable[str],
    config: DocumentationOnlyConfig | None,
) -> ApplicabilityDecision:
    """Evaluate explicit complete inputs; any workflow doubt wins."""
    paths, paths_shape_valid = _path_tuple(changed_paths)
    protected, protected_shape_valid = _path_tuple(protected_paths)
    reasons: list[str] = []

    valid_config = (
        config is not None
        and isinstance(config.workflow_required, bool)
        and isinstance(config.direct_default_branch_allowed, bool)
        and isinstance(config.paths, tuple)
        and bool(config.paths)
        and len(set(config.paths)) == len(config.paths)
        and all(_valid_repo_path(path, allow_prefix=True) for path in config.paths)
    )
    if config is None:
        reasons.append("no_applicability_config")
    elif not valid_config:
        reasons.append("invalid_applicability_config")

    if not paths:
        reasons.append("empty_changed_paths")
    if not paths_shape_valid or any(
        not _valid_repo_path(path, allow_prefix=False) for path in paths
    ):
        reasons.append("invalid_changed_path")
    if not protected_shape_valid or any(
        not _valid_repo_path(path, allow_prefix=True) for path in protected
    ):
        reasons.append("invalid_protected_path")

    matched = bool(valid_config and paths) and all(
        any(_matches(path, rule) for rule in config.paths) for path in paths
    )
    if valid_config and paths and not matched:
        reasons.append("path_not_approved")
    if paths and any(_matches(path, rule) for path in paths for rule in protected):
        reasons.append("protected_path")

    if risk_status not in {"low", "risky", "unavailable"}:
        reasons.append("invalid_risk_status")
    elif risk_status != "low":
        reasons.append("risk_not_low")

    workflow_required = bool(reasons) or bool(config and config.workflow_required)
    if config and config.workflow_required:
        reasons.append("workflow_required_by_config")

    direct_allowed = False
    if not workflow_required:
        reasons.append("documentation_only")
        if protection_status not in {"unprotected", "protected", "unavailable"}:
            reasons.append("invalid_protection_status")
        elif not config.direct_default_branch_allowed:
            reasons.append("direct_default_branch_disabled")
        elif protection_status == "protected":
            reasons.append("default_branch_protected")
        elif protection_status == "unavailable":
            reasons.append("default_branch_protection_unavailable")
        else:
            direct_allowed = True
            reasons.append("direct_default_branch_allowed")

    return ApplicabilityDecision(
        workflow_required=workflow_required,
        direct_default_branch_allowed=direct_allowed,
        matched_rule="documentationOnly" if matched else None,
        paths=paths,
        reason_codes=tuple(dict.fromkeys(reasons)),
    )