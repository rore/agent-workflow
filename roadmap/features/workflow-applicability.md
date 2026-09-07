---
id: workflow-applicability
title: 'Configurable workflow applicability and direct-main exceptions'
status: shipped
priority: medium
commitment: committed
---

# Configurable workflow applicability and direct-main exceptions


## Summary

Users repeatedly tell agents that a small class of work, such as roadmap-only updates, may go directly to main without a Work Record or the engineering workflow. Today the installed instructions require a task branch and record, so a standing repository preference must be restated each session.

Provide one repository-owned, deterministic applicability policy understood by agent instructions, local checks, and CI. A qualifying roadmap-only change may skip the workflow and use main when explicitly configured. Mixed or uncertain changes retain normal requirements.

This is not a blanket exemption for documentation or a way to disable independent repository checks.

## Why

Standing repository preferences should not require repeated user corrections or unnecessary task branches and Work Records for qualifying edits.

## Motivating example

A repository explicitly allows changes confined to its configured roadmap paths to:
- omit a Work Record and workflow checkpoints;
- be made on main.

An agent adds a roadmap idea without creating a branch or record. If it also edits runtime code, a schema, policy, CI, or another non-exempt file, the exception no longer covers the change. The agent reassesses before that edit and follows the normal workflow.

A README link accompanying a roadmap item is NOT implicitly exempt: the repository must explicitly include that path or the combined change follows the normal workflow.

## Design decisions required before implementation

1. Separate "workflow required?" from "direct main allowed?". Skipping the workflow need not authorize direct-main edits, and neither decision authorizes commit, push, merge, deployment, or bypass of branch protection.
2. Define a small config shape in agent-workflow.yaml using existing schema/config patterns. Start with explicit repo-relative path rules; no prose classifier, LLM, new policy language, or speculative rule engine.
3. Define precedence against Redline. A path exemption must not waive an architectural-boundary violation or a protected governance surface. The config, policies, schemas, CI definitions, and agent instructions controlling applicability must not exempt themselves.
4. Define the change set: prospective explicit scope for agent guidance, actual staged/unstaged/untracked changes for local decisions, and authoritative PR/push diff for CI. Report any unavailable coverage rather than assume exemption.
5. Define interaction with existing records: an exemption must not silently ignore a changed malformed Work Record, delete records, or rewrite their state.

This proposal records desired behavior, not a normative change. Update SPEC, schema, and enforcement documentation through the normal engineering process when implementing it.

## In Scope

- No configuration means current workflow and branch requirements remain unchanged.
- A change is exempt only when every relevant changed path qualifies, required inputs are valid, and no protected exclusion applies. Unknown or mixed scope uses the normal workflow.
- Support configured roadmap locations rather than hardcoding roadmap/. Match paths relative to the repo with documented separators, glob semantics, case behavior, and rename handling.
- Renames must consider both old and new paths. Deletions, untracked files, paths with spaces/Unicode, and files outside the repo must not evade the decision.
- Return a shared structured decision: workflow required/exempt, direct-main permission, matched rule, and explanatory paths/reason. Empty changes must be explicit, not permission for arbitrary future edits.
- Evaluate intended scope before demanding a task branch or Work Record. Re-evaluate as scope changes and against the actual diff at enforcement time.
- If scope expands beyond the exception, create/update the normal task record and use the required branch before proceeding with non-exempt work. Preserve existing user edits; no automatic reset, stash, or destructive checkout.
- Explicit user instructions still govern the current session. This feature makes standing repository preferences durable; it must not pretend a config flag authenticates approval.
- Missing/invalid config, unresolved diffs, or ambiguous paths cannot produce a silent exemption. Explain the error and retain normal requirements.
- CI skips only the workflow obligations the shared applicability decision explicitly exempts. Tests, lint, security checks, Redline boundaries, and branch protection remain independently applicable.
- No Work Record should be required merely to explain why a configured exemption needs no Work Record. Report the exemption in existing CLI/CI output.
- Avoid per-turn overhead: evaluate at task pickup, material scope changes, local validation, and CI, not by starting a background service.

## Existing seams to inspect

- [Operating mode](../../core/skill/operating-mode.md): unconditional task-branch and Work Record requirements.
- [Config schema](../../core/schema/agent-workflow.schema.json) and checker config loading.
- [Checker](../../core/checker/checker.py), [predicates](../../core/checker/predicates.py), and [enforcement reference](../../docs/ENFORCEMENT.md): changed-file discovery and record-required rules.
- [Bootstrap](../../core/skill/bootstrap-mode.md), installed hook templates, and [integration guide](../../docs/INTEGRATION.md): avoid instructions that contradict configured exemptions.
- [Local doctor proposal](local-doctor.md): consume the same applicability decision if available, not a separate interpretation.

Keep rule evaluation in one reusable place. Harness-specific instructions and hooks consume its outcome; CI must independently evaluate the actual change. Preserve existing users by default and package updates through the normal distribution flow.

## Acceptance coverage

Caller-surface E2E should exercise a packaged consumer install and the real local/CI entry points using temporary Git repos.

1. No config: existing branch and record requirements unchanged.
2. Configured roadmap-only create/edit/delete: no required record; direct-main permission follows its separate setting.
3. Workflow-exempt but direct-main-disallowed change: still requires the configured branch behavior.
4. Roadmap plus code, README, config, schema, CI, or protected instruction edit: not exempt unless an ordinary non-protected path is explicitly included; protected governance cannot self-exempt.
5. Intended exempt scope expands mid-task: decision changes, guidance transitions to normal workflow, user edits preserved.
6. Rename across exemption boundaries; staged/unstaged/untracked combinations; Unicode/spaces; path normalization; invalid/outside-repo paths.
7. Invalid config, unknown rules, missing base, unavailable change set, empty diff, multiple records, and a changed malformed record.
8. Shadow/binding and boundary interactions: workflow exemption never erases independent blocking findings.
9. Local guidance and CI agree for the same paths/config; CI catches non-exempt files omitted from an agent's claimed scope.
10. At least two layouts and roadmap paths; supported Windows/POSIX behavior; no network/model calls or unrelated file mutation.

## Done When

Done when one documented config policy drives consistent agent guidance, local checking, and CI; the motivating roadmap-only-on-main journey needs no repeated user correction; mixed changes reliably return to normal enforcement; packaged tests pass.

## Out of Scope

Do not add blanket documentation exemptions, risk downgrades, auto-approval, direct pushes/merges, branch-protection changes, workflow bypass based on commit-message keywords, or a new task manager. This feature does not depend on doctor shipping.

## Notes

This is planned OSS work. Keep the existing workflow behavior until an explicit repository policy opts into exemptions.
