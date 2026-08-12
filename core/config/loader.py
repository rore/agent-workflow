"""``agent-workflow.yaml`` loader.

Reads a YAML config, validates against the JSON Schema at
``core/schema/agent-workflow.schema.json``, and exposes a typed view.

Slice Step 2 covers only the ``workRecord`` block; further fields land
incrementally as their owning backlog items are picked up.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jsonschema
import yaml

# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


class ConfigError(ValueError):
    """Raised when the config file is missing, unreadable, or invalid.

    Carries a short, human-readable reason. Callers (the checker, the
    skill driver, bootstrap) translate it into named-predicate failures
    in their own surfaces.
    """


@dataclass(frozen=True)
class LocalBackendConfig:
    """Options for the local Markdown Work Record backend."""

    task_path: str
    """Repo-relative path template, e.g. ``.agent-workflow/tasks/{slug}.md``."""


@dataclass(frozen=True)
class WorkRecordConfig:
    """Work Record backend selection plus backend-specific options."""

    backend: str
    """``local`` or ``jira``."""

    local: LocalBackendConfig | None
    """Populated when ``backend == 'local'``; ``None`` otherwise."""

    required_for_branch_changes: bool = True
    """When True (default), the CI checker emits a blocking
    ``workrecord.required_for_branch_changes`` predicate when a PR
    touched code paths but resolved no Work Record at the branch slug.
    Set to ``False`` to allow pure-housekeeping PRs (vendored-script
    bumps, formatter-only passes) through without a Work Record.
    Schema-default is ``True`` so the harness's "every engineering
    task has a Work Record" contract is on by default."""

    # Jira options are intentionally absent here; W18 introduces them
    # alongside the Jira backend implementation. The schema reserves the
    # shape so config files written today are forward-compatible.


@dataclass(frozen=True)
class RedlineConfig:
    """agent-redline integration options.

    Slice B introduces both fields; they default per the docstrings
    when omitted from the YAML so existing configs (which pre-date this
    slice) keep working unchanged.
    """

    required: bool
    """``True`` when ``redline: required`` (the default). ``False``
    when ``redline: optional`` (an explicit opt-out — the CI checker
    treats a missing verdict as advisory instead of blocking)."""

    verdict_path: str
    """Path the checker reads to find redline's verdict JSON. Default:
    ``build/redline-verdict.json``."""


@dataclass(frozen=True)
class Config:
    """Typed view of the per-repo ``agent-workflow.yaml``.

    Only fields the current slice consumes are surfaced. The raw mapping
    is kept on :attr:`raw` for forward compatibility — callers that want
    to peek at an unsupported field can read it without waiting for the
    loader to grow a typed accessor.
    """

    version: int
    project_name: str
    work_record: WorkRecordConfig
    redline: RedlineConfig
    raw: dict[str, Any]


# ---------------------------------------------------------------------------
# Schema location
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCHEMA_PATH = _REPO_ROOT / "core" / "schema" / "agent-workflow.schema.json"


def _schema() -> dict[str, Any]:
    """Read the schema fresh on each call.

    Schemas don't change at runtime, but caching adds complexity for no
    win in a non-hot path. The check layer's full run loads it a handful
    of times at most.
    """
    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ConfigError(f"config file not found: {path}") from exc
    except OSError as exc:
        raise ConfigError(f"could not read config file {path}: {exc}") from exc

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ConfigError(f"config file {path} is not valid YAML: {exc}") from exc

    if data is None:
        raise ConfigError(f"config file {path} is empty")
    if not isinstance(data, dict):
        raise ConfigError(
            f"config file {path} must be a YAML mapping at the top level "
            f"(got {type(data).__name__})"
        )
    return data


def _validate(data: dict[str, Any]) -> None:
    """Raise :exc:`ConfigError` if ``data`` does not match the schema.

    Uses ``jsonschema``'s draft-2020-12 validator; reports the first
    error with its JSON Pointer-style path so the failing field is
    obvious without a debugger.
    """
    validator = jsonschema.Draft202012Validator(_schema())
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    if not errors:
        return

    first = errors[0]
    path = "/".join(str(p) for p in first.absolute_path) or "(root)"
    raise ConfigError(f"config invalid at {path}: {first.message}")


def _to_config(data: dict[str, Any]) -> Config:
    """Pull validated data into the typed Config view.

    Validation has already enforced presence and types of the fields we
    read here, so no defensive `get()`-with-default — a missing field
    would be a schema bug, not a runtime case to handle.

    Optional top-level fields with their own defaults (``redline``,
    ``redlineVerdictPath``) DO use ``.get()`` with explicit defaults —
    the schema permits their absence and the defaults are documented as
    part of the loader contract.
    """
    work_record = data["workRecord"]
    backend = work_record["backend"]

    local: LocalBackendConfig | None
    if backend == "local":
        local_block = work_record["local"]
        local = LocalBackendConfig(task_path=local_block["taskPath"])
    else:
        # backend == "jira" — full options land with W18. Surface as
        # None so callers that try to use it before then see an
        # obvious failure rather than a silent half-config.
        local = None

    redline = RedlineConfig(
        required=data.get("redline", "required") == "required",
        verdict_path=data.get("redlineVerdictPath", "build/redline-verdict.json"),
    )

    return Config(
        version=data["version"],
        project_name=data["project"]["name"],
        work_record=WorkRecordConfig(
            backend=backend,
            local=local,
            required_for_branch_changes=bool(
                work_record.get("requiredForBranchChanges", True)
            ),
        ),
        redline=redline,
        raw=data,
    )


def load(path: Path | str) -> Config:
    """Read, validate, and return the typed config at ``path``.

    Raises :exc:`ConfigError` on any failure: missing file, bad YAML,
    schema violation. The error message names the offending field where
    possible.
    """
    data = _load_yaml(Path(path))
    _validate(data)
    return _to_config(data)
