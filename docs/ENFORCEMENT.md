# What the CI checker enforces

Single source for "what does the agent-workflow CI gate actually block on". Each row names a predicate, what it checks, its disposition, and how to fix a failure.

The checker is in [`core/checker/`](../core/checker/). It runs in CI via [`core/templates/.github/workflows/agent-workflow.yml.template`](../core/templates/.github/workflows/agent-workflow.yml.template). It is vendored into each consuming repo as a single-file `scripts/agent-workflow-check.py`.

## How the checker behaves

The checker reads:

- `agent-workflow.yaml` at the repo root (backend selection, classifier integration).
- The Work Record at `<taskPath substituted with {slug}>`, where the slug comes from the PR's source branch.
- The risk classifier's verdict artifact at the path configured by `redlineVerdictPath` (when CI ran the classifier first).

It runs every predicate against every Work Record the PR touched (multi-record mode), aggregates the results into a single verdict, and posts a sticky comment on the PR. Exit codes:

| Exit | Meaning | Effect on CI |
|---|---|---|
| `0` | Every predicate passed. | Job green. |
| `1` | Advisory failures only. | Job green. Sticky surfaces the warning. |
| `2` | At least one blocking predicate failed. | Job red. Merge blocks if the check is required. |

The checker does **not** call out to GitHub or any external service. It reads files. It is reproducible offline: running `python scripts/agent-workflow-check.py --repo-root . --slug <slug>` locally produces the same JSON CI produces.

## Predicate reference

Disposition column legend:

- **Blocking** — failure exits 2.
- **Advisory** — failure exits 1.
- **Non-waivable** — cannot be downgraded by a task exception (see §Exceptions below).

### Structural — does this Work Record exist and parse

| Predicate | Checks | Disposition | Fix |
|---|---|---|---|
| `workrecord.exists` | A file resolves at the configured `taskPath` for the slug. | Blocking, non-waivable | Create the Work Record at the path the predicate names. Slug is derived from the branch — see "Slug derivation" below. |
| `workrecord.markers_present` | The marker pair `<!-- agent-workflow:start --> … <!-- agent-workflow:end -->` bounds a single block. | Blocking, non-waivable | Use [`core/templates/work-record-routine.md`](../core/templates/work-record-routine.md) or [`work-record-expanded.md`](../core/templates/work-record-expanded.md) as the reference. |
| `workrecord.required_for_branch_changes` | When `--changed-files` lists code paths but the checker resolved no Work Record at the branch slug, this synthetic predicate names the missing record. Fires only at PR time (not on `--slug`-only local runs). | Blocking (default). Opt out per-repo with `workRecord.requiredForBranchChanges: false` in `agent-workflow.yaml` for genuine housekeeping repos. | Create the Work Record for this branch, or set the opt-out flag if this PR really is housekeeping. |

### Classification — is the risk/complexity declaration valid

| Predicate | Checks | Disposition | Fix |
|---|---|---|---|
| `risk.declared` | The `Risk:` field is one of `Routine`, `Elevated`, `High`. | Blocking, non-waivable | Set the Risk field. `Boundary Violation` is not a valid Work Record value — the workflow must stop before a record is written. |
| `complexity.declared` | The `Complexity:` field is one of `Simple`, `Moderate`, `Large`. | Blocking, non-waivable | Set the Complexity field. |
| `workrecord.shape_matches_classification` | The record's actual shape matches `(Risk, Complexity)`: compact only at `(Routine, Simple)`, expanded everywhere else. | Blocking, non-waivable | Migrate the record between compact/expanded as needed. The expanded shape requires Discovery, Material assumptions, Plan, Verification plan, Plan review, Approvals. |
| `workrecord.routine_fields_present` *(compact records only)* | Every compact-path field is present and non-empty. | Blocking | Fill in the missing field named in the detail. |
| `workrecord.expanded_fields_present` *(expanded records only)* | Every expanded-path field is present and non-empty. | Blocking | Fill in the missing field named in the detail. |
| `workrecord.state_valid` | The `State:` value is one of `Ready to implement`, `Blocked`, `Blocked or returned to planning`, `Ready for review`. | Blocking | Set the State to one of the allowed values. |

### Classifier — does the declared risk match the diff

The classifier (the `agent-redline` job in CI) runs first and writes a JSON **verdict artifact** to the path configured by `redlineVerdictPath` (default `build/redline-verdict.json`). The agent-workflow job reads that artifact; the predicates below verify what's recorded in the Work Record against what the classifier detected on the diff.

The "redline" prefix in these predicate names is the literal identifier in the verdict JSON. It refers to the bundled risk-classification subsystem (`agent-redline-policy.yaml`); see [`INTEGRATION.md`](INTEGRATION.md#risk-classification-and-how-to-keep-it-useful) for how to configure and tune it.

| Predicate | Checks | Disposition | Fix |
|---|---|---|---|
| `risk.redline_findings_available` | The classifier's verdict artifact is present and parsed. | Blocking under `redline: required`; advisory under `redline: optional`. Always blocking when the file exists but failed to parse. | Check the classifier CI job. A missing artifact under `redline: required` is a CI configuration error. |
| `risk.boundary_violation_absent` | No architectural-boundary violation was flagged on the diff. | Blocking, non-waivable | A boundary violation stops the workflow. Either remove the offending change or change the governing policy through its own reviewed change. Boundary-violation findings are **never** waivable through a task exception (SPEC §11). |
| `risk.declared_not_below_detected` | The declared Risk meets the minimum the classifier detected on the diff. | Blocking | Re-classify upward in the Work Record. Migrate the record's shape if it crosses the `(Routine, Simple)` boundary. |

### Review — are the right reviews recorded

| Predicate | Checks | Disposition | Fix |
|---|---|---|---|
| `review.checkpoints_satisfied` | Every classifier-triggered checkpoint is satisfied (PR label or CODEOWNER approval). | Disposition follows the redline policy's `modes` (`perCheck.report` if set, else `modes.default`): **blocking** under `binding`, **advisory** under `shadow`. Non-waivable via task exception either way. | Apply the satisfying label named in the detail, or get the named CODEOWNER review. During the calibration window (`modes.default: shadow`), unmet checkpoints surface in the sticky as advisory and don't block CI. |
| `approval.elevated_clean_context_review_present` | At Risk=Elevated, the `Plan review:` field references a real review (or a `## Plan review` section in the file carries the prose). | Blocking | Run the clean-context plan review and record it. See [`core/templates/checkpoints/plan-and-review.md`](../core/templates/checkpoints/plan-and-review.md). |
| `approval.high_risk_approval_recorded` | At Risk=High, the `Approvals:` field carries a verbatim `Approved by user <timestamp>: "<quote>"` line. | Blocking | The human must explicitly approve; record the response verbatim. |
| `approval.clean_context_does_not_satisfy_human` | At Risk=High, the Plan review reference and the Approvals text are not the same. | Blocking, non-waivable | Record a distinct human approval; a clean-context review **MUST NOT** satisfy a human-approval requirement (SPEC §13.4). |

### Verification — are completion criteria mapped

| Predicate | Checks | Disposition | Fix |
|---|---|---|---|
| `evidence.criteria_have_methods` | On expanded records, each Verification plan line pairs a completion criterion with a verification method. | Advisory | Use one of the accepted grammars: `criterion → method`, `criterion -> method`, `criterion — method`, `method: criterion`, or `manual: <description>`. |
| `evidence.failure_not_claimed_as_success` | Implementation / Evidence prose does not name a failed/skipped check as the basis for `Ready for review`. | Advisory *(temporarily downgraded — slice E)* | Re-read your evidence prose. A failed required check **MUST NOT** be presented as success (SPEC §9.6). |
| `workrecord.commit_order` | The Work Record's first commit on this branch lands at or before the first code commit on the same branch. Walks `origin/main..HEAD` first-parent history. | Advisory | If this fails, the WR was likely written retroactively. Check whether plan-first discipline held — if a session had been killed mid-task, would the WR have been useful as recovery state? Non-blocking. Skipped when git isn't available or the branch has no WR file yet. |

### Exceptions — are recorded waivers well-formed

| Predicate | Checks | Disposition | Fix |
|---|---|---|---|
| `exceptions.well_formed` | Each entry in the optional Exceptions field parses with the required sub-fields. | Blocking, non-waivable | Use the dash-bullet format with `rule`, `reason`, `scope`, `approver`, `expiry?`, `compensating_validation`. |
| `exceptions.not_against_boundary` | No exception names a non-waivable predicate. | Blocking, non-waivable | Remove the entry — non-waivable predicates cannot be downgraded. The current set is listed in [§Non-waivable predicates](#non-waivable-predicates). |
| `exceptions.not_expired` | No exception has an expiry date in the past. ISO `YYYY-MM-DD`. | Blocking, non-waivable | Renew the exception through its approval path, or remove it and address the underlying finding. |

## Slug derivation

The slug is the per-task identifier — the `{slug}` substituted into the `taskPath` template. The checker derives it from the PR's source branch:

1. Strip the first matching prefix: `slice/`, `feat/`, `feature/`, `fix/`, `bug/`, `chore/`, `demo/`.
2. Replace remaining `/` with `-`.

If the PR touched Work Records (the `--changed-files` mode used in CI), each touched record is checked. If `--changed-files` finds no records, the checker falls back to `--slug` and validates the Work Record at the configured `taskPath` for that slug — closing the case where a feature branch's WR landed on an earlier commit and this push touches only code. PRs with no matching WR at the slug AND code paths in the diff fail blocking via `workrecord.required_for_branch_changes` by default — set `workRecord.requiredForBranchChanges: false` in `agent-workflow.yaml` to opt out for genuine housekeeping repos (vendored-script bumps, formatter passes).

## Non-waivable predicates

A task exception **MUST NOT** downgrade these. The list is enforced by `exceptions.not_against_boundary`.

- `risk.boundary_violation_absent` — SPEC §11.
- `workrecord.exists`, `workrecord.markers_present`, `risk.declared`, `complexity.declared`, `workrecord.shape_matches_classification` — preconditions; without them the verdict is unreliable.
- `exceptions.well_formed`, `exceptions.not_against_boundary`, `exceptions.not_expired` — circular waivers are not honoured.
- `approval.clean_context_does_not_satisfy_human` — SPEC §13.4 structural invariant.
- `review.checkpoints_satisfied` — SPEC §13.4 (checkpoint satisfaction MUST remain distinct from human approval). Disposition is mode-dependent (blocking under `binding`, advisory under `shadow`), but a task exception cannot waive it either way.

## What the checker does NOT enforce

By design. Each is a reviewer judgment:

- Whether the Work Record's prose accurately describes the change.
- Whether the discovery was thorough.
- Whether the plan is sound.
- Whether the implementation is correct.
- Whether the verification method actually proves the criterion. Today the checker validates **structural mapping** (each Verification plan line names a method via one of the accepted grammars) and scans for **explicit contradictions** (a failure marker and a success marker against the same test identifier). Both are advisory. SPEC §13.3 names a fuller contract — presence, status, revision, freshness of the Verification Record — as the target shape; status/revision/freshness enforcement is not yet implemented and lives on the PR-status side of the harness. The checker does **not** validate adequacy — whether the named check meaningfully proves the criterion — in any slice; that stays a reviewer judgment.
- Whether tests pass. GitHub already knows that — the workflow does not re-verify CI results.
- Whether a human actually wrote a given approval. Per the 2026-06-23 decision the checker enforces that something approval-shaped is recorded; the cheating window is acknowledged.

If you find the checker passing on something a reviewer should have caught, that is by design — the gates the checker enforces are structural. Human review remains the authority for everything else.

## Where to read more

- [`SPEC.md`](SPEC.md) — the normative workflow and harness contract.
- [`INTEGRATION.md`](INTEGRATION.md#risk-classification-and-how-to-keep-it-useful) — what the risk classifier does in agent-workflow's context, how to configure and tune the policy.
- [`DEFAULT_PROFILE.md`](DEFAULT_PROFILE.md) — default profile mapping (GitHub, CI, Redline).
- [`../core/checker/predicates.py`](../core/checker/predicates.py) — the predicate source. Each predicate has a docstring matching its row above.
