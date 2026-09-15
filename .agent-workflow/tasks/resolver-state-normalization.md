<!-- agent-workflow:start -->
**Outcome:** Work Record validation and resolution accept and normalize the same allowed State spellings, including repeated terminal periods.

**Target:** agent-workflow

**Scope:** Align state normalization in `core/checker/checker.py` with the existing predicate, add focused resolver regression coverage, and regenerate the tracked vendored checker mirrors and manifests.

**Constraints:** Preserve allowed state names, resolver JSON shape/reason codes, read-only behavior, parser behavior, and all unrelated workflow semantics. No private Pallium vendor patch.

**Completion criteria:** Given a parsed State value ending in one or more periods and optional surrounding whitespace, checker validation and `--resolve-work-record` both accept it and return the canonical allowed state; invalid states remain rejected; focused and full repository tests pass.

**Risk:** Elevated

**Complexity:** Simple

**Reason:** `core/checker/checker.py` is gray and watched; resolver tests are blue and generated mirrors are watched. No contract checkpoint, boundary, API, schema, security, persistence, or runtime-config surface is touched.

**Discovery:** At `c355df09`, `workrecord_state_valid` uses `state.rstrip(".").strip()` while `_resolve_work_record` strips whitespace and at most one final period. The existing regression covers exactly one period, so `Ready for review..` validates but resolution returns `invalid_record_state`. Packaging regenerates the checker under `.claude/skills/agent-workflow/` and `dist/agent-workflow/` plus each package manifest from checker source.

**Material assumptions:** Repeated terminal periods are intentionally accepted because the validator already defines that behavior and the consumer report requires resolver parity. If normative specification or existing tests require exactly zero/one period, return to planning instead of widening behavior elsewhere.

**Plan:** Replace the resolver's one-period branch with the validator's existing terminal-period normalization, expand focused regression coverage for resolver and validator parity across repeated periods plus surrounding whitespace, run focused checker tests, regenerate tracked checker mirrors through the repository scripts, run Redline/checker and `tests/run-all.sh`, then obtain smart result review. Stop if the change affects parser semantics, allowed states, output shape, or files outside the recorded scope.

**Verification plan:** Repeated-period valid state resolves canonically and invalid state still fails → focused resolver tests; generated consumers match source → package/committed-skill checks; no workflow regression → full repository suite and final Redline/checker; exact diff is minimal → smart clean-context result review.

**Plan review:** Approved by clean-context reviewer `/root/resolver_normalization_plan_review`; verification expanded to assert repeated-period and surrounding-whitespace parity in both validation and resolution.

**Approvals:** Not required at this risk level.

**Exceptions:** —

**State:** Ready to implement
<!-- agent-workflow:end -->

## Implementation

- Applicability evaluated first: checker source and generated harness files are outside the approved documentation-only set, so the normal workflow applies.
- Clean-context Redline review classified the full intended scope GRAY / Elevated, Simple, with no required checkpoint.
- Reproduced `Ready for review..` resolving as `invalid_record_state` at base `c355df09`, then aligned the resolver with the validator's existing one-line normalization and expanded parity coverage; 5 focused resolver/invalid-state cases pass.
- Repository packaging/install scripts regenerated both tracked checker copies and their deterministic size manifests. Clean-context follow-up confirmed the manifest files are a non-material scope clarification with unchanged risk and no plan-review repeat.
- Focused package verification passed: distribution/source parity, committed dogfood parity, internal references, install probe, and bootstrap simulation.

## Plan review

Clean-context reviewer /root/resolver_normalization_plan_review approved the one-line resolver alignment as the smallest root-cause fix. It required focused coverage of repeated terminal periods plus surrounding whitespace and validator/resolver parity; no SPEC change is needed.

Follow-up review confirmed the generated package manifests are deterministic metadata within the approved approach; classification and plan remain unchanged.
