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
import sys
from pathlib import Path

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
# Changed-files discovery (slice 0)
# ---------------------------------------------------------------------------

# Files under the tasks directory that are not Work Records. The Work
# Record contract is "one task per .md file"; everything else here is
# documentation or hygiene.
_NON_TASK_FILENAMES: frozenset[str] = frozenset({"README.md", "readme.md"})


def discover_slugs_from_changed_files(
    repo_root: Path,
    changed_files_path: Path,
) -> list[str]:
    """Read ``changed_files_path``; return slugs of changed Work Records.

    The file is a newline-delimited list of repo-relative paths (the
    output shape of ``git diff --name-only``). A path qualifies as a
    Work Record when:

    - it sits under ``.agent-workflow/tasks/``,
    - it has a ``.md`` extension,
    - its basename is not in :data:`_NON_TASK_FILENAMES`,
    - its basename does not start with ``.`` (dotfiles),
    - the file still exists on disk (so deleted records don't
      contribute — deletion implies the task is no longer this PR's
      concern).

    Returns slugs in the order they appeared in ``changed_files_path``,
    deduplicated. Slugs are derived as ``Path(filename).stem`` — i.e.
    the filename without the ``.md`` extension. The order is preserved
    so the verdict comment reads in the order CI fed the diff.
    """
    raw = changed_files_path.read_text(encoding="utf-8")
    seen: set[str] = set()
    out: list[str] = []
    tasks_prefix = ".agent-workflow/tasks/"
    for line in raw.splitlines():
        path = line.strip()
        if not path:
            continue
        # Normalise Windows-style separators just in case.
        norm = path.replace("\\", "/")
        if not norm.startswith(tasks_prefix):
            continue
        name = norm[len(tasks_prefix):]
        # Reject paths that include nested subdirectories — tasks are
        # flat under the directory.
        if "/" in name:
            continue
        if not name.endswith(".md"):
            continue
        if name in _NON_TASK_FILENAMES:
            continue
        if name.startswith("."):
            continue
        # Filter out deleted files — git diff includes them, we don't
        # want to "validate" a record that no longer exists.
        full = repo_root / norm
        if not full.exists():
            continue
        slug = Path(name).stem
        if slug not in seen:
            seen.add(slug)
            out.append(slug)
    return out


def read_changed_paths(changed_files_path: Path) -> list[str]:
    """Read ``changed_files_path`` and return all non-empty repo-relative
    paths, in input order. Windows-style separators are normalised to ``/``.

    Used by F5's ``workrecord.required_for_branch_changes`` synthesis to
    decide whether a PR with zero discovered Work Records was pure
    housekeeping (no code paths) or a forgotten Work Record (code paths
    present). The sibling :func:`discover_slugs_from_changed_files`
    filters this list further to Work Record paths only; this one keeps
    everything.

    Raises :exc:`FileNotFoundError` when the path is unreadable, same as
    the discover sibling, so the caller treats both signals uniformly.
    """
    raw = changed_files_path.read_text(encoding="utf-8")
    out: list[str] = []
    for line in raw.splitlines():
        path = line.strip()
        if not path:
            continue
        out.append(path.replace("\\", "/"))
    return out


def task_path_prefix(task_path_template: str) -> str:
    """Return the directory prefix of a Work Record taskPath template.

    Strips the trailing ``{slug}.md`` (or anything after the last ``/``)
    so a template like ``.agent-workflow/tasks/{slug}.md`` produces
    ``.agent-workflow/tasks/``. Trailing slash is preserved so a simple
    ``path.startswith(prefix)`` test classifies WR paths cleanly.

    Returns the empty string when the template has no ``/`` — a
    pathological config we can't infer a prefix from. Callers must
    treat empty as "skip; can't classify safely" rather than as a
    prefix that matches every path; treating an empty prefix as
    "everything is non-WR" would let the F5 synthesis fire on
    WR-adjacent paths in a malformed config.
    """
    norm = task_path_template.replace("\\", "/")
    idx = norm.rfind("/")
    if idx < 0:
        return ""
    return norm[: idx + 1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agent-workflow-check",
        description=(
            "Validate workflow compliance for one or more Work Records. "
            "Use --changed-files for PR-time multi-record discovery; use "
            "--slug for single-record runs (local invocations, fallback "
            "when --changed-files yields zero)."
        ),
    )
    parser.add_argument(
        "--repo-root",
        required=True,
        type=Path,
        help="Path to the repository root (the directory containing agent-workflow.yaml).",
    )
    parser.add_argument(
        "--slug",
        default=None,
        help=(
            "Task slug; selects the Work Record file under the "
            "configured taskPath. Used when --changed-files is not "
            "supplied, or as a fallback when --changed-files cannot be "
            "read. Not used when --changed-files was supplied and "
            "discovery succeeded (even if it yielded zero records — "
            "see the 'PR touched no Work Records' case below)."
        ),
    )
    parser.add_argument(
        "--changed-files",
        type=Path,
        default=None,
        help=(
            "Path to a newline-delimited file listing changed paths "
            "(typically `git diff --name-only ...` piped to a file). "
            "The checker discovers each changed Work Record and runs "
            "the predicate set per record. When this is supplied and "
            "discovery yields zero (a PR that touched no Work Records), "
            "the checker exits clean — that's not a failure, and "
            "--slug does not override it."
        ),
    )
    parser.add_argument(
        "--redline-verdict",
        type=Path,
        default=None,
        help=(
            "Path to redline's verdict JSON. Overrides the configured "
            "redlineVerdictPath; CI uses this to point at the artifact "
            "downloaded from the redline job."
        ),
    )
    parser.add_argument(
        "--base-ref",
        type=str,
        default=None,
        help=(
            "Git ref or SHA marking the PR's base. Used by the "
            "workrecord.commit_order advisory predicate to walk the "
            "branch's commit history. Defaults to BASE_SHA env var, "
            "then to 'origin/main'. CI workflows should pass the "
            "PR's actual base SHA so the synthetic pull/N/merge "
            "commit doesn't collapse the branch's history to one."
        ),
    )
    parser.add_argument(
        "--head-ref",
        type=str,
        default=None,
        help=(
            "Git ref or SHA marking the PR's head. Pairs with "
            "--base-ref. Defaults to HEAD_SHA env var, then to "
            "'HEAD'. On a pull/N/merge checkout, HEAD is the "
            "synthetic merge commit; passing the real PR head SHA "
            "lets the commit-order predicate see the actual branch."
        ),
    )
    args = parser.parse_args(argv)

    if args.slug is None and args.changed_files is None:
        parser.error("at least one of --slug or --changed-files is required")

    repo_root = args.repo_root.resolve()

    slugs: list[str] = []
    discovery_succeeded = False
    if args.changed_files is not None:
        try:
            slugs = discover_slugs_from_changed_files(repo_root, args.changed_files)
            discovery_succeeded = True
        except FileNotFoundError:
            # changed-files path was supplied but didn't resolve (e.g. CI
            # step that produces it crashed, or an operator passed an
            # inline value instead of a file path). Fall back to --slug
            # if we have one — better to validate the branch's record
            # than to exit silent on a broken signal. ``discovery_succeeded``
            # stays False from its initialiser, no reassignment needed.
            print(
                f"warning: --changed-files path {str(args.changed_files)!r} "
                f"could not be read; falling back to --slug if supplied. "
                f"(Pass a path to a newline-delimited file of changed paths, "
                f"not an inline value.)",
                file=sys.stderr,
            )

    # --slug fallback fires in two cases:
    #   (a) --changed-files was not supplied or failed to read; OR
    #   (b) discovery succeeded with zero records but --slug names an
    #       existing Work Record at the configured taskPath.
    #
    # Case (b) closes the F1 hole: a PR that touched only code (no
    # task-file diff) on a branch whose Work Record was already
    # committed in an earlier push still validates against that
    # record. Without it, code-only PRs ship with `records: []` and a
    # green verdict regardless of whether the branch has a Work Record
    # at all. With it, the branch's WR must exist at the path bootstrap
    # configured.
    #
    # Pure housekeeping PRs (vendored-script bumps, formatter passes
    # without a feature branch) that have no matching WR fall through
    # to `records: []` — the WR file simply doesn't exist at the slug
    # so the fallback contributes nothing. This is the documented
    # `riskNone` / housekeeping case.
    # Config — loaded once and reused. Both the --slug fallback and the
    # F5 missing-WR check need it. If it can't be loaded (no
    # agent-workflow.yaml, malformed file), both fallbacks stay
    # conservative; downstream code defaults to existing behaviour.
    cfg = None
    try:
        cfg = load_config_yaml(repo_root / "agent-workflow.yaml")
    except Exception:
        cfg = None

    if args.slug is not None and not slugs:
        if not discovery_succeeded:
            slugs = [args.slug]
        else:
            # Discovery succeeded but yielded zero records. Probe the
            # configured taskPath for a record at --slug; if one exists,
            # validate against it (the "WR landed on an earlier commit"
            # case). If not, leave slugs empty (the "pure housekeeping"
            # case).
            if cfg is not None and cfg.work_record.local is not None:
                try:
                    backend = LocalBackend(
                        repo_root, cfg.work_record.local.task_path
                    )
                    wr_path = repo_root / backend.resolve_location(args.slug)
                    if wr_path.is_file():
                        slugs = [args.slug]
                except Exception:
                    # If backend instantiation fails, the fallback can't
                    # decide — stay conservative, leave slugs empty.
                    pass

    verdict = run_checker_multi(
        repo_root,
        slugs,
        redline_verdict_path=args.redline_verdict,
        base_ref=args.base_ref,
        head_ref=args.head_ref,
    )

    # F5 — forgotten Work Record predicate. When `--changed-files`
    # discovery succeeded but turned up zero records AND the diff
    # touched code paths outside the configured task-path prefix AND
    # the per-repo config keeps the default
    # `workRecord.requiredForBranchChanges: true`, surface a synthetic
    # blocking record so a code-only PR with no Work Record fails CI
    # instead of exiting `records: []`. Distinguishes "pure
    # housekeeping" (explicit opt-out) from "agent forgot the Work
    # Record" (the case this predicate catches).
    if (
        args.changed_files is not None
        and discovery_succeeded
        and not verdict.records
        and cfg is not None
        and cfg.work_record.required_for_branch_changes
        and cfg.work_record.local is not None
    ):
        tpath_prefix = task_path_prefix(cfg.work_record.local.task_path)
        # An empty prefix would mean the taskPath template has no `/`
        # (pathological config) — without a way to tell which paths are
        # WR-adjacent we'd be guessing, so skip the synthesis rather
        # than block on false-positive non-WR paths. The existing
        # `workrecord.exists` predicate path catches an unresolvable
        # taskPath via its own diagnostics.
        if tpath_prefix:
            try:
                all_paths = read_changed_paths(args.changed_files)
            except FileNotFoundError:
                all_paths = []
            non_wr_paths = [p for p in all_paths if not p.startswith(tpath_prefix)]
            if non_wr_paths:
                examples = ", ".join(non_wr_paths[:3])
                more = (
                    f" (+{len(non_wr_paths) - 3} more)"
                    if len(non_wr_paths) > 3
                    else ""
                )
                slug_hint = args.slug or "<branch slug>"
                pred = PredicateResult(
                    name="workrecord.required_for_branch_changes",
                    passed=False,
                    detail=(
                        f"PR touched code paths but resolved no Work Record at "
                        f"{tpath_prefix}{slug_hint}.md. Non-WR paths in this "
                        f"PR: {examples}{more}. Either create the Work Record "
                        f"for this branch, or set "
                        f"`workRecord.requiredForBranchChanges: false` in "
                        f"`agent-workflow.yaml` to opt this repo out (for "
                        f"genuine housekeeping repos)."
                    ),
                    blocking=True,
                )
                synth = aggregate_record(slug_hint, [pred])
                # Preserve effective_rules so the comment formatter
                # surfaces the rule under the "core" source. The name
                # is also in PREDICATE_SOURCE so any callers that look
                # it up by name see the same source attribution.
                synth = dataclasses.replace(
                    synth,
                    effective_rules=[
                        {
                            "name": "workrecord.required_for_branch_changes",
                            "source": "core",
                        }
                    ],
                )
                verdict = aggregate([synth])

    # Force UTF-8 on stdout regardless of platform default — verdict
    # details can contain Unicode (em-dash, arrows, emoji). CI on Linux
    # works fine; this keeps local invocations on Windows working too.
    payload = json.dumps(verdict.to_dict(), indent=2, ensure_ascii=False) + "\n"
    sys.stdout.buffer.write(payload.encode("utf-8"))
    return verdict.exit_code


if __name__ == "__main__":  # pragma: no cover - exercised via __main__
    sys.exit(main())
