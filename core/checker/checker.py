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
import stat
import subprocess
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import quote

from core.config import approve_documentation_only, evaluate_applicability
from core.config import load as load_config_yaml
from core.work_record import WorkRecordParseError, parse_exceptions
from core.work_record.local_backend import LocalBackend

from .predicates import (
    PREDICATE_SOURCE,
    PREDICATES,
    CheckerContext,
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
) -> RecordVerdict:
    """Run the predicate set against one slug and build its RecordVerdict.

    After predicate evaluation, applies the per-task exception downgrade
    pass (slice F) — blocking-failed predicates named by a valid
    exception become advisory. Then aggregates per-record status and
    attaches the effective-rules list.
    """
    ctx = _build_context(repo_root, slug, redline_verdict_path, base_ref=base_ref, head_ref=head_ref)
    results = [predicate(ctx) for predicate in PREDICATES]
    results = _apply_exception_downgrades(results, ctx)
    record = aggregate_record(slug, results)
    return dataclasses.replace(record, effective_rules=_effective_rules(results))


def run_checker(
    repo_root: Path,
    slug: str,
    redline_verdict_path: Path | None = None,
    base_ref: str | None = None,
    head_ref: str | None = None,
) -> Verdict:
    """Run the checker against one slug; return the wrapped verdict.

    Single-record convenience — wraps the one record into the standard
    :class:`Verdict` shape so callers (tests, local CLI, CI) treat
    single and multi uniformly.
    """
    return run_checker_multi(repo_root, [slug], redline_verdict_path, base_ref=base_ref, head_ref=head_ref)


def run_checker_multi(
    repo_root: Path,
    slugs: list[str],
    redline_verdict_path: Path | None = None,
    base_ref: str | None = None,
    head_ref: str | None = None,
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
        _run_one(repo_root, s, redline_verdict_path, base_ref=base_ref, head_ref=head_ref)
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

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agent-workflow-check",
        description="Validate workflow compliance for a task or a complete PR path set.",
    )
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--slug", default=None)
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

    if config_error is not None and changed_path is not None:
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
        )

    redline = None
    redline_error: str | None = None
    risk_status = "unavailable"
    if trusted_paths and discovery_succeeded and cfg is not None:
        verdict_path = args.redline_verdict or Path(cfg.redline.verdict_path)
        if not verdict_path.is_absolute():
            verdict_path = repo_root / verdict_path
        try:
            redline = load_redline_verdict(verdict_path)
        except RedlineVerdictError as exc:
            redline_error = str(exc)
        if redline is not None:
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

    payload = json.dumps(verdict.to_dict(), indent=2, ensure_ascii=False) + "\n"
    sys.stdout.buffer.write(payload.encode("utf-8"))
    return verdict.exit_code

if __name__ == "__main__":  # pragma: no cover - exercised via __main__
    sys.exit(main())
