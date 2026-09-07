<!-- agent-workflow:start -->
**Outcome:** Repositories can exempt explicitly approved documentation-only changes from agent-workflow, while direct-default-branch work is allowed only when every changed path qualifies, risk is low, the user approved it, and live branch protection is absent.

**Target:** agent-workflow

**Scope:** Normative applicability contract; config/schema and shared evaluator; checker/CI integration; bootstrap discovery and approval; operating guidance and hooks; packaged distribution; focused unit and caller-surface E2E coverage; this repository's documentation-only dogfood configuration.

**Constraints:** Deny overrides allow; any mixed, risky, protected, invalid, or uncertain input returns to the normal workflow. Direct-main is documentation/roadmap-only, never bypasses protection, and is lowest priority. No new dependency or policy engine. Preserve existing behavior when no applicability config exists.

**Completion criteria:**
- Bootstrap discovers repository-specific documentation, roadmap, and root README candidates, verifies default-branch protection, and writes only explicitly approved settings.
- One deterministic decision is shared by agent guidance, local checking, and CI; all-path AND semantics and protected/risk precedence are visible in output.
- Documentation-only PRs can pass without a Work Record; mixed/risky/protected changes still require one and independent Redline/CI checks remain active.
- Direct-default-branch eligibility requires approved paths plus a live unprotected result; protected or unavailable status denies it.
- Packaged consumer E2E covers bootstrap, local, CI, rename/dirty-path, fail-closed, and two-layout journeys; the full repository suite passes.

**Risk:** High

**Complexity:** Moderate

**Reason:** The change edits the normative workflow contract, schema, governance configuration, CI behavior, and agent instructions. These are red-zone contract surfaces; multiple runtimes and packaged consumers must agree.

**Discovery:** Current guidance is unconditional: operating mode stops on main and seed/OpenCode reminders require a Work Record for every task. The checker has only a global PR-time requiredForBranchChanges opt-out. Pallium carries a conflicting manual roadmap exception. agent-workflow main is protected; Pallium main is currently unprotected. Existing config, hooks, reporter, checker, bootstrap phases, packaging, and E2E seams can host the feature without a second policy engine.

**Material assumptions:**
- Applicability remains path-deterministic; bootstrap may discover candidates conversationally, but stored policy and enforcement do not use semantic/LLM classification. If deterministic path/risk inputs cannot be produced, deny exemption.
- GitHub classic protection plus applicable rulesets are sufficient for the initial live protection decision. Unsupported provider, missing authentication, or ambiguous response means direct-default-branch is unavailable.
- Broad approved documentation prefixes remain subject to non-exempt governance and Redline precedence; docs/SPEC.md cannot be exempt in this repository.

**Plan:**
1. Amend docs/SPEC.md first and record the substantive precedence/bootstrap decision in docs/DECISIONS.md.
2. Add the smallest typed config and pure applicability evaluator under core/, reusing existing path/config patterns and emitting a structured decision.
3. Integrate the decision into checker/CI inputs so authoritative diffs skip only Work Record obligations and never hide changed malformed records or independent findings.
4. Update bootstrap-mode.md to discover actual documentation/roadmap/README candidates, check protection, present inert drafts, and require explicit Phase 3 approval. Update operating-mode.md and the compact agent reminders to evaluate applicability before branch/record requirements.
5. Add this repo's approved documentation paths with direct-default-branch disabled, then package/reinstall so dist and source agree.
6. Add focused unit tests for combinatorics and packaged temporary-repository E2E for bootstrap/local/CI behavior, including mixed scope, risk precedence, protection states, renames, dirty paths, invalid inputs, Unicode/spaces, and two layouts.
7. Run focused checks, budgets, packaging checks, and tests/run-all.sh; obtain a clean-context smart-model plan review before edits and a smart-model final review after verification. Address findings, then open and merge a PR only when all gates are clean.

Key conventions: SPEC is normative and changes first; config defaults preserve current behavior; no canonical roadmap path; tables over repeated skill prose; source/dist links must both resolve; changed-path evaluation is deny-overrides and repository-relative.

Target files: docs/SPEC.md, docs/DECISIONS.md, docs/ENFORCEMENT.md, docs/INTEGRATION.md, roadmap/features/workflow-applicability.md, agent-workflow.yaml, core/schema/agent-workflow.schema.json, core/config/, core/checker/, core/skill/{agent-workflow,operating-mode,bootstrap-mode}.md, core/skill/hooks/, core/skill/opencode/, core/templates/, tests/, scripts/package-skill.sh and generated dist/agent-workflow/.

Stop conditions: unresolved semantics between workflow exemption and direct-main; inability to fail closed on protection/risk; source/dist drift; an E2E caller can bypass mixed-scope precedence; or smart review finds a material contract gap.

**Verification plan:**
- When bootstrap inspects a repository, it shall suggest only discovered documentation/roadmap/README paths and require explicit approval -> bootstrap caller-surface E2E with protected, unprotected, rejected, partial, and unavailable cases.
- When a change contains only approved low-risk documentation, the checker shall report an explicit exemption without a Work Record -> packaged checker/reporter E2E.
- When any path is mixed, risky, protected, renamed across the boundary, or uncertain, the normal workflow shall win -> evaluator unit matrix plus packaged E2E.
- When branch protection exists or cannot be verified, direct-default-branch shall be denied -> classic-protection/ruleset/unavailable adapter E2E.
- When applicability is absent, existing consumers shall behave unchanged -> existing suite plus no-config regression E2E.
- When skill/package sources change, generated distribution and links/budgets shall remain valid -> package, link, budget, and full test suites.

**Plan review:** Pending clean-context smart-model review.

**Approvals:** Pending plan review; user authorized implementation and PR/merge contingent on preserving the agreed design and verification.

**Exceptions:** —

**State:** Blocked
<!-- agent-workflow:end -->

## Implementation

- Established task context from the approved design discussion and inspected the existing config, checker, CI, bootstrap, hooks, packaging, and Pallium consumer surfaces.

## Evidence

- Pending.

## Result review

- Pending.
