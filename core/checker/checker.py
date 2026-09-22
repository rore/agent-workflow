"""Checker entry points.

Builds a :class:`~.predicates.CheckerContext` per slug, runs the
predicate set, aggregates the verdict, prints the JSON, and exits with
the verdict's exit code.

Slice 0 made the checker multi-record aware: a PR may change more than
one Work Record under ``.agent-workflow/tasks/`` and the checker runs
the predicate set against each. Single-record runs (local CLI, tests)
go through the same path, wrapping their one record in the standard
verdict shape.

Slice F added the per-task exceptions model. When a Work Record's
optional Exceptions field carries a valid rule waiver, the checker
runs the predicates normally and then applies a downgrade pass that
replaces any blocking-failed predicate named by an exception with the
same result at advisory disposition (annotated with the exception's
reason). Non-waivable predicates (see
:data:`core.checker.predicates._NON_WAIVABLE_PREDICATES`) are never
downgraded; an exception against them fails the
``exceptions.not_against_boundary`` predicate.

CLI:

    python -m core.checker --repo-root <path>
                           (--slug <slug> | --changed-files <path>)
                           [--redline-verdict <path>]

When ``--changed-files`` is given, the checker discovers each Work
Record path under ``.agent-workflow/tasks/`` that the file lists and
runs the predicate set against each — multi-record mode. When
``--slug`` is given, the checker runs the predicate set against that
one slug — single-record mode, equivalent to the pre-slice-0 behaviour.
When both are given, ``--changed-files`` is primary; if it cannot be
read, the run falls back to ``--slug``.

Programmatic:

    from core.checker import run_checker, run_checker_multi
    verdict = run_checker(repo_root, slug)           # single-record
    verdict = run_checker_multi(repo_root, slugs)    # multi-record
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path, PurePosixPath

import yaml
from urllib.parse import quote

from core.config import (
    Config,
    ConfigError,
    approve_documentation_only,
    evaluate_applicability,
    valid_repository_path,
)
from core.config import load as load_config_yaml
from core.work_record import WorkRecordParseError, parse_exceptions
from core.work_record.local_backend import (
    InvalidSlugError,
    InvalidTaskPathError,
    LocalBackend,
    UnsafeWorkRecordPathError,
    validate_slug,
)

from .predicates import (
    PREDICATE_SOURCE,
    PREDICATES,
    CheckerContext,
    _ALLOWED_STATES,
)
from .predicates import _NON_WAIVABLE_PREDICATES  # noqa: F401  used by downgrade pass
from .redline_verdict import RedlineVerdictError, load_redline_verdict
from .verdict import PredicateResult, RecordVerdict, Verdict, aggregate, aggregate_record


def _build_context(
    repo_root: Path,
    slug: str,
    redline_verdict_path: Path | None = None,
    base_ref: str | None = None,
    head_ref: str | None = None,
) -> CheckerContext:
    """Read the per-repo config, instantiate the backend, load the Work Record.

    Goes through ``backend.read()`` for the parsed half so the harness
    actually exercises the backend contract (rather than reading raw
    bytes and parsing in the checker, which would let the backend
    interface rot). Reads the raw file separately for the predicates
    that need the unparsed bytes (``workrecord.markers_present``).

    Loads the redline verdict from ``redline_verdict_path`` if given,
    otherwise from ``cfg.redline.verdict_path``. A missing file is fine
    (the redline predicates handle absence); a parse error is caught
    and surfaced via ``CheckerContext.redline_verdict_parse_error`` so
    ``risk.redline_findings_available`` can name it.

    Catches Work Record parse errors so the predicate set can surface
    them as structured failures rather than uncaught exceptions.
    """
    cfg = load_config_yaml(repo_root / "agent-workflow.yaml")

    # Slice scope is local-only. Jira is W18.
    if cfg.work_record.backend != "local":
        raise NotImplementedError(
            f"backend {cfg.work_record.backend!r} not yet implemented in this slice"
        )
    assert cfg.work_record.local is not None  # schema guarantees this
    backend = LocalBackend(repo_root, cfg.work_record.local.task_path)

    # Two reads, by design:
    # - backend.read() exercises the protocol (and the parser dispatch).
    #   Returns None when the file is missing; raises on malformed.
    # - the raw file read gives ``workrecord.markers_present`` the bytes
    #   it needs to evaluate marker structure independent of fields.
    path = Path(backend.resolve_location(slug))
    if not path.is_absolute():
        path = repo_root / path

    raw_text: str | None = path.read_text(encoding="utf-8") if path.exists() else None

    record = None
    shape = None
    parse_error: WorkRecordParseError | None = None
    try:
        parsed = backend.read(slug)
    except WorkRecordParseError as exc:
        parse_error = exc
    else:
        if parsed is not None:
            record = parsed.record
            shape = parsed.shape

    # Redline verdict — CLI override wins, else config default. Resolve
    # relative paths against the repo root so the same config works
    # from any CWD.
    verdict_path = redline_verdict_path or Path(cfg.redline.verdict_path)
    if not verdict_path.is_absolute():
        verdict_path = repo_root / verdict_path

    redline_verdict = None
    redline_verdict_parse_error: str | None = None
    try:
        redline_verdict = load_redline_verdict(verdict_path)
    except RedlineVerdictError as exc:
        redline_verdict_parse_error = str(exc)

    # Exceptions sub-parsing. Only attempted on the expanded shape (the
    # routine shape has no Exceptions field). Parse errors are caught
    # and surfaced via ``exceptions_parse_error`` so the predicate set
    # names them rather than crashing the run.
    exceptions: tuple = ()
    exceptions_parse_error: str | None = None
    if record is not None and shape == "expanded":
        raw_exceptions = record.get("exceptions", "")  # type: ignore[union-attr]
        if raw_exceptions:
            try:
                exceptions = tuple(parse_exceptions(raw_exceptions))
            except WorkRecordParseError as exc:
                exceptions_parse_error = str(exc)

    return CheckerContext(
        backend=backend,
        slug=slug,
        record=record,
        shape=shape,
        parse_error=parse_error,
        raw_text=raw_text,
        redline_verdict=redline_verdict,
        redline_required=cfg.redline.required,
        redline_verdict_parse_error=redline_verdict_parse_error,
        exceptions=exceptions,
        exceptions_parse_error=exceptions_parse_error,
        repo_root=repo_root,
        base_ref=base_ref,
        head_ref=head_ref,
    )


def _apply_exception_downgrades(
    results: list[PredicateResult],
    ctx: CheckerContext,
) -> list[PredicateResult]:
    """Return a new results list with blocking-failed predicates downgraded
    to advisory when a valid exception names them.

    Honoured only when:

    - ``exceptions.well_formed`` and ``exceptions.not_against_boundary``
      and ``exceptions.not_expired`` all passed — the exception block
      is itself valid and the named rule is waivable.
    - The exception's ``rule`` exactly matches a predicate name in the
      results.
    - The named predicate is blocking-failed (an exception against a
      passing predicate is a no-op; an exception against an advisory
      failure is a no-op — already non-blocking).
    - The named predicate is not in :data:`_NON_WAIVABLE_PREDICATES`
      (defence-in-depth — the not_against_boundary predicate would
      have failed first, but we check again to keep the downgrade pass
      honest).

    Downgrades use :func:`dataclasses.replace` because
    :class:`PredicateResult` is frozen. Detail is annotated with the
    exception's reason so reviewers can trace why the disposition
    changed.
    """
    if not ctx.exceptions or ctx.exceptions_parse_error is not None:
        return results

    # Refuse to downgrade if the exception block itself isn't valid.
    # Find the three exception-validity predicates in the results.
    validity_passed = True
    for r in results:
        if r.name in {
            "exceptions.well_formed",
            "exceptions.not_against_boundary",
            "exceptions.not_expired",
        } and not r.passed:
            validity_passed = False
            break
    if not validity_passed:
        return results

    by_name: dict[str, int] = {r.name: i for i, r in enumerate(results)}
    new_results = list(results)
    for exc in ctx.exceptions:
        if exc.rule in _NON_WAIVABLE_PREDICATES:
            continue
        idx = by_name.get(exc.rule)
        if idx is None:
            continue
        existing = new_results[idx]
        if existing.passed or not existing.blocking:
            continue
        new_results[idx] = dataclasses.replace(
            existing,
            blocking=False,
            detail=f"{existing.detail} — waived by exception: {exc.reason}",
        )
    return new_results


def _effective_rules(results: list[PredicateResult]) -> list[dict[str, str]]:
    """Build the effective-rules list for a record's verdict.

    Each entry is ``{"name": <predicate>, "source": <core|default|repo>}``.
    Order mirrors the predicate evaluation order. Predicates without
    a source label fall back to ``unknown`` — this surfaces drift
    between the predicate set and :data:`PREDICATE_SOURCE` loudly
    instead of silently labelling them.
    """
    return [
        {"name": r.name, "source": PREDICATE_SOURCE.get(r.name, "unknown")}
        for r in results
    ]


def _run_one(
    repo_root: Path,
    slug: str,
    redline_verdict_path: Path | None,
    base_ref: str | None = None,
    head_ref: str | None = None,
    require_implementation_ready: bool = False,
) -> RecordVerdict:
    """Run the predicate set against one slug and build its RecordVerdict.

    After predicate evaluation, applies the per-task exception downgrade
    pass (slice F) — blocking-failed predicates named by a valid
    exception become advisory. Then aggregates per-record status and
    attaches the effective-rules list.
    """
    try:
        ctx = _build_context(
            repo_root, slug, redline_verdict_path, base_ref=base_ref, head_ref=head_ref
        )
    except (InvalidSlugError, UnsafeWorkRecordPathError) as exc:
        results = [PredicateResult(
            name="workrecord.exists",
            passed=False,
            detail=f"Work Record could not be resolved: {exc}",
            blocking=True,
        )]
        record = aggregate_record(slug, results)
        return dataclasses.replace(record, effective_rules=_effective_rules(results))
    results = [predicate(ctx) for predicate in PREDICATES]
    if require_implementation_ready:
        state = (
            ctx.record["state"].rstrip(".").strip()
            if ctx.record is not None
            else None
        )
        results.append(PredicateResult(
            name="workrecord.implementation_ready",
            passed=state == "Ready to implement",
            detail=(
                "Work Record is ready for implementation."
                if state == "Ready to implement"
                else f"Work Record state {state!r} is not 'Ready to implement'."
            ),
            blocking=True,
        ))
    results = _apply_exception_downgrades(results, ctx)
    record = aggregate_record(slug, results)
    return dataclasses.replace(record, effective_rules=_effective_rules(results))


def run_checker(
    repo_root: Path,
    slug: str,
    redline_verdict_path: Path | None = None,
    base_ref: str | None = None,
    head_ref: str | None = None,
    require_implementation_ready: bool = False,
) -> Verdict:
    """Run the checker against one slug; return the wrapped verdict.

    Single-record convenience — wraps the one record into the standard
    :class:`Verdict` shape so callers (tests, local CLI, CI) treat
    single and multi uniformly.
    """
    return run_checker_multi(
        repo_root,
        [slug],
        redline_verdict_path,
        base_ref=base_ref,
        head_ref=head_ref,
        require_implementation_ready=require_implementation_ready,
    )


def run_checker_multi(
    repo_root: Path,
    slugs: list[str],
    redline_verdict_path: Path | None = None,
    base_ref: str | None = None,
    head_ref: str | None = None,
    require_implementation_ready: bool = False,
) -> Verdict:
    """Run the checker against multiple slugs; return the aggregated verdict.

    Order of ``records`` mirrors ``slugs`` so the comment output is
    stable and reviewers can scan top-to-bottom in the order CI fed
    the slugs. Each slug runs independently — a missing or malformed
    record on one does not short-circuit the others; its
    ``workrecord.exists`` / ``markers_present`` predicates surface the
    cause locally.

    Empty ``slugs`` produces a clean verdict with no records — see
    :func:`aggregate` for the rationale.
    """
    records = [
        _run_one(
            repo_root,
            s,
            redline_verdict_path,
            base_ref=base_ref,
            head_ref=head_ref,
            require_implementation_ready=require_implementation_ready,
        )
        for s in slugs
    ]
    return aggregate(records)


# ---------------------------------------------------------------------------
# Changed-files discovery and applicability
# ---------------------------------------------------------------------------

_NON_TASK_FILENAMES: frozenset[str] = frozenset({"README.md", "readme.md"})

# These governance surfaces can never exempt themselves. Repo-specific
# Redline policy adds further risk classification; this small list is the
# checker-side floor when the policy is missing or incomplete.
_PROTECTED_APPLICABILITY_PATHS: tuple[str, ...] = (
    "agent-workflow.yaml",
    "agent-redline-policy.yaml",
    ".github/",
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".claude/",
    ".agents/",
    ".codex/",
    ".opencode/",
    ".agent-redline/",
    "dist/agent-workflow/",
    "scripts/agent-workflow-check.py",
    "scripts/agent-redline-report.py",
    "core/schema/",
    "core/config/",
    "core/checker/",
    "core/skill/",
    "core/templates/",
    "core/agent-redline/",
    "docs/SPEC.md",
    "docs/DECISIONS.md",
)
_PROTECTED_INSTRUCTION_FILENAMES: frozenset[str] = frozenset(
    {"AGENTS.md", "CLAUDE.md", "GEMINI.md", "copilot-instructions.md"}
)
_WINDOWS_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def read_changed_paths(
    changed_files_path: Path,
    *,
    nul_delimited: bool = False,
) -> list[str]:
    """Read the complete path set; NUL mode preserves every filename byte."""
    if not nul_delimited:
        return [
            line.strip().replace("\\", "/")
            for line in changed_files_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    raw = changed_files_path.read_bytes()
    if not raw or not raw.endswith(b"\0"):
        raise ValueError("NUL-delimited changed-files input is empty or incomplete")
    fields = raw.split(b"\0")
    if fields[-1] != b"" or any(field == b"" for field in fields[:-1]):
        raise ValueError("NUL-delimited changed-files input contains an empty path")
    return [field.decode("utf-8") for field in fields[:-1]]


def _task_path_parts(task_path_template: str) -> tuple[str, str]:
    norm = task_path_template.replace("\\", "/")
    if norm.count("{slug}") != 1:
        return "", ""
    return tuple(norm.split("{slug}", 1))  # type: ignore[return-value]


def discover_slugs_from_changed_files(
    repo_root: Path,
    changed_files_path: Path,
    task_path_template: str = ".agent-workflow/tasks/{slug}.md",
    *,
    changed_paths: list[str] | None = None,
    nul_delimited: bool = False,
) -> list[str]:
    """Return existing changed Work Record slugs for the configured taskPath."""
    paths = changed_paths
    if paths is None:
        paths = read_changed_paths(changed_files_path, nul_delimited=nul_delimited)
    prefix, suffix = _task_path_parts(task_path_template)
    if not prefix and not suffix:
        return []

    seen: set[str] = set()
    out: list[str] = []
    for path in paths:
        norm = path if nul_delimited else path.replace("\\", "/")
        if not norm.startswith(prefix) or (suffix and not norm.endswith(suffix)):
            continue
        end = len(norm) - len(suffix) if suffix else len(norm)
        slug = norm[len(prefix):end]
        name = f"{slug}{suffix}"
        if not slug or "/" in slug or name in _NON_TASK_FILENAMES or slug.startswith("."):
            continue
        if not (repo_root / norm).exists():
            continue
        if slug not in seen:
            seen.add(slug)
            out.append(slug)
    return out


def task_path_prefix(task_path_template: str) -> str:
    """Return the static directory prefix before ``{slug}``, or empty."""
    prefix, _ = _task_path_parts(task_path_template)
    if not prefix or "/" not in prefix:
        return ""
    return prefix[: prefix.rfind("/") + 1]


def _windows_reparse_point(path: Path) -> bool:
    """Detect junctions/reparse points on Python versions without Path.is_junction."""
    if os.name != "nt":
        return False
    try:
        attrs = path.lstat().st_file_attributes
        mask = stat.FILE_ATTRIBUTE_REPARSE_POINT
    except FileNotFoundError:
        return False
    except (AttributeError, OSError):
        return True
    return bool(attrs & mask)


def _unsafe_applicability_path(repo_root: Path, path: str) -> bool:
    """Reject directories and any symlink/junction traversal, including prospective paths."""
    root = repo_root.resolve()
    candidate = repo_root / path
    try:
        candidate.resolve(strict=False).relative_to(root)
    except (OSError, ValueError):
        return True
    if candidate.is_dir():
        return True
    for ancestor in (candidate, *candidate.parents):
        if ancestor == repo_root:
            break
        try:
            if ancestor.is_symlink() or (
                hasattr(ancestor, "is_junction") and ancestor.is_junction()
            ) or _windows_reparse_point(ancestor):
                return True
        except OSError:
            return True
    return False


def _github_default_branch_protection(repo_root: Path) -> str:
    """Return a fresh GitHub protection status; any failed query is unavailable."""
    def gh(*args: str):
        try:
            result = subprocess.run(
                ["gh", *args], cwd=repo_root, capture_output=True, text=True,
                encoding="utf-8", timeout=20, check=False,
                creationflags=_WINDOWS_NO_WINDOW,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None
        if result.returncode != 0:
            return None
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return None

    view = gh("repo", "view", "--json", "nameWithOwner")
    if not isinstance(view, dict) or not isinstance(view.get("nameWithOwner"), str):
        return "unavailable"
    repo = view["nameWithOwner"]
    metadata = gh("api", f"repos/{repo}")
    if not isinstance(metadata, dict) or not isinstance(metadata.get("default_branch"), str):
        return "unavailable"
    try:
        current = subprocess.run(
            ["git", "branch", "--show-current"], cwd=repo_root,
            capture_output=True, text=True, encoding="utf-8", timeout=20, check=False,
            creationflags=_WINDOWS_NO_WINDOW,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unavailable"
    if current.returncode != 0 or current.stdout.strip() != metadata["default_branch"]:
        return "unavailable"
    branch = quote(metadata["default_branch"], safe="")
    branch_info = gh("api", f"repos/{repo}/branches/{branch}")
    rules = gh("api", f"repos/{repo}/rules/branches/{branch}")
    if (
        not isinstance(branch_info, dict)
        or not isinstance(branch_info.get("protected"), bool)
        or not isinstance(rules, list)
    ):
        return "unavailable"
    return "protected" if branch_info["protected"] or rules else "unprotected"

def _load_behavior_contract_policy(
    repo_root: Path,
) -> tuple[dict[str, object] | None, str | None]:
    path = repo_root / "agent-redline-policy.yaml"
    if not path.is_file():
        return None, None
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return None, f"could not read Redline behavior-contract policy: {exc}"
    if not isinstance(data, dict) or "behaviorContracts" not in data:
        return None, None
    block = data.get("behaviorContracts")
    if not isinstance(block, dict):
        return None, "Redline behaviorContracts must be an object"
    paths = block.get("paths")
    verification = block.get("verification")
    protection = block.get("protection", "repository")
    checkpoint = block.get("checkpoint")
    malformed = (
        not isinstance(paths, list)
        or not paths
        or not all(isinstance(pattern, str) for pattern in paths)
        or len(paths) != len(set(paths))
        or not isinstance(verification, str)
        or not verification.strip()
        or protection not in {"repository", "workflow"}
        or (
            protection == "repository"
            and (not isinstance(checkpoint, str) or not checkpoint.strip())
        )
        or (protection == "workflow" and checkpoint is not None)
    )
    if malformed:
        return None, "Redline behaviorContracts is malformed"
    for pattern in paths:
        exact = pattern[:-3] if pattern.endswith("/**") else pattern
        if (
            not exact
            or any(char in exact for char in "*?[]{}")
            or not valid_repository_path(exact, allow_prefix=False)
        ):
            return None, f"Redline behaviorContracts contains unsafe path {pattern!r}"
    return {
        "paths": paths,
        "verification": verification,
        "protection": protection,
        "checkpoint": checkpoint,
    }, None


def _behavior_contract_policy_matches(path: str, pattern: str) -> bool:
    if pattern.endswith("/**"):
        return path.startswith(pattern[:-2])
    return path == pattern


def _behavior_contract_evidence_record(detail: str) -> RecordVerdict:
    result = PredicateResult(
        name="behavior_contracts.redline_evidence_complete",
        passed=False,
        detail=detail,
        blocking=True,
    )
    record = aggregate_record("<behavior-contracts>", [result])
    return dataclasses.replace(
        record,
        effective_rules=[{"name": result.name, "source": "repo"}],
    )


def _contract_changed_path_valid(repo_root: Path, path: str) -> bool:
    return valid_repository_path(path) and not _unsafe_applicability_path(repo_root, path)


def _verification_reference_present(text: str, identifier: str) -> bool:
    token = r"[A-Za-z0-9_.-]"
    return re.search(rf"(?<!{token}){re.escape(identifier)}(?!{token})", text) is not None


def _behavior_contract_record(
    repo_root: Path,
    redline: RedlineVerdict,
    slugs: list[str],
    paths: list[str],
    *,
    paths_complete: bool,
    redline_verdict_path: Path | None,
    base_ref: str | None,
    head_ref: str | None,
) -> RecordVerdict:
    """Check Redline-reported behavior contracts against trusted PR paths."""
    detail = redline.behavior_contract_changes
    assert detail is not None and detail["detected"]
    repository_protection = detail["version"] == 1
    affected = (
        [entry["path"] for entry in detail["paths"]]
        if repository_protection
        else list(detail["paths"])
    )
    owners_by_path = (
        {
            entry["path"]: set(entry["owners"])
            for entry in detail["paths"]
        }
        if repository_protection
        else {}
    )

    paths_safe = all(_contract_changed_path_valid(repo_root, path) for path in paths)
    paths_unique = len(paths) == len(set(paths))
    affected_safe = all(
        _contract_changed_path_valid(repo_root, path)
        for path in affected
    )
    affected_current = set(affected).issubset(paths)
    affected_red = set(affected).issubset(redline.zones.get("red", []))
    complete = (
        paths_complete
        and paths_safe
        and paths_unique
        and affected_safe
        and affected_current
        and affected_red
    )

    owners_compatible = True
    checkpoint_reported = True
    checkpoint = detail.get("checkpoint")
    if repository_protection:
        owner_sets = {
            tuple(sorted(owners))
            for owners in owners_by_path.values()
        }
        owners_compatible = (
            bool(affected)
            and all(owners_by_path.values())
            and len(owner_sets) == 1
        )
        checkpoint_reported = any(
            item.get("id") == checkpoint
            for item in redline.checkpoints
        )
    authority_configured = owners_compatible and checkpoint_reported

    contexts: list[CheckerContext] = []
    if complete:
        for slug in slugs:
            try:
                contexts.append(_build_context(
                    repo_root,
                    slug,
                    redline_verdict_path,
                    base_ref=base_ref,
                    head_ref=head_ref,
                ))
            except (InvalidSlugError, UnsafeWorkRecordPathError):
                continue

    entries: dict[str, list[tuple[object, CheckerContext]]] = {
        path: [] for path in affected
    }
    for ctx in contexts:
        if ctx.record is None:
            continue
        for change in ctx.record.get("behavior_changes", []):  # type: ignore[union-attr]
            if change.target == "repository-contract" and change.path in entries:
                entries[change.path].append((change, ctx))

    classified = complete and all(len(entries[path]) == 1 for path in affected)
    authorized = classified and authority_configured
    classification_detail: list[str] = []
    authorization_detail: list[str] = []
    affected_contexts: dict[str, CheckerContext] = {}
    if repository_protection and not owners_compatible:
        authorization_detail.append(
            "affected paths need one compatible non-empty CODEOWNERS authority set"
        )
    if repository_protection and not checkpoint_reported:
        authorization_detail.append(
            f"Redline did not report configured checkpoint {checkpoint!r}"
        )
    for path in affected:
        matches = entries[path]
        if len(matches) != 1:
            classification_detail.append(
                f"{path!r} has {len(matches)} repository-contract entries; expected exactly one"
            )
            continue
        change, ctx = matches[0]
        affected_contexts[ctx.slug] = ctx
        classification_detail.append(f"{path!r} classified as {change.classification}")
        if change.classification != "requirement-change":
            continue
        authority = change.authority
        approval = change.approval
        if repository_protection:
            owners = owners_by_path[path]
            valid_approval = (
                authority is not None
                and authority.scope == "repository"
                and authority.name in owners
                and approval is not None
                and approval.by == authority.name
            )
            expected = (
                f"repository authority and approval.by from one of {sorted(owners)!r}"
            )
        else:
            valid_approval = (
                authority is not None
                and authority.scope == "task"
                and authority.name == "task-owner"
                and approval is not None
                and approval.by == "user"
            )
            expected = "task-scoped task-owner authority and approval.by 'user'"
        if not valid_approval:
            authorized = False
            authorization_detail.append(f"{path!r} requires {expected}")

    verification = detail["verification"]
    verification_linked = classified and any(
        _verification_reference_present(
            str(ctx.record.get("verification", ""))
            + "\n"
            + str(ctx.record.get("verification_plan", "")),
            verification,
        )
        for ctx in affected_contexts.values()
        if ctx.record is not None
    )
    if not paths_complete:
        complete_detail = "trusted NUL changed-path evidence is missing or incomplete."
    elif not paths_safe or not affected_safe:
        complete_detail = "changed-path evidence contains an unsafe or non-normalized path."
    elif not paths_unique:
        complete_detail = "changed-path evidence contains duplicate paths."
    elif not affected_current:
        complete_detail = "Redline reported a behavior-contract path outside the current diff."
    elif not affected_red:
        complete_detail = "Redline reported a behavior-contract path that is not classified red."
    else:
        complete_detail = "trusted NUL paths and Redline behavior-contract evidence agree."

    if repository_protection:
        authorized_detail = (
            "repository requirement changes reference canonical CODEOWNERS authority."
        )
    else:
        authorized_detail = (
            "workflow protection uses task-owner/user approval evidence; "
            "the user is not authenticated as repository authority and merge is not enforced."
        )
    results = [
        PredicateResult(
            name="behavior_contracts.changed_paths_complete",
            passed=complete,
            detail=complete_detail,
            blocking=True,
        ),
        PredicateResult(
            name="behavior_contracts.changed_paths_classified",
            passed=classified,
            detail=(
                "all affected repository contracts have exactly one classification."
                if classified
                else "; ".join(classification_detail)
                or "contract path classification is unavailable."
            ),
            blocking=True,
        ),
        PredicateResult(
            name="behavior_contracts.requirement_changes_authorized",
            passed=authorized,
            detail=(
                authorized_detail
                if authorized
                else "; ".join(authorization_detail)
                or "repository contract classifications are not authorized."
            ),
            blocking=True,
        ),
        PredicateResult(
            name="behavior_contracts.verification_linked",
            passed=verification_linked,
            detail=(
                f"an affected Work Record references reported verification "
                f"{verification!r}."
                if verification_linked
                else f"no affected Work Record references reported verification "
                f"{verification!r}."
            ),
            blocking=True,
        ),
    ]
    record = aggregate_record("<behavior-contracts>", results)
    return dataclasses.replace(
        record,
        effective_rules=[{"name": result.name, "source": "repo"} for result in results],
    )


def _append_record(verdict: Verdict, record: RecordVerdict) -> Verdict:
    return aggregate([*verdict.records, record])

def _synthetic_verdict(
    slug: str,
    results: list[PredicateResult],
    *,
    source: str,
) -> Verdict:
    record = aggregate_record(slug, results)
    record = dataclasses.replace(
        record,
        effective_rules=[{"name": result.name, "source": source} for result in results],
    )
    return aggregate([record])


_WORK_RECORD_REF_PREFIX = "agent-workflow:"
_RESOLVER_SLUG_PREFIXES = ("slice/", "feat/", "feature/", "fix/", "bug/", "chore/", "demo/")


def _resolver_result(
    status: str,
    reason: str,
    *,
    work_record_ref: str | None = None,
    slug: str | None = None,
    record_path: str | None = None,
    record_state: str | None = None,
    message: str | None = None,
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "status": status,
        "reason": reason,
        "work_record_ref": work_record_ref,
        "slug": slug,
        "record_path": record_path,
        "record_state": record_state,
        "message": None if message is None else message[:512],
    }


def _resolver_error(reason: str, exc: object) -> dict[str, object]:
    return _resolver_result("error", reason, message=str(exc) or reason)


def _resolve_work_record(
    repo_root: Path,
    supplied_ref: str | None,
) -> dict[str, object]:
    slug: str | None = None
    if supplied_ref is not None:
        if not supplied_ref.startswith(_WORK_RECORD_REF_PREFIX):
            return _resolver_error(
                "invalid_work_record_ref",
                f"reference must start with {_WORK_RECORD_REF_PREFIX!r}",
            )
        slug = supplied_ref[len(_WORK_RECORD_REF_PREFIX):]
        try:
            validate_slug(slug)
        except InvalidSlugError as exc:
            return _resolver_error("invalid_work_record_ref", exc)

    config_path = repo_root / "agent-workflow.yaml"
    try:
        config_path.stat()
    except FileNotFoundError:
        return _resolver_result("absent", "workflow_not_configured")
    except OSError as exc:
        return _resolver_error("invalid_config", exc)
    if not config_path.is_file():
        return _resolver_error("invalid_config", "agent-workflow.yaml is not a file")

    try:
        cfg = load_config_yaml(config_path)
    except (ConfigError, OSError, UnicodeError) as exc:
        return _resolver_error("invalid_config", exc)
    if cfg.work_record.backend != "local" or cfg.work_record.local is None:
        return _resolver_error(
            "unsupported_backend",
            f"backend {cfg.work_record.backend!r} does not support local resolution",
        )
    try:
        backend = LocalBackend(repo_root, cfg.work_record.local.task_path)
    except InvalidTaskPathError as exc:
        return _resolver_error("invalid_config", exc)

    if slug is None:
        try:
            current = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=repo_root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=20,
                check=False,
                creationflags=_WINDOWS_NO_WINDOW,
            )
        except (OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
            return _resolver_error("git_unavailable", exc)
        if current.returncode != 0:
            return _resolver_error(
                "git_unavailable",
                current.stderr.strip() or f"git exited {current.returncode}",
            )
        branch = current.stdout.strip()
        if not branch:
            return _resolver_result("absent", "current_record_unavailable")
        slug = branch
        for prefix in _RESOLVER_SLUG_PREFIXES:
            if slug.startswith(prefix):
                slug = slug[len(prefix):]
                break
        slug = slug.replace("/", "-")
        try:
            validate_slug(slug)
        except InvalidSlugError as exc:
            return _resolver_error("invalid_work_record_ref", exc)

    work_record_ref = f"{_WORK_RECORD_REF_PREFIX}{slug}"
    try:
        record_path = backend.resolve_location(slug)
    except (InvalidSlugError, UnsafeWorkRecordPathError, OSError) as exc:
        return _resolver_error("unsafe_record_path", exc)

    try:
        parsed = backend.read(slug)
    except UnsafeWorkRecordPathError as exc:
        return _resolver_error("unsafe_record_path", exc)
    except WorkRecordParseError as exc:
        return _resolver_error("malformed_record", exc)
    except UnicodeError as exc:
        return _resolver_error("malformed_record", exc)
    except OSError as exc:
        return _resolver_error("unreadable_record", exc)
    if parsed is None:
        return _resolver_result(
            "absent",
            "record_not_found",
            work_record_ref=work_record_ref,
            slug=slug,
            record_path=record_path,
        )

    record_state = parsed.record["state"].rstrip(".").strip()
    if record_state not in _ALLOWED_STATES:
        return _resolver_error(
            "invalid_record_state",
            f"unsupported Work Record state {record_state!r}",
        )
    return _resolver_result(
        "found",
        "record_found",
        work_record_ref=work_record_ref,
        slug=slug,
        record_path=record_path,
        record_state=record_state,
    )


def _emit_resolver_result(result: dict[str, object]) -> int:
    payload = (json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    if len(payload) > 8192:
        result = _resolver_error("unsafe_record_path", "resolver output exceeds 8192 bytes")
        payload = (json.dumps(result, separators=(",", ":")) + "\n").encode("utf-8")
    sys.stdout.buffer.write(payload)
    return 2 if result["status"] == "error" else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agent-workflow-check",
        description="Validate workflow compliance for a task or a complete PR path set.",
    )
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--slug", default=None)
    parser.add_argument("--resolve-work-record", action="store_true")
    parser.add_argument("--work-record-ref")
    changed = parser.add_mutually_exclusive_group()
    changed.add_argument(
        "--changed-files",
        type=Path,
        help="Legacy newline-delimited paths; supported but never grants applicability.",
    )
    changed.add_argument(
        "--changed-files-z",
        type=Path,
        help="Complete NUL-delimited paths from `git diff --name-only -z --no-renames`.",
    )
    parser.add_argument("--redline-verdict", type=Path, default=None)
    parser.add_argument(
        "--require-implementation-ready",
        action="store_true",
        help="Require the resolved Work Record state to be Ready to implement.",
    )
    parser.add_argument("--bootstrap-applicability-proposal-z", type=Path)
    parser.add_argument("--bootstrap-applicability-approved-z", type=Path)
    parser.add_argument("--bootstrap-direct-default-branch-approved", action="store_true")
    parser.add_argument(
        "--bootstrap-protection-status",
        choices=("unprotected", "protected", "unavailable"),
    )
    parser.add_argument("--base-ref", type=str, default=None)
    parser.add_argument("--head-ref", type=str, default=None)
    parser.add_argument(
        "--check-default-branch-protection", action="store_true",
        help="Query GitHub live before reporting direct-default-branch eligibility.",
    )
    args = parser.parse_args(argv)

    if args.work_record_ref is not None and not args.resolve_work_record:
        parser.error("--work-record-ref requires --resolve-work-record")
    if args.resolve_work_record:
        incompatible = any((
            args.slug is not None,
            args.changed_files is not None,
            args.changed_files_z is not None,
            args.redline_verdict is not None,
            args.require_implementation_ready,
            args.bootstrap_applicability_proposal_z is not None,
            args.bootstrap_applicability_approved_z is not None,
            args.bootstrap_direct_default_branch_approved,
            args.bootstrap_protection_status is not None,
            args.base_ref is not None,
            args.head_ref is not None,
            args.check_default_branch_protection,
        ))
        if incompatible:
            parser.error(
                "--resolve-work-record cannot be combined with validation or bootstrap options"
            )
        return _emit_resolver_result(
            _resolve_work_record(args.repo_root.resolve(), args.work_record_ref)
        )

    bootstrap_proposal = args.bootstrap_applicability_proposal_z
    if bootstrap_proposal is not None:
        if args.bootstrap_applicability_approved_z is None or args.bootstrap_protection_status is None:
            parser.error("bootstrap applicability needs proposal, approved paths, and protection status")
        try:
            discovered = read_changed_paths(bootstrap_proposal, nul_delimited=True)
            approved_file = args.bootstrap_applicability_approved_z
            approved = (
                [] if approved_file.read_bytes() == b""
                else read_changed_paths(approved_file, nul_delimited=True)
            )
            rule = approve_documentation_only(
                discovered,
                approved,
                direct_default_branch_approved=args.bootstrap_direct_default_branch_approved,
                protection_status=args.bootstrap_protection_status,
            )
        except (OSError, UnicodeError, ValueError) as exc:
            print(f"bootstrap applicability approval failed: {exc}", file=sys.stderr)
            return 2
        fragment = None if rule is None else {
            "paths": list(rule.paths),
            "workflowRequired": rule.workflow_required,
            "directDefaultBranchAllowed": rule.direct_default_branch_allowed,
        }
        print(json.dumps(fragment))
        return 0

    changed_path = args.changed_files_z or args.changed_files
    trusted_paths = args.changed_files_z is not None
    if args.slug is None and changed_path is None:
        parser.error("at least one of --slug, --changed-files, or --changed-files-z is required")

    repo_root = args.repo_root.resolve()
    cfg = None
    config_error: str | None = None
    try:
        cfg = load_config_yaml(repo_root / "agent-workflow.yaml")
    except Exception as exc:
        config_error = str(exc)

    paths: list[str] = []
    slugs: list[str] = []
    changed_record_slugs: list[str] = []
    discovery_succeeded = False
    if changed_path is not None:
        try:
            paths = read_changed_paths(changed_path, nul_delimited=trusted_paths)
            task_template = (
                cfg.work_record.local.task_path
                if cfg is not None and cfg.work_record.local is not None
                else ".agent-workflow/tasks/{slug}.md"
            )
            slugs = discover_slugs_from_changed_files(
                repo_root,
                changed_path,
                task_template,
                changed_paths=paths,
                nul_delimited=trusted_paths,
            )
            changed_record_slugs = list(slugs)
            discovery_succeeded = True
        except (OSError, UnicodeError, ValueError) as exc:
            print(
                f"warning: --changed-files path {str(changed_path)!r} could not be read: {exc}; "
                "falling back to --slug if supplied.",
                file=sys.stderr,
            )

    if args.slug is not None and not slugs:
        if not discovery_succeeded:
            slugs = [args.slug]
        elif cfg is not None and cfg.work_record.local is not None:
            try:
                backend = LocalBackend(repo_root, cfg.work_record.local.task_path)
                wr_path = repo_root / backend.resolve_location(args.slug)
                if wr_path.is_file():
                    slugs = [args.slug]
            except Exception:
                pass

    if config_error is not None:
        verdict = _synthetic_verdict(
            args.slug or "<configuration>",
            [PredicateResult(
                name="config.valid",
                passed=False,
                detail=f"agent-workflow.yaml could not be loaded: {config_error}",
                blocking=True,
            )],
            source="repo",
        )
    elif changed_path is not None and not discovery_succeeded and not slugs:
        verdict = _synthetic_verdict(
            args.slug or "<changed-files>",
            [PredicateResult(
                name="changed_paths.complete",
                passed=False,
                detail="changed-path input was unreadable or incomplete; workflow applicability cannot be decided.",
                blocking=True,
            )],
            source="core",
        )
    else:
        verdict = run_checker_multi(
            repo_root,
            slugs,
            redline_verdict_path=args.redline_verdict,
            base_ref=args.base_ref,
            head_ref=args.head_ref,
            require_implementation_ready=args.require_implementation_ready,
        )

    redline = None
    redline_error: str | None = None
    risk_status = "unavailable"
    if cfg is not None:
        verdict_path = args.redline_verdict or Path(cfg.redline.verdict_path)
        if not verdict_path.is_absolute():
            verdict_path = repo_root / verdict_path
        try:
            redline = load_redline_verdict(verdict_path)
        except RedlineVerdictError as exc:
            redline_error = str(exc)
        if redline is not None and trusted_paths and discovery_succeeded:
            risk_status = redline.applicability_risk_status(paths)
            if any(_unsafe_applicability_path(repo_root, path) for path in paths):
                risk_status = "risky"

    applicability = None
    protection_status = (
        _github_default_branch_protection(repo_root)
        if args.check_default_branch_protection
        else "unavailable"
    )
    documentation_only = (
        cfg.applicability.documentation_only
        if cfg is not None and cfg.applicability is not None
        else None
    )
    if trusted_paths and discovery_succeeded and cfg is not None and not verdict.records:
        protected_paths = list(_PROTECTED_APPLICABILITY_PATHS)

        protected_paths.extend(
            path
            for path in paths
            if PurePosixPath(path).name in _PROTECTED_INSTRUCTION_FILENAMES
        )
        if cfg.work_record.local is not None:
            prefix = task_path_prefix(cfg.work_record.local.task_path)
            if prefix:
                protected_paths.append(prefix)
        applicability = evaluate_applicability(
            paths,
            risk_status,
            protection_status,
            protected_paths,
            documentation_only,
        )
        if not applicability.workflow_required:
            verdict = _synthetic_verdict(
                "<documentation-only>",
                [PredicateResult(
                    name="workflow.applicability",
                    passed=True,
                    detail=(
                        "all changed paths are in the human-approved documentation-only set; "
                        "Work Record not required. "
                        + (
                            "Direct-default-branch is allowed by the fresh unprotected result."
                            if applicability.direct_default_branch_allowed
                            else "Direct-default-branch is not allowed: "
                            + ", ".join(applicability.reason_codes)
                        )
                    ),
                    blocking=True,
                )],
                source="repo",
            )

    must_have_wr = bool(
        cfg is not None
        and cfg.work_record.local is not None
        and (
            cfg.work_record.required_for_branch_changes
            or (trusted_paths and documentation_only is not None)
        )
    )
    if (
        changed_path is not None
        and discovery_succeeded
        and not verdict.records
        and must_have_wr
        and cfg is not None
        and cfg.work_record.local is not None
    ):
        prefix = task_path_prefix(cfg.work_record.local.task_path)
        non_wr_paths = [path for path in paths if not prefix or not path.startswith(prefix)]
        blocking_paths = (
            paths
            if trusted_paths and documentation_only is not None and applicability is not None
            else non_wr_paths
        )
        if blocking_paths:
            examples = ", ".join(repr(path) for path in blocking_paths[:3])
            more = f" (+{len(blocking_paths) - 3} more)" if len(blocking_paths) > 3 else ""
            results = [PredicateResult(
                name="workrecord.required_for_branch_changes",
                passed=False,
                detail=(
                    f"change requires a Work Record; no changed record resolved. Paths: "
                    f"{examples}{more}. Create the branch Work Record or, when no "
                    "applicability policy is configured, explicitly set "
                    "`workRecord.requiredForBranchChanges: false`."
                ),
                blocking=True,
            )]
            if trusted_paths and documentation_only is not None and applicability is not None:
                results.append(PredicateResult(
                    name="workflow.applicability",
                    passed=False,
                    detail="documentation-only exemption denied: " + ", ".join(applicability.reason_codes),
                    blocking=True,
                ))
            if trusted_paths and (redline is None or redline_error is not None):
                results.append(PredicateResult(
                    name="risk.redline_findings_available",
                    passed=False,
                    detail=(
                        f"redline verdict failed to parse: {redline_error}"
                        if redline_error
                        else "redline verdict missing; applicability requires complete risk evidence."
                    ),
                    blocking=True,
                ))
            if redline is not None and redline.has_boundary_violation:
                results.append(PredicateResult(
                    name="risk.boundary_violation_absent",
                    passed=False,
                    detail="boundary violation prevents workflow exemption.",
                    blocking=True,
                ))
            verdict = _synthetic_verdict(args.slug or "<branch slug>", results, source="core")

    behavior_policy, behavior_policy_error = _load_behavior_contract_policy(repo_root)
    behavior_detail = redline.behavior_contract_changes if redline is not None else None
    behavior_evidence_error = behavior_policy_error
    if behavior_evidence_error is None and behavior_policy is None and behavior_detail is not None:
        behavior_evidence_error = (
            "Redline reported behavior contracts but the current policy has no behaviorContracts block"
        )
    elif behavior_evidence_error is None and behavior_policy is not None:
        if behavior_detail is None:
            behavior_evidence_error = (
                "current Redline behaviorContracts policy has no matching versioned verdict detail"
            )
        else:
            protection = behavior_policy["protection"]
            expected_version = 1 if protection == "repository" else 2
            if behavior_detail["version"] != expected_version:
                behavior_evidence_error = (
                    "current Redline policy and verdict disagree on behavior-contract protection"
                )
            else:
                expected = {
                    path
                    for path in paths
                    if any(
                        _behavior_contract_policy_matches(path, pattern)
                        for pattern in behavior_policy["paths"]
                    )
                }
                reported = (
                    {entry["path"] for entry in behavior_detail["paths"]}
                    if protection == "repository"
                    else set(behavior_detail["paths"])
                )
                if expected != reported:
                    behavior_evidence_error = (
                        "current Redline policy and verdict disagree on affected behavior-contract paths"
                    )
                elif behavior_detail["verification"] != behavior_policy["verification"]:
                    behavior_evidence_error = (
                        "current Redline policy and verdict disagree on behavior-contract controls"
                    )
                elif (
                    protection == "repository"
                    and behavior_detail["checkpoint"] != behavior_policy["checkpoint"]
                ):
                    behavior_evidence_error = (
                        "current Redline policy and verdict disagree on behavior-contract controls"
                    )
    if behavior_evidence_error is not None:
        verdict = _append_record(
            verdict,
            _behavior_contract_evidence_record(behavior_evidence_error),
        )
    elif behavior_detail is not None and behavior_detail["detected"]:
        verdict = _append_record(
            verdict,
            _behavior_contract_record(
                repo_root,
                redline,
                changed_record_slugs,
                paths,
                paths_complete=trusted_paths and discovery_succeeded,
                redline_verdict_path=args.redline_verdict,
                base_ref=args.base_ref,
                head_ref=args.head_ref,
            ),
        )
    payload = json.dumps(verdict.to_dict(), indent=2, ensure_ascii=False) + "\n"
    sys.stdout.buffer.write(payload.encode("utf-8"))
    return verdict.exit_code

if __name__ == "__main__":  # pragma: no cover - exercised via __main__
    sys.exit(main())
