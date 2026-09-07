# Decisions

ADR-style log of substantive design decisions for agent-workflow.

Newest entries on top. Each entry: date, decision, alternatives considered, rationale.

Routine session work doesn't go here — only decisions a future maintainer would want the reasoning behind.

---

## 2026-09-07 — Documentation-only applicability is deny-overrides

**Decision:** Repositories may explicitly approve discovered documentation, roadmap, and root README paths to skip agent-workflow. Any mixed, risky, protected, invalid, or uncertain input makes the complete change use the normal workflow. Direct-default-branch permission is a separate, lowest-priority opt-in and is effective only with a fresh unprotected-branch result.

**Alternatives considered:** A global missing-Work-Record opt-out; hardcoded `roadmap/` and `docs/` paths; ordered allow rules; treating bootstrap's protection observation as durable; using prose or model classification.

**Rationale:** Pallium repeatedly needed a manual roadmap exception, while installed workflow guidance contradicted it. Repository layouts differ, documentation can include governance contracts, and branch protection changes over time. Bootstrap discovery plus human approval makes the standing preference durable; deterministic all-path evaluation, Redline/protected-surface precedence, and fresh protection checks keep the exception narrow.
