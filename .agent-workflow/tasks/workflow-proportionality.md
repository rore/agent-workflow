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
Pending repository discovery.

**Material assumptions:**
Pending discovery.

**Plan:**
Pending discovery and clean-context review.

**Verification plan:**
Pending discovery.

**Plan review:**
Pending clean-context review.

**Approvals:**
Pending human plan approval.

**Exceptions:**
—

**State:** Blocked
<!-- agent-workflow:end -->

## Implementation

- 2026-09-25: Established this record before discovery or implementation. Isolated branch `feat/workflow-proportionality`; awaiting plan and approval.
