<!-- agent-workflow:start -->
**Outcome:**
Agent Workflow updates distinguish completed historical tasks from active work before applying current Work Record gates.

**Target:**
agent-workflow.

**Scope:**
Agent-loaded operating guidance, update documentation, and required generated skill/package copies.

**Constraints:**
Do not weaken checker gates, rewrite completed Work Records, invent baseline or review evidence, add state/schema/tooling, or change consumer repositories.

**Completion criteria:**
When updating an installed repo with an existing Work Record, the agent checks the owning task or PR's live delivery state before treating the record as active; completed records remain historical, while active work meets current gates with real evidence.

**Requirement baseline:**
{"source":"codex-user-item:e6ca50ec-6c9e-4191-89e5-8323887c4bc0","outcome":"Agent Workflow updates distinguish completed historical tasks from active work before applying current Work Record gates.","scope":"Agent-loaded operating guidance, update documentation, and required generated skill/package copies.","constraints":"Do not weaken checker gates, rewrite completed Work Records, invent baseline or review evidence, add state/schema/tooling, or change consumer repositories.","completion_criteria":"When updating an installed repo with an existing Work Record, the agent checks the owning task or PR's live delivery state before treating the record as active; completed records remain historical, while active work meets current gates with real evidence."}

**Risk:**
Elevated

**Complexity:**
Simple

**Reason:**
Agent-loaded operating guidance and generated copies are Redline gray/watch; documentation is blue. One coherent instruction change, no contract or checker change.

**Discovery:**
SPEC §9 already says Ready for review is not merged/delivered. docs/INTEGRATION.md tells updaters to preserve historical Work Records but starts its migration instructions with "in-flight branches" without requiring a live PR/task status check. docs/INTEGRATION.md explicitly routes installed-skill updates through operating mode, whose pickup rule lacks that check. A reported consumer PR was already merged; its old checkout's Ready for review marker caused an unnecessary migration stop. No applicable roadmap item remains open for this update. Current operating-mode budget is 1868/1900 tokens; package script mirrors source into dist and native installs.

**Material assumptions:**
The existing SPEC covers delivery-state truth; if the intended wording creates a new normative gate, return to planning and edit SPEC first. If package output does not mirror the source sentence, stop and inspect the packager.

**Plan:**
1. Add one concise rule at the existing operating-mode pickup point: verify the owning task/PR's live delivery state before migrating an existing Work Record; preserve completed history.
2. Clarify docs/INTEGRATION.md's installed-update procedure: completed records remain unchanged and future work starts from updated default branch with a new record; only genuinely active branches enter migration, with authoritative baseline and actual review evidence.
3. Regenerate dist/native copies; check source/package parity, token budget, links, and the full suite. Do not change checker, schema, SPEC, or consumer repos. Stop if an active-record checker defect is found.

**Verification plan:**
When an update encounters an existing Work Record, the agent checks live delivery state and does not migrate completed history → inspect operating-mode source and packaged copy plus docs/INTEGRATION.md; run budget, package/link checks, and full tests/run-all.sh.

**Plan review:**
Pending independent review.

**Approvals:**
Not required at this risk level. User authorized delivery: "Okay, so let's make sure this doesn't happen again. Do what you need to do. I approve getting it till the end."

**Exceptions:**
—

**State:** Blocked
<!-- agent-workflow:end -->

## Implementation

- 2026-09-25: Isolated branch feat/update-history-guidance from current main. Non-exempt agent-loaded guidance selected; planning/review remains before implementation. No source edit yet.
