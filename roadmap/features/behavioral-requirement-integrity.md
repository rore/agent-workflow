---
id: behavioral-requirement-integrity
title: 'Behavioral requirement integrity'
status: queued
priority: high
commitment: committed
---

# Behavioral requirement integrity

## Summary

Prevent an agent from silently weakening what a task or repository requires so
that an incomplete implementation can pass its rewritten Work Record or tests.

Protect behavior at two levels:

1. the Task Context established before discovery and planning;
2. repository-designated behavioral contract artifacts backed by required CI.

Implementation and verification mechanics may change. A material requirement
change needs an explicit decision from the human authorized for that requirement.

## Problem

### Task-local requirement drift

A Work Record may begin with the correct behavioral outcome, constraints, scope,
and completion criteria. When discovery or implementation reveals that the
requirement is difficult, unsafe, or incompatible with the chosen approach, an
agent can currently return to planning, weaken the Work Record, update tests, and
continue. The workflow then becomes internally consistent while the original
requirement has disappeared.

Pallium PR #167 required:

- a message to wake an unloaded Codex recipient automatically;
- the recipient workspace to remain unchanged.

When safe cold wake proved unavailable, the Work Record and tests were weakened
to queue delivery until a later manual resume. The workflow recorded the new
decision but did not recognize that required behavior had changed.

### Repository-level behavioral regression

A task Work Record cannot restate every behavioral commitment accumulated by a
product. A later change can break behavior omitted from its current record.
Repositories may already express durable behavior through acceptance, end-to-end,
contract, or regression tests. When a human designates those artifacts as
authoritative, future tasks inherit their behavioral commitments.

Agents remain free to change implementation and test mechanics. They must not
silently remove, weaken, disable, or narrow an established product requirement.

## Goal and principle

> Agents may change how a requirement is implemented or verified. They may not
> materially weaken, remove, narrow, or redefine required behavior without
> explicit approval from the human authorized for that requirement.

Requirements may be wrong, impossible, obsolete, ambiguous, or unsafe. Discovery
of that fact is legitimate. It triggers a blocked decision, not permission for
the implementing agent to redefine the requirement.

The existing specification already requires escalation when product intent is
infeasible, unsafe, contradictory, or materially ambiguous. This feature makes
that rule operational and adds protection for durable repository behavior that
the current task may not mention.

## Part A: Task-local requirement integrity

### Requirement baseline

When Establish Task Context completes, before discovery or planning may change
its meaning, capture these fields as the immutable task-local baseline:

- Outcome
- Scope
- Constraints
- Completion criteria

Use an immutable authoritative source revision when one exists; otherwise retain
the initial values in the Work Record. Do not wait until the first **Ready to
implement** transition: that would allow discovery or planning to weaken
requirements before the snapshot exists.

Later approved changes update the current Task Context but never rewrite the
baseline. Result review compares the current context with the baseline and the
complete chain of approved Behavior changes entries.

Target remains structural identity rather than a behavioral commitment.

The protected unit is Task Context as a behavioral commitment, not four
independent fields. A Scope edit that excludes a previously required case is a
requirement change even when Outcome, Constraints, and Completion criteria are
textually unchanged.

If the task originates in an authoritative external requirement system, preserve
and reference that identity. Do not silently narrow it while translating it into
the Work Record or replace it with a competing local source of truth.

### Behavior change classifications

Both compact and expanded Work Records may carry an optional, machine-readable
Behavior changes record. It adds no routine ceremony when requirements remain
unchanged.

Every material difference from the baseline or protected repository behavior is
classified as:

- **equivalent** — wording or mechanics changed without changing behavior;
- **coverage-only** — verification covers more of the same requirement without
  creating a new product obligation;
- **requirement-change** — behavior is removed, weakened, narrowed, deferred,
  made best-effort, or otherwise redefined.

A stricter or broader product guarantee is also **requirement-change**; it is not
automatically safe because it appears stronger. Adding supported platforms,
states, inputs, or guarantees creates a new product obligation. Adding test cases
that merely exercise an unchanged obligation is **coverage-only**.

Equivalent refinements include:

- making a criterion more precise without changing its meaning;
- correcting terminology;
- splitting one criterion into equivalent criteria;
- replacing an implementation-oriented criterion with the same observable
  outcome;
- clarifying ambiguity before implementation without narrowing the behavior.

A change is **requirement-change** when it:

- removes or weakens required behavior;
- changes when or where the behavior applies;
- adds a fallback that no longer satisfies the original requirement;
- turns automatic behavior into manual or deferred behavior;
- turns guaranteed behavior into best-effort behavior;
- reduces supported cases, platforms, states, runtimes, or inputs;
- converts an observable requirement into a weaker implementation proxy;
- changes a constraint so previously forbidden behavior becomes permitted;
- introduces a materially broader or stricter product commitment.

For example, changing "sending to an unloaded recipient automatically wakes it"
to "delivery remains pending until the recipient is resumed" is a requirement
change. Changing "recipient workspace must remain unchanged" to "recipient
workspace should normally remain unchanged" is also a requirement change.

### Required workflow

When discovery, planning, implementation, or verification reveals that a
baseline requirement should materially change:

1. Stop implementation.
2. Set Work Record State to **Blocked**.
3. Preserve the baseline and record:
   - the affected field, contract, or requirement;
   - exact current and proposed behavior;
   - why the original cannot or should not be preserved;
   - impact of the change;
   - known alternatives;
   - required approval authority.
4. Ask that human explicitly whether to change the requirement.
5. Do not continue under the replacement until approval is recorded.
6. After approval:
   - append the verbatim approval and authoritative reference when available;
   - update the current Task Context, leaving the baseline unchanged;
   - rerun affected planning and review;
   - update the Verification Plan;
   - reassess Risk when the technical impact warrants it.

The approval binds the exact previous and proposed behavior. It is not blanket
permission for later or wider changes. Clean-context agent review cannot satisfy
the human requirement.

Task-local approval comes from the human who owns the current task requirement.
Repository-wide contract changes use repository-defined authority. The checker
validates structure and available evidence; it does not claim to authenticate
arbitrary prose.

### Routine tasks

Routine/Simple tasks gain no extra field content or checkpoint when behavior is
unchanged. If they require a behavioral change, they block and use the same
optional Behavior changes record. Approval alone does not force migration to an
Elevated classification or expanded Work Record; Risk still describes the
impact of an incorrect implementation.

Behavior-change approval and Risk are separate dimensions:

- Risk controls implementation and review rigor.
- Behavioral authority controls who may change what the product must do.

## Part B: Repository behavioral contracts

### Configuration and adoption

Allow a repository to configure authoritative contract artifacts, initially with
one minimal shape such as:

    behaviorContracts:
      paths:
        - tests/behavior/**
        - tests/relay/contracts/**
      verification: relay-behavior-contracts

The exact verification representation may reference an existing required CI job
or repository verification surface. A redundant **policy: protected** option is
unnecessary while protection is the only supported policy.

Configured paths provide mutation integrity. They do not by themselves provide
regression enforcement. Adoption therefore requires the configured suite to
already run in required CI, or to name an existing required verification check.
Agent Workflow reuses that surface; it does not become a test runner.

Configured contract paths are protected governance surfaces and cannot qualify
for the documentation-only workflow exemption.

### Contract semantics

Files under configured paths express authoritative behavioral requirements that
future tasks inherit.

Agents may:

- add coverage for an existing requirement;
- refactor test mechanics while preserving behavior;
- rename or reorganize tests without losing the represented behavior;
- replace one test implementation with an equivalent test;
- improve coverage.

Without repository-authorized approval, agents may not:

- delete an existing requirement;
- weaken its assertion;
- skip or disable it;
- narrow supported cases;
- replace it with a weaker proxy;
- change expected behavior in a way that alters the product contract;
- remove coverage because a new implementation cannot satisfy the old behavior;
- create a materially new product guarantee under a "strengthening" label.

### Requirement identity

Prefer stable requirement identity over treating source text as the contract.
Repositories may carry identity in test names, annotations, comment markers,
metadata, manifests, or scenario IDs.

Example:

    RELAY-WAKE-001
    When a supported unloaded recipient receives a Relay message,
    Pallium automatically activates the exact recipient session without human
    intervention.

Do not mandate a universal format in the first slice. Stable-ID disappearance,
duplicate, disabled, or malformed checks remain optional until Pallium
dogfooding demonstrates that generic support is worthwhile.

### Discovery, planning, and verification

At task pickup, inspect only relevant configured contracts. Identify affected
contract IDs or files, preserve their meaning in the plan, and include their
required CI surface in verification. Do not load the entire suite for every
task.

Do not assume that a new task silently supersedes an existing contract. When the
requested behavior and repository contract disagree, identify the authoritative
source or block for human resolution.

For each affected contract, planning records whether it is preserved,
coverage-only, or proposed for requirement change. A contract edit that may
alter meaning is classified before implementation:

- **equivalent**: continue; record why behavior is unchanged when non-obvious;
- **coverage-only**: continue unless it actually creates a new product decision;
- **requirement-change**: block, propose the exact change, obtain the
  repository-authorized approval, then modify the contract.

Verification traces to both current Task Context and relevant repository
contracts. Replacing a test is allowed; dropping the behavior it represented is
not.

### Approval authority

Task-local and repository-level approvals have different authority:

- A task-local requirement originating with the current user may be changed by
  that user's explicit approval.
- A repository-wide contract uses repository-defined authority, such as a
  CODEOWNER, designated product owner, or existing review checkpoint.

Configuration or existing GitHub governance identifies the repository authority.
An arbitrary human interaction with the agent must not silently authorize a
product-wide contract change.

## Checkpoint integration

Do not add another workflow stage.

- **Establish Context:** capture the immutable baseline before discovery; do not
  narrow authoritative input while translating it.
- **Discover:** inspect relevant configured contracts and resolve conflicts or
  block.
- **Assess Risk:** keep behavioral approval independent from Risk.
- **Plan and Review:** check that the plan preserves the baseline and relevant
  contracts; proposed changes block for the correct human.
- **Implement:** forbid requirement accommodation—editing Scope, Work Record,
  tests, docs, or contracts until an incomplete implementation passes.
- **Verify:** ask whether the implementation satisfies the behavior, not merely
  whether current tests pass.
- **Review the Result:** compare final Task Context to baseline; inspect every
  Behavior changes entry and protected contract edit; look for tests removed
  because behavior disappeared.

## Deterministic enforcement

Reuse the checker's trusted NUL-delimited changed-path input and existing
repository path-matching semantics. Do not add another diff or policy engine.

At PR time:

1. Detect whether configured behavioral-contract paths changed.
2. If none changed, add no contract-mutation gate.
3. If protected files changed, require a machine-readable classification.
4. If classified **requirement-change**, require the matching authorized human
   approval record.
5. Surface every affected contract file prominently in the verdict.
6. Continue relying on required CI for regression execution and pass/fail state.

Behavior-change approval predicates are non-waivable through task exceptions.
Missing or malformed changed-path evidence fails closed. Renames consider both
old and new paths. Deletion, untracked files, path normalization, Unicode,
spaces, and repository containment follow the existing checker rules.

The harness can deterministically detect:

- protected contract paths changed;
- required classification is missing or malformed;
- approval-shaped evidence is missing for a declared requirement change;
- configured contract paths attempted to use a workflow exemption;
- requirement IDs disappeared, were duplicated, or were disabled when a future
  repository adopts stable-ID checks;
- a baseline or structured change record is missing when the chosen Work Record
  representation makes that fact mechanically observable.

Reviewer judgment remains responsible for:

- semantic equivalence of rewritten prose or refactored tests;
- whether a claimed coverage-only change creates a new obligation;
- whether all relevant contracts were discovered;
- implementation correctness and contract satisfaction;
- verification adequacy;
- approval authorship or authority when no authoritative integration proves it.

Do not describe semantic preservation, human identity, or regression coverage as
mechanically enforced unless the repository provides the corresponding
deterministic control.

## Bootstrap and repository integration

During installation or reconfiguration, inspect for likely acceptance,
end-to-end, contract, regression, and scenario-fixture surfaces. Do not protect
them automatically. Present exact candidates and their existing CI coverage to
the human, who chooses the paths and repository approval authority.

Example:

    I found these likely behavioral-contract surfaces:

    - tests/relay/behavior/**
    - tests/relay/wake/fixtures/**

    The relay-behavior-contracts required check exercises the first path.
    Should Agent Workflow protect either path, and which repository role may
    approve a requirement change?

This follows the existing rule that repository governance is explicitly adopted,
not inferred by the agent.

## Pallium target usage

Pallium should create a dedicated Relay behavioral regression suite expressing
durable product behavior rather than implementation mechanisms:

    RELAY-WAKE-001
    A message to a supported unloaded recipient automatically activates the exact
    recipient without human intervention.

    RELAY-WAKE-002
    A message to a loaded idle recipient automatically starts a recipient turn.

    RELAY-WAKE-003
    A message to a busy recipient is queued as a distinct turn rather than
    injected into the active turn.

    RELAY-WAKE-004
    Wake must not change the recipient's workspace or scope.

    RELAY-DELIVERY-001
    Delivery remains pending until runtime admission is confirmed.

    RELAY-DELIVERY-002
    Wake failure does not lose the persisted delivery.

Configure that suite as a protected contract surface backed by required CI.
PR #167 would then meet two independent controls: its task-local baseline would
protect cold wake, and its repository contract would protect the inherited
behavior. The redundancy is intentional.

## Canonical replay: Pallium PR #167

The initial baseline includes automatic wake for an unloaded recipient and
preservation of its workspace. Safe cold wake then proves unavailable.

The workflow must block both attempted accommodations:

1. changing Completion criteria to delivery on the recipient's next manual
   resume;
2. narrowing Scope to exclude unloaded recipients.

The agent presents the exact requirement change, impact, and alternatives to the
appropriate human. Only explicit approval permits updating current Task Context
or protected contracts. Without approval, the correct result is **Blocked**, not
a green queue-only implementation.

## Delivery slices

1. **Workflow semantics and baseline:** update the normative SPEC first, then
   existing checkpoint guidance; define the immutable baseline, classifications,
   approval lifecycle, and optional record shape for both Work Record forms.
2. **Configuration and checker:** add **behaviorContracts.paths**, required
   verification linkage, changed-path detection, classification and non-waivable
   approval predicates, verdict output, bootstrap adoption, and packaged tests.
3. **Pallium dogfood and stable IDs:** add the Relay behavioral suite, replay
   PR #167, then decide whether generic stable-ID checks earn their complexity.

No new checkpoint, semantic-diff engine, service, or universal contract format
is required.

## Acceptance coverage

1. Baseline captures Outcome, Scope, Constraints, and Completion criteria after
   Establish Context and before discovery/planning.
2. Later approved changes update current Task Context without rewriting baseline.
3. An infeasible or unsafe requirement moves State to **Blocked**; it cannot be
   silently accommodated by implementation, tests, docs, or Work Record edits.
4. Clean-context agent review cannot authorize a requirement change.
5. Equivalent wording and coverage-only test changes proceed without human
   approval but carry the required classification when protected files change.
6. Completion-criteria weakening and Scope narrowing both block until authorized.
7. Compact tasks remain compact when no requirement changes and can record an
   exceptional behavior change without migrating solely for ceremony.
8. A repository can configure one or more behavioral-contract paths plus an
   existing required verification surface.
9. Relevant tasks inspect and reference affected contracts during discovery,
   planning, and verification without loading the complete suite.
10. Protected contract edits are prominent in the verdict and cannot use the
    documentation-only exemption.
11. A declared repository requirement change requires repository-authorized
    approval; task-local user approval cannot silently substitute for it.
12. Required CI exercises the configured contract suite; mutation protection is
    not described as regression enforcement on its own.
13. Equivalent test refactoring does not require approval merely because a
    protected file changed.
14. The checker makes no semantic-equivalence, approval-authorship, or
    implementation-correctness claim.
15. Missing, malformed, renamed, deleted, Unicode, spaced, and outside-repository
    path inputs follow existing fail-closed safety rules.
16. At least two repository layouts and contract locations are covered.
17. The Pallium PR #167 replay blocks both documented erosion paths and cannot
    legitimately reach queue-only behavior without explicit approval.
18. Pallium can protect its Relay suite without making Agent Workflow the product
    specification owner.

## Out of scope

- Turning the Work Record into a complete product specification.
- Making every regression test immutable or authoritative.
- Making Agent Workflow own repository product requirements.
- Generic semantic comparison of prose or arbitrary tests.
- Automatic discovery of every behavior affected by a code change.
- Forbidding intentional product changes after authorized approval.
- Human approval for ordinary implementation or equivalent test refactoring.
- Replacing code review, external requirements, product authority, or CI.
- Requiring every repository to adopt behavioral contracts.
- A universal stable-ID format before dogfooding demonstrates the need.

## Done When

Task-local requirements are durably baselined before discovery, material changes
cannot legitimately advance without the appropriate human decision, configured
repository contracts receive mutation protection plus required-CI regression
coverage, PR #167's two erosion paths are blocked, and the packaged workflow and
checker tests pass without adding routine ceremony.
