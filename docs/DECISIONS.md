# Decisions

ADR-style log of substantive design decisions for agent-workflow.

Newest entries on top. Each entry: date, decision, alternatives considered, rationale.

Routine session work doesn't go here — only decisions a future maintainer would want the reasoning behind.

---

## 2026-09-08 — Field feedback is on-demand and approval-gated

**Decision:** Agent-workflow keeps a compact suspected-defect trigger in normally loaded guidance and loads the detailed feedback contract only after that trigger fires. Public reports must be repeatable, actionable, upstream-owned, sanitized, and not duplicates. The agent shows the verified destination, title, and body for user approval immediately before submission unless a standing instruction explicitly authorizes automatic product/skill defect reports to that exact destination. Filed and unsent reports share a one-per-task limit.

**Alternatives considered:** Automatic issue creation on every trigger; a shared telemetry or feedback service; carrying the full trigger/filter/submission policy in the always-loaded skill; dropping the existing Work Record fallback.

**Rationale:** Field evidence is valuable, but automatic public writes can leak consumer context and create duplicate or misrouted issues. A small trigger plus an on-demand local guide preserves detection while keeping recurring context cost low. Draft-first fallback retains useful evidence without new infrastructure or external writes.

## 2026-09-07 — Documentation-only applicability is deny-overrides

**Decision:** Repositories may explicitly approve discovered documentation, roadmap, and root README paths to skip agent-workflow. Any mixed, risky, protected, invalid, or uncertain input makes the complete change use the normal workflow. Direct-default-branch permission is a separate, lowest-priority opt-in and is effective only with a fresh unprotected-branch result.

**Alternatives considered:** A global missing-Work-Record opt-out; hardcoded `roadmap/` and `docs/` paths; ordered allow rules; treating bootstrap's protection observation as durable; using prose or model classification.

**Rationale:** Pallium repeatedly needed a manual roadmap exception, while installed workflow guidance contradicted it. Repository layouts differ, documentation can include governance contracts, and branch protection changes over time. Bootstrap discovery plus human approval makes the standing preference durable; deterministic all-path evaluation, Redline/protected-surface precedence, and fresh protection checks keep the exception narrow.
