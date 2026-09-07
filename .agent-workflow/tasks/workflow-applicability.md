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
2. Add the smallest typed config and pure applicability evaluator under core/, reusing existing path/config patterns and emitting a structured decision. Define a lossless status-aware Git path contract; legacy/incomplete path inputs cannot grant exemption.
3. Integrate the decision into checker/CI inputs so authoritative diffs skip only Work Record obligations and never hide changed malformed records, protected installed/configured surfaces, global Redline findings, or independent failures when zero records exist.
4. Update bootstrap-mode.md to discover actual documentation/roadmap/README candidates, obtain fresh classic/ruleset protection evidence, present inert drafts, and require explicit Phase 3 approval. Add a deterministic proposal/approval seam that caller-surface E2E can exercise. Update operating-mode.md and the compact agent reminders to evaluate applicability before branch/record requirements and recheck protection at use time.
5. Add this repo's approved documentation paths with direct-default-branch disabled, then package/reinstall so dist and source agree.
6. Add focused unit tests for combinatorics and packaged temporary-repository E2E for bootstrap/local/CI behavior, including mixed scope, global risk with zero records, protected/configured task paths, protection freshness/states, lossless renames and whitespace paths, dirty/omitted paths, invalid inputs, Unicode/spaces, legacy opt-out behavior, and two layouts.
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

**Plan review:** Clean-context review recorded in [Plan review](#plan-review); proceed only with the required corrections below incorporated. Human approval remains separate.

**Approvals:** Approved by user 2026-09-07: "ok. so keep all these design and plan, then you can start. be very budget conscious, so plan what you do as an expensive model and what you can delegate to cheap models to make this cost less. reviews should be done with a smart model. if you are sure everything works and verified you can take it through pr to merger"

**Exceptions:** —

**State:** Ready to implement
<!-- agent-workflow:end -->

## Implementation

- Established task context from the approved design discussion and inspected the existing config, checker, CI, bootstrap, hooks, packaging, and Pallium consumer surfaces.

## Evidence

- Pending.

## Result review

- Pending.

## Plan review

Clean-context review, 2026-09-07. Reviewed the recorded plan against SPEC sections 1, 5, 6, 8, 9.4, 11 and 13; config loading, checker discovery/aggregation, Redline risk translation, operating/bootstrap guidance, both CI surfaces, vendoring and consumer E2E seams.

Disposition: the approach is sound with the following required implementation constraints. These clarify existing fail-closed and caller-surface requirements; they do not authorize implementation, approve policy drafts, or replace the separate human approval required for High risk.

1. **Complete, authoritative scope.** The existing `git diff --name-only` / newline-list / `strip()` path seam is insufficient: it loses rename sources and changes whitespace-bearing filenames. Define one lossless Git collection contract (including both rename sides, staged, unstaged, untracked and committed branch changes); reject ambiguous legacy input for exemption. CI must use trusted event refs and the same full path set for applicability and Redline, not an agent-provided subset. Missing base, malformed paths, unsupported file types such as symlinks/submodules, or incomplete coverage must deny exemption. Test rename-to-docs, dirty mixed scope, leading/trailing whitespace, and an omitted non-exempt file through the actual packaged caller.
2. **Risk cannot disappear with the record.** `run_checker_multi([])` currently runs no predicates, while the Redline reader defaults missing fields toward Routine. Evaluate global config/risk/independent findings even when exemption produces zero records. Missing, malformed, unknown or incomplete risk evidence cannot prove low risk; shadow mode must not make sensitive paths exempt. Preserve boundary failures and independent blocking findings. Define a supported pre-edit risk source and raise-by-judgment behavior without requiring a Work Record merely to decide applicability. Test absent/partial verdicts, boundary failures, and red/watch overlaps beneath approved docs prefixes.
3. **Deny surfaces must cover the real install.** Protect applicability configuration, Redline policy, schemas, CI, instruction/hook sources and their installed/vendored copies; include repository-specific authoritative docs such as SPEC and the configured Work Record location. Account for policy/config edits or removals in the same diff so a change cannot erase its own exclusion before evaluation. `discover_slugs_from_changed_files` currently hardcodes `.agent-workflow/tasks/`: test a second `taskPath` under an otherwise approved docs prefix, including changed malformed/multiple records, to ensure exemption cannot conceal them.
4. **Direct-default permission has fresh, separate inputs.** A bootstrap observation is not standing evidence that the branch remains unprotected. Resolve the actual repository/default branch and recheck protection at use time, including after scope/config changes; deny on stale evidence, permission errors, ambiguous not-found responses, incomplete rule coverage or unsupported hosts. Do not treat actor bypass capability as an unprotected branch. A pure evaluator may consume a protection result, but the operational caller must obtain it live. Test protection becoming enabled after bootstrap, ruleset-only protection, uncertain responses, and default-branch identity changes. Permission to edit still does not authorize commit/push or prove protection cannot change after the check.
5. **State CI's enforcement boundary accurately.** Both current workflows are PR-only; no push event is checked. Do not describe the shipped PR workflow as preventing direct pushes. Either document that direct-default behavior is agent guidance with live checks and no pre-push enforcement, or explicitly scope any push integration and test its event-specific before/after refs, missing-history failures and skipped PR-only steps. Keep required jobs running and make unexpected checker/reporter exits fail rather than interpreting every non-2 exit as success.
6. **Bootstrap approval needs a real test seam.** Existing bootstrap E2E explicitly skips conversational Phases 1-3 and overwrites config with a fixture. It cannot prove discovery, rejection or partial approval. Exercise the actual deterministic proposal/approval helper if one is introduced, with inert drafts and only selected approved settings persisted, including direct-default separately; otherwise label the simulation honestly and add a concrete conversational acceptance check. Tests must not fabricate approval by placing an approved flag in their own replacement config. Preserve Phase 5's separate CI confirmation.
7. **Bound compatibility and normative claims.** Qualify the unconditional requirements in SPEC sections 1, 6 and 13.1, and distinguish applicability from a per-task waiver under section 11. Define precedence with the existing `requiredForBranchChanges: false` opt-out: no-applicability consumers retain their behavior, but the legacy flag cannot establish new direct-default eligibility or suppress independent failures. Add no-applicability CLI/API and legacy-opt-out regressions. Include the new module in `scripts/build-vendored-checker.sh` and execute installed entry points; a source-only evaluator test does not establish packaged parity.

The final review must verify these constraints against the implemented source and packaged journeys. Any unresolved protection/risk evidence model or inability to preserve deny precedence remains a return-to-planning condition. No product files, approval field or State were changed by this review.
