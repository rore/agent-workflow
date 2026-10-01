<!-- agent-workflow:start -->
**Outcome:** Planning and review distinguish required behavior from chosen mechanisms and challenge unnecessary complexity without weakening safety or user intent.

**Target:** agent-workflow.

**Scope:** Existing planning and result-review guidance, required generated mirrors, and task-local verification in this repository.

**Constraints:** Preserve required behavior, safety, compatibility, explicit user-required mechanisms, protected tests and contracts, scope and existing approval rules. No private incident details, unrelated redesign, new fields, artifacts, checkpoints, gates, research phase, scoring system or evaluation framework; no consumer or shared-checkout changes.

**Completion criteria:** Existing coverage and gaps are identified; the smallest justified guidance distinguishes guarantees from mechanisms and questions overall necessity/proportionality; three lightweight scenarios accept safe replacement, retain a necessary mechanism and reject weakened protected behavior; required packaging, validation, independent reviews and delivery gates pass.

**Requirement baseline:**
{"source":"codex-user:01a0f75a-dd25-7a30-a2c6-3d5793a5105d","outcome":"Planning and review distinguish required behavior from chosen mechanisms and challenge unnecessary complexity without weakening safety or user intent.","scope":"Existing planning and result-review guidance, required generated mirrors, and task-local verification in this repository.","constraints":"Preserve required behavior, safety, compatibility, explicit user-required mechanisms, protected tests and contracts, scope and existing approval rules. No private incident details, unrelated redesign, new fields, artifacts, checkpoints, gates, research phase, scoring system or evaluation framework; no consumer or shared-checkout changes.","completion_criteria":"Existing coverage and gaps are identified; the smallest justified guidance distinguishes guarantees from mechanisms and questions overall necessity/proportionality; three lightweight scenarios accept safe replacement, retain a necessary mechanism and reject weakened protected behavior; required packaging, validation, independent reviews and delivery gates pass."}

**Risk:** Elevated

**Complexity:** Simple

**Reason:** The effective policy leaves loaded core templates and generated harness guidance gray/watch; they are not ordinary documentation. One narrow guidance clarification; no red, runtime-config, contract-schema or boundary surface intended.

**Discovery:** SPEC §9.1 already separates context from approach; §9.4 governs plans and approvals; §9.7 tests adequacy/scope/assumptions. Behavioral integrity protects requirements, contracts and tests. Existing plan-and-review and review-result do not explicitly distinguish inherited mechanisms from guarantees or challenge overall necessity/proportionality. This clarifies reviewer judgment, not normative gates. Planning is 876/900 tokens; result review 655/700, so remove duplicated verification-example/rationale prose rather than raise ceilings.

**Material assumptions:** This clarifies existing planning/review judgment without changing normative requirements. If discovery requires new semantics or a protected surface, stop, reassess and obtain the applicable review before editing.

**Plan:**
1. Add one canonical short Approach paragraph in core/templates/checkpoints/plan-and-review.md: distinguish outcomes/safety/compatibility from mechanisms; establish protected behavior first; inherited code/tests are not proof of necessity; assess overall necessity/proportionality; prefer simpler supported options only preserving behavior, explicitly required mechanisms and scope; cross-reference behavioral-integrity.md and prohibit weakening protected tests/contracts. Trim only repeated field-example/rationale wording to stay within 900 tokens.
2. Add one short pointer in core/templates/checkpoints/review-result.md to apply that same distinction to the overall approach, not only patch correctness. No duplicated safety rules, new gate, SPEC/config/checker/test change or extra artifact. No substantive architectural decision; rationale belongs in the PR and this record rather than a new decision-log entry.
3. Regenerate package and reinstall owned isolated native mirrors. Check three lightweight scenarios with the independent reviewer; run existing budgets, links/package/skill validation and mandatory full suite; obtain independent result/adequacy acceptance, then separate PR/CI/thread resolution and authorized merge.
Conventions: source-first edits, existing checkpoint load points, canonical relative cross-reference, unchanged user-selected independent sessions. Stop before new scope/normative semantics, unsafe simplification, failed assumption or unresolved finding. The source paragraph itself is the bounded implementation; no cheap-agent delegation because coordination would exceed the edit cost. Smart reviews remain independent.

**Verification plan:**
- Existing coverage/gap and exact minimal changed guidance → source/SPEC comparison and independent plan/result review.
- Safe replacement, necessary safety/compatibility mechanism retained, protected-contract weakening rejected → three lightweight reviewer scenarios recorded in existing Evidence prose, no framework; include explicitly required mechanism and unknown external evidence as boundary checks.
- No weakened protections, new process or private details → bounded diff and cross-reference review against behavioral integrity, existing scope and approval rules.
- No recurring budget growth beyond existing ceilings; packaged/native guidance parity → before/after budget measurements, existing package/link tests and skill validator after install.
- Verified delivery → final unchanged-product nine-layer suite, independent verification-adequacy acceptance, actual PR CI and disposition of every review finding before match-head merge.

**Plan review:** Agent technical review: /root/mechanism_guidance_plan_review, clean-context non-implementer Sol/high, approved dead3afa632858aad0d8d6b1a9ff87602f0a3971; risk and verification adequacy accepted, no blocking findings. Full disposition below.

**Approvals:** Not required at this risk level. Direct user authorization to perform the separate task is verified below; it is not a fabricated later review.

**Exceptions:** —

**State:** Ready for review
<!-- agent-workflow:end -->

## Authoritative request

Separate assignment `relay-msg-1e918989c9a24e7b8673e81d8e7970aa`, delivery `relay-delivery-3408673cbece462fa11cc53a889ab667`, from @workflow-manager. Main read all payload pages and the attached request. Direct human authorization independently verified in manager thread `01a0d7cd-696b-76a0-8f2f-48a80a201905`, user source `01a0f75a-dd25-7a30-a2c6-3d5793a5105d`, exact quote "ok, let's do this", following the two-clarification assessment. Private incident details are not copied into public files. Authorized delivery/merge remains subject to actual gates.

## Implementation

- Invoked Agent Workflow, evaluated applicability and classified before discovery/planning/edits. Loaded harness instructions cannot use the documentation-only exemption.
- Separate branch `feat/planning-proportionality`, current main baseline `2908156db674cea0f99643e56a02b3a5907bf92c`. Reused clean isolated checkout; retained ignored bootstrap proof. Existing `workflow-proportionality` record/branch belongs to merged PR #42 and is not this task.
- State Blocked means discovery/plan/review not complete, not missing task authorization. No product edits yet. No applicable canonical roadmap item: board's Now item is local-doctor, whose broader scope and ownership remain untouched.

## Evidence

Effective zone policy: core templates and required dist/native mirrors gray/watch; Work Records blue. No intended boundary dependency or red-zone edit. Risk Elevated, Complexity Simple. The shared checkout remains owned by other work and is not edited.

Pre-edit clean-context classifier /root/proportionality_scope_risk confirmed gray/watch and Elevated floor with no red/checkpoint/boundary/API/schema/security/config touch. Its first read-only command failed environment error 1385; narrow elevated retry succeeded, no edits. Current-main installed guidance allows direct mechanical classification; the shared root's older skill must not be used to impose stale extra ceremony. Initial genuine reporter/checker at d02d93f returned 0/2, pending plan-review/Blocked state, not readiness. Budget baseline: planning 876/900, result review 655/700; all 22 files pass.

Implemented only the two approved load-point edits: canonical Approach paragraph and result-review pointer. Removed repeated field-example/rationale prose, retaining explicit criterion-to-check mapping. No normative contract, runtime, test or gate changed. Regenerated 72-file package and both owned local installs; standalone skill validator and diff check pass. All 22 unchanged ceilings pass: planning 886/900 (+10 tokens), result review 671/700 (+16), combined recurring cost +26 estimated tokens. No ceiling raised. Product verification and independent scenario/result acceptance remain pending.

Result reviewer /root/mechanism_guidance_plan_review found one valid trim error at 129e926: compact Approach must remain concrete enough to predict the diff. Restore that exact existing clause; other trims retain criterion-to-check mapping. This is a bounded correction within the approved plan, not new scope. The cheap runner's first full-suite invocation routed through WSL and failed at schema because python was unavailable; its Git calls also could not interpret the Windows worktree pointer. Failure log hash `9DEA2004F2427AF38A842F29B351455B727E3C2248C40C23A800CD62C37C71CF`; malformed wrapper status/executor exit 2 is not a product pass. No further environment investigation or unapproved rerun: main will use the already verified explicit native Git Bash/Python invocation at the corrected product revision.

Skill feedback trigger 4 dropped: the old shared-checkout install versus current isolated install was a local version-selection mistake, not contradictory upstream instructions. The requested judgment clarification is addressed here rather than submitted as a separate feature-request defect. No public issue or private incident detail is published.

Native full suite at corrected fc9aa8 stopped in links (session 96612, final chunk d74fa2, exit 1): the required public checkpoint mirrors docs/agent-workflow/plan-and-review.md and review-result.md differ beyond tests/links/check-links.py's declared rewrite map. Budget/schema/Work Record/checker/Redline/tuner/hooks passed, but the full suite did not. Before further edits, add those two exact public destinations to the implementation target list as required mirrors of already-approved source; they are blue and preserve the Elevated overall floor. No source or normative behavior expansion. Main read both public files and parity rule; there is no standalone generator, so apply the exact reviewed source delta with existing public-link rewrites preserved. Independent reviewer confirms this missing-mirror finding and requires focused validation plus final full rerun. Latest budgets after restoring concreteness: planning 898/900 (+22), result 671/700 (+16), total +38 estimated tokens; no ceiling raised.

Final complete native suite passed at unchanged clean product c30d62856859703b7e115c3b280babee263c70fd: session 16481, final chunk 0adc1f, executor exit 0, all nine layers ok. Log .local/planning-proportionality-final-native-suite.log SHA256 `84907233F82F17DD557585BDD43EDD511F720EB5331AF493C75955D1C33EE54F`; Windows Python 3.12.14 and native Git Bash. Includes package/install/public parity and relative links, all budget ceilings, schema/Work Record/checker, reporter/actual CI callers, tuner, hooks and two-layout bootstrap transitions. Focused links also passed all 200 files after public sync. Earlier failed native log SHA256 `57C9A28EC20D840DCD1CE1C93DF37C1A8A73451C15A7F6CD5E2A7A36DBDE4572` remains retained, not counted as success. Current final budget +38 estimated recurring tokens; no new framework/fields/gates or protected test changes. Subsequent readiness commit changes only this record, reusing reviewed and verified unchanged product identity.

## Result review

Agent technical review: /root/mechanism_guidance_plan_review, clean-context non-implementer Sol/high; final independent result and adequacy approval at c30d62856859703b7e115c3b280babee263c70fd.
Reviewed revision: c30d62856859703b7e115c3b280babee263c70fd.
Verification adequacy: Approved. Reviewer inspected source/normative limits, protected behavior, all required native/dist/public mirrors, three scenarios, final clean head, final log and hash; authoritative parent executor exit 0 referenced. Compact-plan concreteness and public-mirror findings are both resolved, no open finding. PR CI/thread resolution/merge are not inferred from local verification.

Independent lightweight scenario outcomes from actual installed guidance: (1) replace the bespoke copy wrapper when the supported alternative preserves byte identity, access restrictions and error reporting and no mechanism is mandated; (2) retain the wrapper until concurrency exclusion and legacy-format compatibility are preserved; (3) reject deletion of a protected contract test and weaker isolation verification. Explicitly user-required mechanisms need user authority to change; unknown external failure calls for causal evidence and assumption validation, not an unsupported extra abstraction. These are review exercises, not deployed changes or proof of future agent compliance. Same non-implementer reviewer reused unchanged source/scenario review for the two bounded remediation deltas and independently accepted the final full-run evidence; no broader review restart or fabricated human approval.

## Plan review

/root/mechanism_guidance_plan_review inspected the complete record and authoritative attachment, planning/result/behavioral-integrity templates, SPEC §§9.1/9.4/9.7, contribution discipline and effective policy at clean revision dead3af. Approved: Elevated classification and verification plan appropriate, no blocking finding. New wording must apply existing Task Context/plan/result judgment and preserve verification mapping and protected behavior. No SPEC/High gate is needed for the bounded clarification; a new mandatory criterion, scope expansion or protected-behavior change would require SPEC-first reclassification and review. This is plan-only acceptance, not result approval.

Implementation pickup: source targets are exactly core/templates/checkpoints/plan-and-review.md and review-result.md; required dist/native copies and manifests are generated. No other product file is approved for edits. Context baseline remains unchanged; user authority is already verified. State advanced after plan acceptance, before source edits.
