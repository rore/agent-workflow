# Decisions

ADR-style log of substantive design decisions for agent-workflow.

Newest entries on top. Each entry: date, decision, alternatives considered, rationale.

Routine session work doesn't go here — only decisions a future maintainer would want the reasoning behind.

---

## 2026-09-10 — Supported runtimes share one pre-mutation decision

**Decision:** Claude Code, Codex, and stable OpenCode 1.x use native discovery
and thin adapters around one checker-backed decision for supported structured
file mutations. The decision uses the complete known change set, permits
Work-Record-only recovery, and otherwise requires either implementation-ready
workflow evidence or the existing whole-change exemption. Default-branch work
requires the exemption independently. Adapter faults are reported as degraded
and fail open; arbitrary shell mutation remains an explicit non-claim.

**Alternatives considered:** Copy Claude's plan-text hook to every runtime;
maintain separate runtime policy engines; parse arbitrary shell commands; claim
OpenCode 2 support while it remains beta.

**Rationale:** Observable parity matters more than identical hook names. One
decision prevents policy drift, while native adapters preserve each platform's
loader, trust, and denial behavior. Shell parsing and beta compatibility add
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
