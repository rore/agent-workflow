<!-- agent-workflow:start -->
**Outcome:** Pull-request CI detects a Work Record requirement baseline rewritten after its first committed version.

**Target:** agent-workflow.

**Scope:** Normative baseline rule, existing checker and CI history integration, focused and end-to-end tests, relevant public and agent guidance, generated package, and this Work Record.

**Constraints:** Preserve current Work Record format, legitimate legacy baseline establishment, and the advisory commit-order rule. Do not claim Git history proves initial requirement accuracy, semantic classification, or resistance to rewritten branch history. Avoid a new artifact, configuration field, or CI job.

**Completion criteria:** On PRs, a later baseline rewrite fails the existing Agent Workflow check for new and existing Work Records; unchanged baselines pass despite JSON formatting changes; legacy owner establishment remains possible; unavailable required history fails visibly; end-to-end tests cover real Git history and packaged CI-style execution; documentation explains the protection and limits.

**Requirement baseline:** {"source":"user-request:0f7c016d-cad2-48ad-9f5f-330325cf69f2","outcome":"Pull-request CI detects a Work Record requirement baseline rewritten after its first committed version.","scope":"Normative baseline rule, existing checker and CI history integration, focused and end-to-end tests, relevant public and agent guidance, generated package, and this Work Record.","constraints":"Preserve current Work Record format, legitimate legacy baseline establishment, and the advisory commit-order rule. Do not claim Git history proves initial requirement accuracy, semantic classification, or resistance to rewritten branch history. Avoid a new artifact, configuration field, or CI job.","completion_criteria":"On PRs, a later baseline rewrite fails the existing Agent Workflow check for new and existing Work Records; unchanged baselines pass despite JSON formatting changes; legacy owner establishment remains possible; unavailable required history fails visibly; end-to-end tests cover real Git history and packaged CI-style execution; documentation explains the protection and limits."}

**Risk:** High

**Complexity:** Moderate

**Reason:** Redline classifies the normative SPEC as red and requires architecture-review. The new non-waivable PR gate affects every consuming repository; a false pass or false failure changes governance behavior.

**Discovery:** The current checker parses Requirement baseline as a five-field value and enforces an exact baseline-to-current change chain, but only against the baseline in the current file. The existing workrecord.commit_order Git walk is advisory and may skip missing history. Both source and shipped PR workflows fetch full history and pass real base/head SHAs, avoiding the synthetic merge commit. The CLI discovers each changed Work Record from trusted NUL paths, but currently omits deleted records. Historical records may lack the baseline or have older unrelated fields; the history reader should parse only the baseline field using the existing parser. See docs/SPEC.md §§9.1, 13.2; core/work_record/parser.py; core/checker/{checker,predicates}.py; core/templates/.github/workflows/agent-workflow.yml.template; tests/checker/test_checker.py; tests/package/check-e2e-bootstrap.sh.

**Material assumptions:** 1. Assumption: real base/head commits are available in packaged PR CI and a first-parent path history can identify the first committed record version for new records and the first owner-established baseline for base-existing legacy records without a separate anchor artifact. Disprove with a real Git fixture where a merge, legacy establishment, or alternate taskPath produces the wrong anchor. Action: stop and revise the algorithm before shipping. 2. Assumption: a changed Work Record deleted or renamed away may be treated as missing rather than silently ignored. Disprove with an established supported archival/move flow. Action: return to planning rather than block that flow incidentally. 3. Assumption: historical baseline extraction can reuse the parser's marker/field/JSON validation without requiring older unrelated fields to meet today's shape. Disprove with representative legacy fixture. Action: add only the narrow compatibility handling needed. 4. Assumption: local checker calls without a complete explicit base/head pair should remain usable, while PR calls with supplied but unusable history must fail closed. Disprove with CI invocation or consumer adapter requiring another signal. Action: revise activation without weakening PR checks.

**Plan:** 1. Amend normative docs/SPEC.md first: the existing PR checker compares each changed Work Record's parsed baseline to the base-tree baseline; a new branch-created record must carry a valid baseline in its first commit, while a base-existing legacy record may establish one once from authority. A later mismatch, a malformed historical baseline, or unavailable supplied history blocks, while commit-order stays advisory. Explicitly limit the claim to visible Git history and preserve reviewer responsibility for initial accuracy/meaning. Add a decision note. 2. Reuse the parser's baseline validation through a narrow historical-field reader. Add one non-waivable requirements.baseline_unchanged predicate in core/checker/predicates.py, using explicit base/head SHA context, shared-ancestry validation, first-parent path history, bounded Git calls, and parsed value comparison; skip only when neither history ref was supplied, fail when exactly one was supplied. Compare the checked Work Record to the anchor, not raw JSON bytes. 3. In core/checker/checker.py, ensure changed Work Record deletions/renames do not evade the existing missing-record gate; preserve multi-record, custom taskPath, and documentation-only applicability behavior. Do not add another artifact, config, job, path classifier, or mandatory commit-order rule. 4. Add real-repository tests for base-present/new/legacy records, source and field tampering, JSON reformat, missing or malformed first-commit baseline, deletion/rename, multi-record and custom-path handling, missing/invalid refs, and a synthetic PR-merge checkout. Exercise the generated vendored checker with --base-ref, --head-ref, and NUL paths in a temporary consumer repo; run package and full suites. 5. Update docs/ENFORCEMENT.md, docs/BEHAVIORAL_INTEGRITY.md, and minimal operational guidance; scan README/INTEGRATION for needed corrections; regenerate/install dist/agent-workflow/; complete a clean-context result review. Stop if the history source cannot be distinguished reliably from a merely missing baseline or if the gate would break supported record migration.

**Verification plan:** When an existing or newly established baseline changes later, the PR checker shall exit 2 with a named, non-waivable finding → real Git fixture tests for source and behavioral fields plus vendored CLI E2E. When only JSON formatting or unrelated Task Context changes occur, the baseline predicate shall pass → semantic-JSON and approved-change fixtures. When legacy records establish a baseline or a PR contains multiple/custom-path records, each relevant baseline shall be anchored and checked independently → real Git multi-record/legacy/custom-layout tests. When a changed record is deleted/renamed or supplied history is unusable, PR CI shall fail visibly → deletion/rename, single/missing-ref, shallow/unrelated-history, and synthetic-merge E2E cases. When the package ships, source and vendored checker behavior shall agree → package drift, source/vendored parity, and bash tests/run-all.sh.

**Plan review:** Clean-context review by /root/baseline_plan_review; findings and disposition under ## Plan review.

**Approvals:** Approved by user 2026-09-24: "yes"

**Exceptions:** —

**State:** Ready to implement
<!-- agent-workflow:end -->

## Plan review

- Reviewer challenged a new Work Record with no baseline in its first commit: a later "first valid" anchor would bless a revised value. Plan revised to require a valid baseline in the first committed version of branch-created records; only base-existing legacy records can establish one later from authority.
- Reviewer required malformed historical baselines to fail, and a single supplied history ref or unrelated refs to fail instead of skipping. Plan and verification revised accordingly. Deletion/rename-old paths must enter the existing missing-record gate. No other plan blocker remained.

## Implementation

- Established initial Task Context before implementation. Scope is not documentation-only. Redline pre-edit classification is RED/architecture-review, with no boundary rule or API/schema/security path in the intended change.
- Discovery found that the checker already receives the PR's real base/head SHAs and parses baseline values; no extra CI job or Work Record field is needed. Architecture checkpoint: add a non-waivable history check without changing semantic-approval authority or commit-order policy. Compatibility risk is high for legacy records, record deletion, and incomplete Git history; the test plan targets each.
- Handoff: branch feat/requirement-baseline-history; last committed revision 2d200c9 established the untouched baseline. State remains Blocked for High-risk plan approval. Next action after approval: edit docs/SPEC.md first, then implement and test the gate. Source item user-request:0f7c016d-cad2-48ad-9f5f-330325cf69f2; Work Record agent-workflow:requirement-baseline-history at .agent-workflow/tasks/requirement-baseline-history.md.
- User approved the reviewed plan on 2026-09-24. Human-authored non-exempt PRs without Work Records remain governed by the existing missing-record gate; no author-based exemption is in scope.
- Implementation targets: docs/SPEC.md, docs/DECISIONS.md, core/work_record/parser.py, core/checker/{predicates,checker}.py, tests/checker/ fixtures and real-Git tests, tests/package/ E2E wiring, docs/{ENFORCEMENT,BEHAVIORAL_INTEGRITY}.md, minimal agent guidance, and regenerated dist/agent-workflow/ / local install. Scan README.md and docs/INTEGRATION.md for corrections before finalizing.

## Evidence

- Source request: user-request:0f7c016d-cad2-48ad-9f5f-330325cf69f2.
