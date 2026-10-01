# Node bootstrap profile

Source: manager assignment `relay-msg-7ebb00749f5a452e9d57c1ec185a6785`, based on direct user item `01a0f657-6753-7ca2-881c-a142a776b55c`: "if we look at minimap (or similar node projects), can we establish a small profile that can help with bootstrap?"

<!-- agent-workflow:start -->
**Outcome:** Node/JS/TS repositories have a small reusable bootstrap profile that proposes risk policy from their actual layout.
**Target:** agent-workflow
**Scope:** Existing Redline extension mechanism, bootstrap routing and guidance, supporting documentation, verification, and generated skill packages.
**Constraints:** Preserve repository-specific human policy approval, shared workflow gates, Python/JVM routing, and no-package fallback. No new analysis dependency, generalized exclusions, automatic JS/UI safety, fabricated boundaries, consumer edits, or changes to the root checkout.
**Completion criteria:** A Minimap-like nested layout and a distinct Node/TS layout produce layout-specific bootstrap candidates using the shipped profile; boundary capability is accurately not configured; no-package and Python/JVM routing remain valid; sensitive source and mirrors are not silently excluded; packaging, independent review, and required tests pass before merge.
**Requirement baseline:**
{"source":"relay-msg-7ebb00749f5a452e9d57c1ec185a6785","outcome":"Node/JS/TS repositories have a small reusable bootstrap profile that proposes risk policy from their actual layout.","scope":"Existing Redline extension mechanism, bootstrap routing and guidance, supporting documentation, verification, and generated skill packages.","constraints":"Preserve repository-specific human policy approval, shared workflow gates, Python/JVM routing, and no-package fallback. No new analysis dependency, generalized exclusions, automatic JS/UI safety, fabricated boundaries, consumer edits, or changes to the root checkout.","completion_criteria":"A Minimap-like nested layout and a distinct Node/TS layout produce layout-specific bootstrap candidates using the shipped profile; boundary capability is accurately not configured; no-package and Python/JVM routing remain valid; sensitive source and mirrors are not silently excluded; packaging, independent review, and required tests pass before merge."}
**Risk:** Elevated
**Complexity:** Moderate
**Reason:** Extension and bootstrap instruction paths are gray/watch under the effective policy; tests and ordinary docs are blue. Several shipped bootstrap surfaces and layout-dependent behavior require independent technical review. No red contract/schema/CI/policy edits are intended.
**Discovery:** Routing is agent guidance, not a runtime detector. Redline bootstrap Phase 1 currently selects Python/JVM or generic zone-only; Phase 2 already requires actual-path evidence and human approval. Packaging enumerates extension folders without a new build mechanism. Existing zone-only thresholds are 30/80 files and 800/1500 lines. Node can reuse the policy schema/reporter with adapter none; no operating-mode override is needed. Existing tests do not exercise Node proposal adaptation. Manager supplied inspected Minimap layout/script/mirror evidence; second layout will be a clearly labeled representative TypeScript workspace fixture.
**Material assumptions:** The existing extension mechanism can support a zone-only Node profile without normative/schema changes. Contrary evidence returns this task to planning and the manager for any required human gate.
**Plan:** Add only extensions/node/{profile.md,scaffold.md,adapter.yaml,suppressions.yaml}. Profile discovers tracked package manifests (including nested/workspace), scripts, exports/bin/main and TypeScript/test configuration, actual source/test/config/lock paths and generated mirror parity. Propose narrow evidence-backed red/blue/watch entries under existing Phase 2/3 approval, never blanket JS/UI blue or generated/lock exclusions. Zone-only boundaries remain not configured; no boundary tool or dependency. Route positive package.json evidence to node, ambiguous mixed builds to human choice, no package to existing fallback; only add node to workflow finding enum. Register small new-file budgets, integrate focused schema/reporter checks into existing redline layer, and update docs/REDLINE.md, docs/PACKAGING.md and decision rationale. No SPEC/schema/active-policy/CI changes. Stop for material scope expansion, contract changes, or unsupported backend assumptions. Then package/install, full suite, independent result review, PR/CI and review-thread closure before merge.
**Verification plan:** Two layouts: independent blind bootstrap exercise reads shipped instructions with Minimap-like nested fixture and distinct TypeScript workspace fixture; reports exact candidates, test commands, human approval boundary and mirror obligations, without consumer writes. Runnable schema/reporter checks validate adapted policy proposals for both layouts, red sensitive-source/governance paths, blue narrow tests, gray unknown code, watch manifests/locks/mirrors, adapter none, and suppression detection on source. No-package and Python/JVM routing preservation: blind exercise scenarios plus unchanged existing suites. Package/link/budget validation proves extension ships and references resolve; tests/run-all.sh runs before push. Native agent exercise is instruction evidence, not proof of an automatic detector or a boundary backend. Independent result review compares baseline and real failure paths.
**Plan review:** Agent technical review: /root/node_profile_review, approved at f0311496ed783e3fbcb14af04872a1f307c4ee26; see independent Plan review below. Verification refinements include ambiguous mixed builds and protected contract tests beneath test trees, with narrow suppression exemptions.
**Approvals:** Not required at Elevated; additional High-risk or expanded scope gates go through the manager.
**Exceptions:** —
**State:** Ready to implement
<!-- agent-workflow:end -->

## Implementation

- Baseline established on `feat/node-bootstrap-profile` at current main `b94cb5017923f3d7fa3090a315058d3b6f3bcad2`, in the reused clean isolated checkout. Discovery and implementation have not begun. Blocked only on normal discovery/planning/review gates.
- Discovery: existing profile/scaffold/adapter/suppression shape and automatic extension packaging suffice. No new parser, policy schema, framework taxonomy, or boundary service is needed. Proposed plan awaits independent technical review.
- Plan approved. Exact intended edits: `core/agent-redline/extensions/node/{profile.md,scaffold.md,adapter.yaml,suppressions.yaml}`, both bootstrap mode files, `tests/budget/budget.yaml`, `tests/redline/{run.sh,check-node-profile.py}`, `tests/package/check-install-probe.sh`, `docs/{REDLINE.md,PACKAGING.md,DECISIONS.md}`, and generated `dist/agent-workflow/` plus native mirrors. No edits to test-only detection logic. Existing Python/JVM regression simulator runs unchanged. Implementation and tests delegated together within these paths; main retains synthesis and reviews.

## Plan review

Independent clean-context non-implementer `/root/node_profile_review` approved the plan at `f0311496ed783e3fbcb14af04872a1f307c4ee26`; reviewed record blob `a76e3af4ed4839c33b93a9eeb3b84662b7ee22c8`, SHA256 `203AF6D1DFDB53E447DEC6C2BECD6885B7C44A9397406D0AE37EC5BD91C1A4F0`. No blocking findings. Inspected SPEC risk/plan/result requirements, both bootstrap sources, Python/zone-only defaults, real reporter/suppressions/adapter behavior, packaging and budget/reference checks. Approved the existing four-file zone-only mechanism with no new detector/dependency/schema/SPEC/backend. Coverage refinements: ambiguous mixed builds defer selection to the developer; suppression checks must include protected contracts under test trees and avoid broad inherited test exemptions. No implementation or tests were performed by this reviewer.

## Evidence

- Initial classification: core extension/bootstrap and generated skill surfaces are gray/watch; no configured red paths intended. Whole-change documentation exemption does not apply.

## Result review

Pending.
