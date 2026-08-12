# Default Implementation Profile

Profile-specific mapping of the workflow and harness contract (`SPEC.md`) to GitHub, CI, repository guidance, and Agent Redline.

**Normative for default profile implementations; not part of the portable core specification.**

## 1. System Mapping

- **Canonical Work Record:** Local Markdown file in the consuming repo's `.agent-workflow/tasks/` directory. This is the canonical Work Record store for the default profile; bootstrap installs it without asking. The local backend is not a stopgap — it is the intended source of truth.
- **Workflow guidance and readiness validation:** shared `/agent-workflow` skill
- **Repository guidance:** `AGENTS.md` or existing repository documentation
- **Implementation diff and review discussion:** GitHub pull request
- **Risk and policy findings:** Agent Redline (bundled and non-optional; installed by bootstrap as part of the agent-workflow install, not as a separate step)
- **Verification:** repository commands and GitHub CI
- **Approval and merge enforcement:** GitHub required reviewers, required checks, and branch protection
- **Exceptions:** recorded in the Work Record's structured block (the marker-bounded Markdown section), approved under team policy
- **External post-merge follow-up:** separate linked issue or task accepted by its delivery or operational owner

### Repository Delivery Guidance

Repositories **MAY** define local artifacts such as PRDs, architecture documents, ADRs, and delivery decompositions.

These artifacts are impact-triggered outputs of the shared workflow, not mandatory phases for every task.

The local Markdown backend is the canonical Work Record store. A `jira` backend value is reserved in the schema as an optional future integration; it is not implemented, and there is no requirement to adopt it — the local backend stands on its own.

Where a repository also uses an external issue tracker, repository-local backlogs **SHOULD NOT** duplicate its identifiers, ownership, or status unless they are generated from or synchronized with it.

## 2. Default Workflow Paths

The default profile defines no degraded-mode bypass. When a required authoritative system, approval, policy evaluation, or verification check is unavailable, the affected gate remains unsatisfied unless an authorized and documented fallback is approved.

### Routine Path

The Work Record backend (currently the local Markdown file under `.agent-workflow/tasks/<slug>.md`; see [§1 System Mapping](#1-system-mapping)) contains the compact Work Record.

The `/agent-workflow` skill confirms:

- outcome, target, and scope are present
- risk is Routine
- approach and verification are stated
- no blocking finding exists

GitHub and CI remain authoritative for implementation, verification, review, and merge.

### Expanded Path

The Work Record backend (currently local) is the canonical index and contains or links:

- Task Context (outcome, target, scope, constraints, completion criteria — SHOULD use EARS form: *When `<trigger>`, the `<system>` shall `<observable outcome>`*)
- material Discovery Summary
- risk and complexity decision
- plan and Verification Plan
- assumptions and invalidation conditions
- required reviews and approvals
- pull request
- CI evidence
- review outcome
- exceptions or external follow-up

## 3. Default Minimum Risk Triggers

The following are **at least Elevated**:

- authentication or authorization changes
- tenant-isolation changes
- public APIs, inter-service contracts, or event and message schemas
- database migrations
- financial or ledger behavior
- behavioral or compatibility changes to shared libraries or platform components used by multiple services
- infrastructure or deployment configuration affecting production resources, networking, routing, resource allocation, or service topology
- third-party integration contracts, authentication, or request and response construction
- changes to CI, architecture rules, risk policy, or verification controls

The following are **High** unless prohibited:

- destructive or difficult-to-reverse database, infrastructure, or deployment changes
- intentional public compatibility breaks
- material cross-tenant risk
- material financial-integrity risk
- broad changes to production-critical behavior

The following are **Boundary Violations** when unauthorized:

- weakening or bypassing required CI checks
- weakening protected architecture or policy rules
- introducing secrets
- implementing an unapproved destructive or compatibility-breaking change

Repositories **MAY** add stronger triggers and identify repository-specific sensitive surfaces.

**Definition of Done.** Existing project Definition of Done requirements apply through this workflow. Applicable requirements are represented as task completion criteria, verification requirements, approvals, or group and repository rules. The Work Record links to their authoritative evidence and does not duplicate the Definition of Done.

### Elevated review controls

The portable spec (`SPEC.md` §9.4) treats clean-context plan review as **SHOULD** for Elevated tasks. Within the default profile this is tightened to **required presence**: an Elevated Work Record **MUST** record a clean-context plan review reference before implementation begins, and the harness CI checker enforces presence.

This is presence, not quality — consistent with the Judgment Boundary in `SPEC.md` §5. Whether the clean-context review was thorough remains a reviewer judgment; whether it happened at all is enforced.

## 4. Default Routine Work Record Example

```text
Outcome:
Fix retry handling in WalletService.

Target:
wallet-service.

Scope:
Retry path and its tests. No public API or schema changes.

Constraints:
Public API and tenant isolation unchanged.

Completion criteria:
A retry under transient failure produces one wallet, not multiple.

Risk and complexity:
Routine / Simple.
No sensitive path or blocking finding detected.

Approach:
Reuse the existing retry utility and add a regression test.

Verification:
WalletRetryTest plus required wallet-service CI.

State:
Ready to implement.
```

## 5. Default Expanded Work Record Example

```text
Outcome:
Repeated or concurrent wallet-creation retries create one wallet.

Target:
wallet-service.

Scope:
Wallet creation flow, persistence, and related tests.

Constraints:
No public API change.
Tenant isolation remains unchanged.

Completion criteria:
When concurrent retry requests arrive, the system shall create exactly one wallet (verified by concurrency test).
When a single wallet-creation request is made, the system shall create one wallet with no regression.

Risk:
Elevated.
Triggered surfaces: persistence semantics, concurrency, tenant isolation.

Complexity:
Moderate.

Discovery:
No persisted idempotency key exists.
Concurrent retry coverage is missing.
Existing request identifier may be reusable.

Material assumption:
The request identifier is stable across retries.

Disproving evidence:
Retry requests receive different identifiers.

Action if disproved:
Stop implementation and return to planning.

Plan:
Persist a tenant-scoped idempotency key.
Enforce uniqueness by tenant and request identifier.
Return the existing wallet for retries.

Verification:
- Concurrent retries: concurrency integration test
- Tenant isolation: cross-tenant authorization test
- API compatibility: API compatibility check
- Persistence guarantee: constraint inspection and test

Plan review:
Clean-context agent review <link>

Approvals:
None required

Implementation:
PR <link>

Evidence:
CI <link>

Result review:
Separate reviewer <link>

State:
Ready for review.
```

## 6. Pilot Calibration

**Non-normative.** The default profile risk triggers, gates, and review controls are starting hypotheses, not permanent rules. During the pilot — and on an ongoing basis as the workflow becomes load-bearing — evaluate whether each rule earns its overhead.

The point is not to stand up a dashboard before the pilot. It is to make explicit that overhead without yield is grounds for relaxing a rule, and that misses despite the rule are grounds for strengthening it. Bureaucracy that catches nothing useful is the failure mode the calibration loop exists to prevent.

### Signals observable from Work Records alone (cheap)

These need no additional instrumentation; the Work Records already carry them:

- **Risk-classification overrides** — agent declared a different Risk than the structural minimum redline detected, in either direction.
- **Shape mismatches caught by the checker** — task declared `(Routine, Simple)` but used the expanded shape, or vice versa.
- **Blocking findings by predicate** — which CI predicates fire most often, and on which kinds of tasks.
- **Re-planning rate** — Work Records that moved from `Ready to implement` back to `Blocked or returned to planning` after material change.
- **Stale or incomplete records at merge** — required fields empty when the PR was approved.

### Signals requiring linkage (defer instrumentation)

These are useful but cost more — they require linking Work Records to downstream signals not yet collected in a uniform way:

- repeated reviewer corrections on the same kind of issue across tasks
- verification gaps surfaced post-merge
- defects discovered after review whose root cause is something the workflow could have caught

Start the pilot on the cheap signals and add downstream linkage only when the cheap signals leave a real question unanswered.

### When a rule gets revised

A risk trigger or review control is a candidate for revision when one of these is observable across a representative sample of tasks (≥10 for the pilot, more once volume permits):

- The rule classifies tasks as Expanded but the additional controls produce no blocking findings on those tasks. → Candidate for relaxation.
- Reviewers consistently raise the same issue that the existing controls did not catch. → Candidate for strengthening or moving up to a checker predicate.
- The rule's classification is overridden by the agent or developer more often than it stands. → The rule is mis-targeted; rewrite the trigger.

Revisions land as normal slices against this repo. The change is the rule, not the workflow's posture.
