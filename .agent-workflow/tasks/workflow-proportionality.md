<!-- agent-workflow:start -->
**Outcome:**
Agent Workflow applies proportionate risk, review, and delegation controls; bootstrap and upgrades preserve those controls without unnecessary ceremony.

**Target:**
agent-workflow.

**Scope:**
Normative SPEC, risk/checker and skill guidance, bootstrap calibration, installation/upgrade path, package output, and focused tests in this repository.

**Constraints:**
Preserve hard security/contract/persistence/financial/boundary floors, explicit human approval for policy relaxation, compatibility and CI enforcement; do not edit consumer repositories or Pallium/dictation services; no silent self-waiver or extra services.

**Completion criteria:**
Unclassified paths remain distinguishable from proven danger; approved narrow policy changes persist without bypassing current-task gates; mechanical classification no longer mandates a separate agent; reviews/delegation scale to consequence; bootstrap proposes layout-specific low-risk zones and docs only with approval; install/upgrade has fewer redundant copies or sync steps with parity preserved; focused tests and the full suite pass.

**Requirement baseline:**
{"source":"pallium-relay:relay-msg-3571b68fa45a48d989a2c4d3b04a9c62","outcome":"Agent Workflow applies proportionate risk, review, and delegation controls; bootstrap and upgrades preserve those controls without unnecessary ceremony.","scope":"Normative SPEC, risk/checker and skill guidance, bootstrap calibration, installation/upgrade path, package output, and focused tests in this repository.","constraints":"Preserve hard security/contract/persistence/financial/boundary floors, explicit human approval for policy relaxation, compatibility and CI enforcement; do not edit consumer repositories or Pallium/dictation services; no silent self-waiver or extra services.","completion_criteria":"Unclassified paths remain distinguishable from proven danger; approved narrow policy changes persist without bypassing current-task gates; mechanical classification no longer mandates a separate agent; reviews/delegation scale to consequence; bootstrap proposes layout-specific low-risk zones and docs only with approval; install/upgrade has fewer redundant copies or sync steps with parity preserved; focused tests and the full suite pass."}

**Risk:**
High

**Complexity:**
Large

**Reason:**
The normative SPEC is Redline red with architecture-review; changing risk floors and governance is a contract surface. Five independently verifiable outcomes span the spec, checker, skill, bootstrap, packaging, and tests in one repository. No boundary violation is identified.

**Discovery:**
The checker maps gray and red alike to an Elevated floor; its predicate reports only the level. Redline already emits separate gray/red paths. assess-risk.md mandates a classification-only subagent. Redline permits suggesting explicit gray classification but forbids silent policy edits; the tuner already gives reviewed suggestions. Bootstrap has layout inspection and strict approved docs-applicability input, but extension blue test globs can be broad and ordinary code often remains gray. package-skill.sh default builds dist and recursively rebuilds both local installs; install-skill-locally.sh builds those two installs separately. A wrapper-only redirect would increase builds from two to three; one build plus two artifact copies is the safe simplification. Consumer bootstrap also copies checkpoint docs outside the installed package into docs/agent-workflow/, and its AGENTS/summary templates point there. Source/package parity and two-layout E2E checks exist. Pre-edit Redline found the SPEC red with architecture-review and no boundary violation.

**Material assumptions:**
- Gray is an uncertainty floor, not proof of intrinsic danger. If CI or policy treats gray as safe without approved blue classification, stop and redesign the gate; this PR cannot waive its own risk.
- Installed package checkpoint files can be canonical for new/upgraded consumers. If any runtime reader requires the extra docs/agent-workflow/ mirror, retain that reader's copy and narrow the consolidation.
- Bootstrap remains a conversational, human-approved policy proposal. If tests cannot validate proposal quality deterministically, test downstream approved-policy behavior in two layouts and make the remaining judgment explicit.

**Plan:**
1. Update SPEC risk, plan/review, bootstrap, and packaging/upgrade contracts first; append a focused decision. Treat gray as unclassified with a provisional Elevated floor until a separately reviewed, human-approved narrow policy change makes an evidenced path blue. Protected surfaces and new danger retain/raise current-task floors; no self-waiver.
2. Align assess-risk.md, plan-and-review.md, operating-mode.md, and Redline operating/bootstrap guidance. Replace Redline operating-mode.md stale-policy advice that demotes red to gray: retain the current verdict/floor/checkpoint until a separate approved governance change takes effect. Use deterministic verdict plus ordinary judgment for mechanical pre-edit classification; call separate agents only for real uncertainty and required material review. Select the cheapest reviewer capable of the consequence, preserve the non-implementer and High-risk human requirements, and never override user-selected settings. Record exact path evidence and consequences when proposing red/blue policy changes during ordinary work; batch nonurgent suggestions, do not repeat a rejected proposal without new evidence, and do not block an otherwise-ready task on an optional future-policy proposal. Persist only after approval through policy governance. Do not misstate authorized existing task exceptions as mechanically impossible self-waivers.
3. Keep Redline's zone verdict and conservative checker floor; change checker messaging to identify provisional gray-only gating only when no red, checkpoint, runtime-config, or contract signal independently requires Elevated/High. Add focused tests for each signal combination; no parallel risk state or policy-learning service.
4. Tighten bootstrap proposals from observed tracked layout/history: precise low-risk code/test candidates and discovered docs/roadmap/README, excluding governance, contracts, and genuinely mixed/uncertain paths. Missing history alone is not a safety finding: use inspected code/layout evidence when sufficient; retain conservative classification only when uncertainty remains. Reuse existing applicability approval and Redline red precedence. Test flat and nested layouts, mixed and protected cases.
5. Make installed workflow skill checkpoints canonical for new/upgraded consumers; stop copying only the redundant docs/agent-workflow/ mirror, retaining Redline docs/agent/ and docs/agent-redline/skills/ readers. Update owned AGENTS/summary references and upgrade guidance while preserving legacy files and links unless explicitly approved for removal. Build the package once to dist, then copy that exact artifact to both local native installs; keep source/dist/Claude/Codex parity checks.
6. Reinstall/package, run focused tests during edits and one required full suite before push, obtain independent result review and High-risk human result review, then PR/CI/merge if authorized and green. Stop on materially changed scope, failed assumptions, safety regression, or unresolved finding. Architecture-review checkpoint note accompanies the PR.
Key conventions/targets: SPEC before skill/checker changes; source in core/skill/, core/templates/, core/checker/, bundled Redline source; generated dist/ and committed .claude/skills/ from packaging, never hand-edit generated copies. This single Work Record owns all five related outcomes; phases are independently verified but not split into competing records.

**Verification plan:**
- When a gray path lacks approved classification and no stronger signal exists, checker shall show an unclassified provisional Elevated floor; red/contract/checkpoint/runtime-config signals and boundary block remain → focused checker goldens/predicate tests and E2E mixed-path cases.
- When ordinary work identifies a candidate policy correction or disputes a red path, the skill shall require exact evidence, human approval, separate reviewed governance change, and unchanged current-task floor/checkpoint until approved; optional future proposals shall not block ready work or repeat rejected suggestions without new evidence; authorized existing task exceptions remain accurately described → skill-source assertions plus clean-context scenario review.
- When pre-edit classification is mechanical, the skill shall allow deterministic verdict/ordinary judgment without a classification-only subagent; material reviews shall remain independent and cost-aware → instruction tests/budget check plus plan-review scenarios.
- When bootstrap sees two distinct layouts, it shall propose narrow evidenced blue code/test roots and discovered docs paths only; protected/mixed/uncertain files remain gated → two-layout packaged E2E and applicability schema tests.
- When installing or upgrading, the package shall remain discoverable and source/dist/Claude/Codex/checker-consistent without the extra workflow docs mirror or repeated local build; Redline docs and legacy mirrors remain → package parity, install-probe, links, generated owned AGENTS marker, and legacy-upgrade tests.
- When the whole change is complete, the required suite shall pass at final revision and architecture-review/human result review shall be satisfied → bash tests/run-all.sh, PR CI, final-diff review.

**Plan review:**
Astra clean-context review on 2026-09-25; see Plan review below. Two blocking corrections and three clarifications incorporated before human approval.

**Approvals:**
Approved by user 2026-09-25T10:32:24Z: "i approve"

**Exceptions:**
—

**State:** Ready for review
<!-- agent-workflow:end -->
## Plan review

Astra reviewed the draft independently on 2026-09-25. It caught the red-to-gray stale-policy contradiction and a proposed installer change that would increase rebuilds. It also required a precise workflow-only mirror scope, diagnostics for independent Elevated signals, and accurate treatment of authorized exceptions. The plan above incorporates each item. A bounded delta review of the corrected Plan and Verification plan passed with no new contradiction; this is not human approval.

The coordinator reviewed the five-outcome direction on 2026-09-25 and confirmed the gray floor, then clarified optional proposal batching/nonblocking behavior and missing-history evidence. This is not human approval.

Human approval was verified directly in coordinator task 01a0d7cd-696b-76a0-8f2f-48a80a201905, user message 01a0d81f-632a-7461-b982-5a599c935076, after the coordinator presented the reviewed plan. Relay delivery relay-msg-48e784a90bae46c6bdf416ea384d3881 carried the approval to this task.

## Implementation

- 2026-09-25: Established the record before discovery or implementation on isolated branch feat/workflow-proportionality.
- 2026-09-25: Discovery and pre-edit Redline complete. Plan reviewed, corrected, and committed; no source implementation or tests started.
- 2026-09-25 handoff: Source pallium-relay:relay-msg-3571b68fa45a48d989a2c4d3b04a9c62; record agent-workflow:workflow-proportionality. Last clean revision before coordinator clarifications 9aa5e07d966554b62324e81b08ab4e80d9df03c8. State Blocked pending exact human plan approval. Next: record approval, then change SPEC first.

- 2026-09-25: Verified exact human approval and moved State to Ready to implement. Planned source targets: docs/SPEC.md, docs/DECISIONS.md, relevant integration/packaging/enforcement docs; core/skill/operating-mode.md and bootstrap-mode.md; core/templates/checkpoints/assess-risk.md and plan-and-review.md; bundled Redline operating/bootstrap guidance; core/checker/predicates.py; package/local-install scripts; consumer AGENTS/summary templates; focused checker/bootstrap/package tests; generated dist/ and committed Claude skill. No consumer repository edits.
- 2026-09-25: Consolidated workflow checkpoint guidance into the installed skill package; installer now builds once and copies to both native installs.
- 2026-09-25: SPEC contract committed first at f246de7. Propagated deterministic-first risk guidance, removed Redline red-to-gray stale-policy instruction, added provisional-gray checker detail and six-case matrix, and aligned enforcement docs. Focused checker suites: 122 passed. Bootstrap and package slices are in separate disjoint-file implementation; State remains Ready to implement.
- 2026-09-25: Bootstrap slice inspects tracked paths, layout, tests, and representative code before narrowing zone proposals; protected contract/governance and uncertain paths stay gated. Two flat/nested approved-policy reporter cases passed. Packaging slice builds once and copies identical artifacts to Claude/Codex installs, stops creating the extra workflow-doc mirror for new consumers, and preserves legacy mirrors. Focused install-sync and budget checks passed. Lead reviewed both slices and narrowed the bootstrap test fixture.

## Evidence

Commit a5fb5f2 contains the reviewed source and generated package changes. At that content revision, bash tests/run-all.sh passed every layer: budget, schema, work-record, checker (234), redline, tuner, hooks, links, and package, including the two-layout packaged bootstrap simulation. The focused bootstrap calibration tests passed (2). The earlier local full-suite failures were environment setup (an absent worktree virtualenv and a Git Bash Python 3 shim) or the public guide mirror before sync; all were corrected and the final full run passed. The local checker with the actual Redline verdict has no blocking findings; architecture-review remains shadow/advisory until PR review or label. No applicable roadmap item was found.

Skill-feedback triggers 2 and 4 dropped: the stale Redline classification instruction and reviewer-caught plan contradiction are corrected in this change; no outstanding upstream defect remains.