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
**Discovery:** Pending; baseline established before repository discovery.
**Material assumptions:** The existing extension mechanism can support a zone-only Node profile without normative/schema changes. Contrary evidence returns this task to planning and the manager for any required human gate.
**Plan:** Pending discovery and independent plan review; do not implement yet.
**Verification plan:** Pending mapping from completion criteria to focused checks.
**Plan review:** Pending clean-context technical review.
**Approvals:** Not required at Elevated; additional High-risk or expanded scope gates go through the manager.
**Exceptions:** —
**State:** Blocked
<!-- agent-workflow:end -->

## Implementation

- Baseline established on `feat/node-bootstrap-profile` at current main `b94cb5017923f3d7fa3090a315058d3b6f3bcad2`, in the reused clean isolated checkout. Discovery and implementation have not begun. Blocked only on normal discovery/planning/review gates.

## Evidence

- Initial classification: core extension/bootstrap and generated skill surfaces are gray/watch; no configured red paths intended. Whole-change documentation exemption does not apply.

## Result review

Pending.
