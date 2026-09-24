<!-- agent-workflow:start -->
**Outcome:**
PR history checking rejects a Work Record first committed without a valid Requirement baseline on a merged side branch.

**Target:**
Agent Workflow's committed Requirement baseline checker.

**Scope:**
Correct the shared history traversal in `core/checker/predicates.py`, add real-Git merge-history regression coverage, regenerate packaged checker copies, and maintain this Work Record.

**Constraints:**
Preserve the existing SPEC first-committed-version rule, legacy base-record allowance, and no-refs local behavior. Do not rewrite consumer history, patch Pallium's vendored copy, add a dependency, or weaken the gate for this migration case.

**Completion criteria:**
A PR head reached through a merge's second parent fails when its Work Record's first commit lacks a valid baseline or an initial baseline is later rewritten; an initially valid baseline still passes. Source and packaged checks agree, required tests and CI pass, and the upstream merged revision is reported to the Pallium task.

**Requirement baseline:**
{"source":"codex-task:01a0c998-aeba-71a2-8603-9fb043051d2d","outcome":"PR history checking rejects a Work Record first committed without a valid Requirement baseline on a merged side branch.","scope":"Correct the shared history traversal in `core/checker/predicates.py`, add real-Git merge-history regression coverage, regenerate packaged checker copies, and maintain this Work Record.","constraints":"Preserve the existing SPEC first-committed-version rule, legacy base-record allowance, and no-refs local behavior. Do not rewrite consumer history, patch Pallium's vendored copy, add a dependency, or weaken the gate for this migration case.","completion_criteria":"A PR head reached through a merge's second parent fails when its Work Record's first commit lacks a valid baseline or an initial baseline is later rewritten; an initially valid baseline still passes. Source and packaged checks agree, required tests and CI pass, and the upstream merged revision is reported to the Pallium task."}

**Risk:** Elevated

**Complexity:** Moderate

**Reason:**
Redline classifies the checker and generated copies gray/watch with no checkpoint; tests and Work Record are blue. Elevated because this is a non-waivable provenance gate; Moderate because merge-DAG ordering and source/package parity need validation.

**Discovery:**
The checker logs only the first-parent chain from merge-base to PR head, so a side branch's first Work Record commit can be hidden by a merge snapshot. Existing real-Git E2E tests cover linear history and an explicit pre-merge PR head, not a PR head that includes a side-branch merge. SPEC §§9.1/13.4 already require the first committed baseline; no normative contract change is needed.

**Material assumptions:**
Git's full-history topological traversal can expose ancestor commits before their merge snapshot for this path. Disproof: the synthetic merge regression or a valid merged baseline case fails; then adjust the history walk without changing the baseline rule.

**Plan:**
Add failing real-Git merged-side-branch cases (missing/malformed initial baseline and initial-baseline rewrite) plus a valid control, with a skewed ancestor timestamp; pass the merge commit as PR head. Replace the first-parent path walk with full-history, topological, reverse traversal; regenerate checker copies; run source and vendored E2E plus the full suite, review the final diff, then PR and merge. Stop if the fix requires changing the SPEC or migration semantics.

**Verification plan:**
- Invalid first side-parent commit remains blocked after merge -> real-Git source and vendored E2E with missing/malformed baseline and rewritten baseline, including skewed timestamps.
- Valid first side-parent commit remains accepted -> real-Git positive merge control and existing linear/legacy tests.
- Source and installed checker behavior agree -> same merged-history E2E through packaged checker and package parity checks.
- Repository remains shippable -> full test suite, PR CI, and independent result review.

**Plan review:**
Approved by clean-context /root/baseline_merge_plan_review; details below.

**Approvals:**
Not required at this risk level.

**Exceptions:**
—

**State:** Ready for review
<!-- agent-workflow:end -->

## Implementation

Isolated branch `feat/baseline-merge-history` at `cef51bc9519ccb55dbd2a57fd8f3467b7b9e060c`. Initial planning committed before code as acdc3a5. Clean-context plan review approved the bounded change. No applicable native roadmap item was found. Target files were core/checker/predicates.py, tests/checker/test_baseline_history_e2e.py, generated checker copies/manifests, and this record. Six invalid merged-parent cases exposed the old bypass; the shared walk now uses full history plus topological reverse order. No SPEC or migration semantics changed.

## Plan review

The reviewer required --full-history --topo-order --reverse so path simplification and skewed commit timestamps cannot hide an ancestor. Tests must use the merge commit as PR head, cover missing/malformed/replaced initial baselines and a valid control, and run source and vendored checkers. This remains a bounded first-anchor fix; it does not claim to validate every intermediate snapshot or independently introduced sibling records.

## Evidence

The new real-Git cases reproduced six false passes before the fix; after the one-walk change, all eight merged-parent cases passed through source and packaged checkers. On the working tree atop 53f3a68, native test layers budget, schema, work-record, checker, redline, tuner, hooks, and links passed; the WSL package layer passed dist parity, committed-skill parity, references, install probe, and two-layout bootstrap E2E. The temporary test-venv junction was removed and its target preserved. git diff --check passed. Post-commit PR CI remains authoritative.

## Result review

Independent final-diff review pending. No separate skill-feedback issue: the reported upstream defect is being corrected in this PR, so a second issue would duplicate the actionable work.
