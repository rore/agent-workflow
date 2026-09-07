---
id: local-doctor
title: 'Local doctor: run existing checks before push'
status: queued
priority: medium
commitment: committed
---

# Local doctor: run existing checks before push


## Summary

One local command classifies the actual change, checks its Work Records, and explains what needs attention before pushing. Humans and any coding agent use the same command. Reuse Redline and the workflow checker; add no new policy engine, enforcement predicates, or LLM judge.

The pieces already exist separately. The local Redline helper classifies committed changes; the workflow checker consumes a verdict but does not generate a fresh one. Doctor connects them and makes incomplete local coverage visible.

## Why

Classification and workflow validation currently require separate local invocations. A single preflight gives agents and humans earlier feedback without adding new checks.

## Demonstration

An agent records a small change as Routine but also modifies a shared contract classified as Elevated by repository policy. Doctor reports declared/detected risk, the triggering path/checkpoint, and the next action. The agent removes the unintended change or records the expanded scope and obtains review, then reruns.

A second example has correct risk but a missing required Work Record field. This demonstrates workflow checking beyond Redline.

Passing means the applicable checks passed for the stated inputs, not that the code is correct or CI will pass.

## Existing seams to inspect

- [Checker CLI and orchestration](../../core/checker/checker.py): run_checker, run_checker_multi, changed-file discovery, base/head arguments, verdict input.
- [Predicates](../../core/checker/predicates.py) and [enforcement reference](../../docs/ENFORCEMENT.md).
- [Redline reporter](../../core/agent-redline/core/reporter/reporter.py).
- [Local Redline helper](../../core/agent-redline/core/templates/pre-push-check.sh): committed-revision comparison and documented local/CI asymmetries.
- [Packaging](../../docs/PACKAGING.md), [integration](../../docs/INTEGRATION.md), and [packaging script](../../scripts/package-skill.sh).

## In Scope

### Command and change selection

Extend the existing CLI or add one small companion entry point consistent with consumer packaging. "Doctor" is a feature name, not a requirement for a new installed executable or package manager.

Accept repository root, base ref, and explicit Work Record selection using existing conventions. Honor configured paths and base selection; do not hardcode src/, main, or the Work Record directory.

Prefer committed branch changes from resolved merge base to HEAD for the first slice. Print exact refs/revisions and scope. Detect staged, unstaged, and untracked changes: either explicitly exclude them with at least an advisory exit or implement a coherent snapshot covering them. Never imply an excluded working tree was checked.

Classification and record parsing must refer to the same snapshot. Do not classify HEAD while silently validating a differently edited working-tree record. Use existing mechanisms where possible; document any additional snapshot mechanism before implementation.

Discover all applicable changed records using existing checker rules. Explicit selection must not silently hide other relevant records/changes. Never select the newest record by modification time. Detached HEAD requires explicit inputs when branch-based selection is necessary.

Missing base/merge base, non-repository paths, unresolved conflicts, ambiguous selection, and empty diffs need explicit outcomes. No implicit fetch, checkout, stash, commit, index mutation, or silent base substitution.

### Checks and policy

Generate a fresh Redline verdict, then pass the same changed-file and revision context to the existing workflow checker. Run applicable existing checks for:

- configuration validity;
- record presence, parsing, markers, required fields, risk/complexity shape, and valid state;
- declared versus detected risk, configured boundaries, and triggered checkpoints;
- recorded reviews/approvals, exceptions, and existing evidence/commit-order predicates.

Preserve predicate identifiers, applicability, optional/required configuration, and shadow/binding behavior. Do not invent completion requirements for in-progress tasks. If [workflow applicability](workflow-applicability.md) has shipped, consume its shared decision; otherwise preserve current rules and do not implement a separate exemption mechanism.

### Freshness and unavailable inputs

Do not treat a cached redline-verdict.json as fresh classification. Prefer an invocation-local artifact or existing in-process interface.

Report checks run, skipped, and unavailable, with reasons. Boundary adapters, generated API specs, and authoritative PR context may not be available locally. Missing required evidence cannot become a passing result; unknown freshness is not clean coverage.

Do not automatically run builds, tests, expensive generators, remote requests, or side-effecting adapters. Document supported evidence inputs and provenance. Bound child-process execution, distinguish tool failure from detected violations, and clean temporary artifacts on failure/interruption.

Keep doctor execution/coverage status separate from existing predicate results. Never fabricate a passing predicate to accommodate missing inputs.

### Output and exits

Concise output includes comparison, selected records, declared/detected risk, findings with predicate IDs/paths, unavailable checks, and next actions. Reuse existing structured output rather than building a new reporting framework.

Preserve repository exit conventions: 0 clean for the explicitly checked scope; 1 advisory/incomplete optional coverage; 2 blocking findings or failure to perform required checks. Highest severity wins. Explain whether exit 2 means a violation or an execution failure. Dirty exclusions cannot exit clean.

The command does not authenticate approvals, prove evidence adequacy, or establish that tests passed because a record says so.

### Packaging and documentation

Support the normal vendored consumer installation and this source checkout. Add one invocation to verification/review guidance and document coverage limitations. CI still evaluates authoritative inputs independently. Update the normative SPEC first if implementing this proposal changes its contract.

## Out of Scope

Stop/SessionStart hooks, plugin conversion, mandatory pre-push installation, loop detection, automatic record/risk/policy edits, new risk heuristics, semantic Scope interpretation, approval identity verification, correctness judgments, Jira, new harness adapters, dashboards, services, and paid model calls.

## Acceptance coverage

Use public CLI E2E with temporary Git consumer repos and the real reporter/checker, not only mocked verdicts. Cover at least two repo layouts and configured non-default record paths/base branches.

1. Clean routine change; understated risk; boundary violation; missing/malformed/wrong-shaped record; invalid state; missing recorded review; malformed configuration and exception. Assert existing severities.
2. Multiple records, explicit selection, ambiguous/missing selection, detached HEAD, empty diff, and changes without applicable task records.
3. Staged/unstaged/untracked changes: correct coverage or explicit non-clean exclusion. Include add/delete/rename, Unicode/spaces in paths, and conflicts.
4. Missing refs, missing/stale evidence, invalid reporter output, unavailable adapters/PR context, and timeout. None can masquerade as complete success.
5. Optional/required Redline and shadow/binding behavior; direct checker/reporter agreement for identical inputs. Document local/CI input differences.
6. No mutation of user content, index, refs, or untracked files; temporary cleanup; no unexpected network/model calls.
7. Packaged consumer execution without imports from the development checkout; supported Windows and POSIX entry points.
8. Both demonstration journeys: finding, correction, rerun, actual output.

## Notes

Inspect existing seams first. Record the chosen CLI, snapshot, discovery behavior, and coverage limits before code edits. Implement minimal orchestration, package it, and exercise the consumer CLI. Separate any proposed predicate semantic change from doctor.

## Done When

The packaged command, focused E2E, required repository checks, and accurate documentation pass. Hook support and dirty-worktree support are not prerequisites for the initial slice.
