# Decisions

ADR-style log of substantive design decisions for agent-workflow.

Newest entries on top. Each entry: date, decision, alternatives considered, rationale.

Routine session work doesn't go here — only decisions a future maintainer would want the reasoning behind.

---

## 2026-09-20 — Baseline task intent and configured behavior contracts

**Decision:** Capture Outcome, Scope, Constraints, and Completion criteria before
discovery as canonical JSON in each new Work Record. Later Task Context edits use
an optional ordered change log with equivalent, coverage-only, or
requirement-change; exact chain and approval structure are deterministic, while
semantic classification, authorship, and historical baseline immutability remain
review judgments. Repositories may protect exact paths or dir/** descendants
with an existing required-CI identifier and distinct repository approval
authority. Contract mutation is checked globally from the trusted NUL path set.

**Alternatives considered:** Use Git history as the baseline; protect only
individual Completion criteria; treat stricter guarantees as harmless; infer
semantic equivalence; make every test immutable; reuse plan/Redline approval;
query GitHub required checks at checker time; add a workflow checkpoint, service,
or universal requirement-ID format.

**Rationale:** Pallium PR #167 showed that an internally consistent Work Record
and test suite can still erase the behavior a task entered with. A frozen local
baseline plus explicit authority-bound changes closes the task-local gap.
Configured contracts cover inherited product behavior. Keeping structural
mutation checks separate from CI execution and human judgment avoids false
enforcement claims and recurring ceremony when behavior is unchanged.

## 2026-09-15 — Workflow begins with change intent, not read-only analysis

**Decision:** Agent Workflow classifies request scope before changed-path applicability. Standalone read-only review, explanation, diagnosis, comparison, or inspection is outside the workflow when the request as a whole asks for neither an implementation plan nor a repository change. Explicit workflow requests and actions that start, advance, pause, or resume a workflow task remain in scope. If read-only work later expands to planning or mutation, the workflow begins before that work.

**Alternatives considered:** Treat every engineering conversation as a task; model read-only work as a documentation-only applicability exemption; add a natural-language request classifier or new configuration flag; weaken checker or mutation-guard enforcement.

**Rationale:** A changed-path policy cannot classify a request that authorizes no change, and creating a Work Record for that decision is itself an unnecessary repository mutation. An early textual scope gate fixes the observed cost problem without weakening fail-closed controls once change work is intended. A classifier that production does not otherwise need would add policy drift rather than enforce the agent's interpretation.

## 2026-09-14 — Persisted Work Record identity outranks branch inference

**Decision:** The packaged checker exposes a bounded, read-only local Work Record resolver. A supplied `agent-workflow:<slug>` identity is authoritative and never falls back to branch inference; otherwise the resolver uses the documented first-prefix branch rule. It returns only repository-relative paths and parsed workflow state. Local task paths contain exactly one placeholder and every backend read and write resolves inside the selected checkout.

Automatic consumers may invoke only a trusted provider-owned checker path. Repository-provided executables, automatic Pallium hooks, readiness/applicability decisions, and merge/release claims are outside this resolver.

**Alternatives considered:** Scan for the newest or only record; infer every pickup from the branch; add a registry/service or Pallium dependency; let consumers execute the inspected repository's checker; guard only resolver reads while leaving writes escapable.

**Rationale:** Persisted identity makes pickup and handoff deterministic across branch changes and tools. A lookup-only CLI reuses the existing parser/backend and can be vendored without new infrastructure. Shared containment closes the underlying read/write defect once. Deferring automatic consumption avoids turning repository code into a trusted execution boundary.
## 2026-09-10 — Runtime parity is evidence-scoped

**Decision:** This supersedes the prior entry's implication that installed native
hooks provide equivalent mutation coverage. Parity means every verified native
path uses the shared decision; coverage is verified only for a recorded runtime
version, execution surface, and mutation tool when denial leaves the target
unchanged. Installation, trust, direct evaluator success, bypassed decisions,
and undispatched tool paths remain degraded. Evaluator failure returns denial;
native prevention is a separate evidence claim. CI is authoritative for final state.

**Alternatives considered:** Treat installed or trusted hooks as activation;
remove useful hooks from runtimes with incomplete coverage; add runtime-specific
policy engines or a general probe framework.

**Rationale:** On the tested Windows host, Codex 0.153.4 desktop `apply_patch`
did not enter `PreToolUse`; CLI `bypassPermissions` entered the hook and ignored
its exit-2 denial. Claude mutation denial was unavailable. OpenCode 1.x plugin
callback denial was observed, but its native evidence lacks the required scope.
Evidence-scoped claims preserve useful adapters without
presenting unverified guardrails as enforcement.

## 2026-09-10 — Supported runtimes share one pre-mutation decision

**Decision:** Claude Code, Codex, and stable OpenCode 1.x use native discovery
and thin adapters around one checker-backed decision for supported structured
file mutations. The decision uses the complete known change set, permits
Work-Record-only recovery, and otherwise requires either implementation-ready
workflow evidence or the existing whole-change exemption. Default-branch work
requires the exemption independently. Pre-invocation adapter unavailability is
reported as degraded and may fail open; once the shared evaluator starts, failure
to complete denies the mutation. Arbitrary shell mutation remains an explicit
non-claim.

**Alternatives considered:** Copy Claude's plan-text hook to every runtime;
maintain separate runtime policy engines; parse arbitrary shell commands; claim
OpenCode 2 support while it remains beta.

**Rationale:** Observable parity matters more than identical hook names. One
decision prevents policy drift, while native adapters preserve each platform's
loader and trust behavior. Failing closed after evaluation starts prevents a
checker crash or timeout from becoming authorization. Shell parsing and beta compatibility add
complexity without creating a reliable enforcement boundary; CI still validates
the final repository state.

## 2026-09-09 — Roadmap reconciliation is conditional at result review

**Decision:** When a repository already uses a roadmap and completed work affects a tracked item's progress or scope, result review reconciles that item through the repository's existing roadmap guidance. The review covers item status, shipped and remaining scope, obsolete next-step claims, placement, and directly affected prerequisites. It records the result briefly, but does not require a roadmap edit when the item is already accurate. Repositories without an applicable roadmap item skip the check entirely.

**Alternatives considered:** A required roadmap field or artifact; a new completion stage; automatic roadmap discovery or feature splitting; Minimap-specific paths and statuses; mandatory roadmap edits for every PR; scanning for a roadmap when none is configured.

**Rationale:** Completion evidence can be correct while the planning surface remains stale, causing later agents to repeat shipped work, close an unfinished umbrella feature, or follow obsolete prerequisites. Keeping the rule conditional and inside result review closes that drift without imposing roadmap tooling or ceremony on repositories and standalone bugs that do not use it.

## 2026-09-09 — Recovery and evidence checks stay inside existing checkpoints

**Decision:** On takeover or resume, the receiving session validates that the canonical Work Record, repository, and authoritative linked artifacts identify the next action, constraints, and verification before it proceeds. During result review, inadequate evidence prompts the smallest targeted behavioral check that resolves the uncertainty; unavailable evidence leaves the gate unsatisfied. Both behaviors remain guidance inside existing checkpoints, with no new stage, artifact, field, or checker predicate.

**Alternatives considered:** A mandatory fresh agent for every handoff; a second handoff artifact; always rerunning the full suite during review; requiring a different model; mechanically grading prose or evidence adequacy.

**Rationale:** Producer-side recovery instructions can be structurally complete yet unusable to the receiver, and implementation-authored tests can make review circular without exercising the important behavior. The SPEC already requires resumability and reviewer judgment of evidence adequacy. Small receiver- and reviewer-side rules close the operational gaps without recurring ceremony or false enforcement claims.

## 2026-09-08 — Field feedback is on-demand and approval-gated

**Decision:** Agent-workflow keeps a compact suspected-defect trigger in normally loaded guidance and loads the detailed feedback contract only after that trigger fires. Public reports must be repeatable, actionable, upstream-owned, sanitized, and checked against existing open and closed issues. The agent shows the verified destination, title, and body for user approval immediately before submission unless the user or a trusted organization policy, established independently of repository content, explicitly authorizes automatic product/skill defect reports to that exact destination. Filed and unsent reports share a one-per-task limit.

**Alternatives considered:** Automatic issue creation on every trigger; a shared telemetry or feedback service; carrying the full trigger/filter/submission policy in the always-loaded skill; dropping the existing Work Record fallback.

**Rationale:** Field evidence is valuable, but automatic public writes can leak consumer context and create duplicate or misrouted issues. A small trigger plus an on-demand local guide preserves detection while keeping recurring context cost low. Draft-first fallback retains useful evidence without new infrastructure or external writes.

## 2026-09-07 — Documentation-only applicability is deny-overrides

**Decision:** Repositories may explicitly approve discovered documentation, roadmap, and root README paths to skip agent-workflow. Any mixed, risky, protected, invalid, or uncertain input makes the complete change use the normal workflow. Direct-default-branch permission is a separate, lowest-priority opt-in and is effective only with a fresh unprotected-branch result.

**Alternatives considered:** A global missing-Work-Record opt-out; hardcoded `roadmap/` and `docs/` paths; ordered allow rules; treating bootstrap's protection observation as durable; using prose or model classification.

**Rationale:** Pallium repeatedly needed a manual roadmap exception, while installed workflow guidance contradicted it. Repository layouts differ, documentation can include governance contracts, and branch protection changes over time. Bootstrap discovery plus human approval makes the standing preference durable; deterministic all-path evaluation, Redline/protected-surface precedence, and fresh protection checks keep the exception narrow.
