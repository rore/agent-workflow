# Agent Engineering Workflow and Harness Specification

This document has two parts:

1. **Agent Engineering Workflow Specification** — the portable engineering policy.
2. **Minimum Harness Contract** — the minimum guarantees required to implement the workflow consistently.

The default profile mapping (GitHub, CI, Agent Redline) lives in [`DEFAULT_PROFILE.md`](DEFAULT_PROFILE.md).

---

# Part I: Agent Engineering Workflow Specification

## 1. Purpose and Scope

This specification defines how engineers, AI agents, reviewers, and engineering systems deliver software changes from an already-defined product requirement.

Product discovery, prioritization, feature ownership, environment provisioning, runtime security operations, and operational release management are outside its scope.

The workflow begins with an approved epic, story, or equivalent requirement and ends with a reviewed engineering change that has the required pre-merge evidence and approvals.

The workflow is:

**Establish Task Context → Discover → Assess Risk and Complexity → Plan and Review → Implement Within Approved Scope → Verify → Review**

Every change **MUST** satisfy the purpose and gate of each checkpoint. This does not require a separate document or ceremony for every checkpoint.

Routine work **SHOULD** use a compact fast path. Higher-risk or more complex work requires stronger planning, review, verification, and recovery state.

When validation can occur only after merge or deployment, the engineering task **MUST** identify a responsible owner and linked follow-up. The operational validation lifecycle remains outside this workflow.

## 2. Normative Language

- **MUST / MUST NOT:** mandatory
- **SHOULD / SHOULD NOT:** expected unless a justified exception exists
- **MAY:** optional

## 3. Roles

### Human Engineer

Owns technical intent, resolves material ambiguity, makes or approves important technical decisions, accepts exceptions, and remains accountable for the result.

### AI Agent

Investigates the current system, proposes an approach, implements the change, runs verification, and maintains durable work state.

The agent role may be fulfilled by one agent or by a coordinated set of agents. The workflow does not prescribe the orchestration model.

### Reviewer

Evaluates a proposed plan or completed result.

A **clean-context agent review** is performed without the implementation conversation. It reduces anchoring, but it is not an independent assurance mechanism.

A **separate human review** provides independent judgment. Specialist review may be required for high-risk changes.

An AI review **MUST NOT** replace human review required by repository, organizational, security, or compliance policy.

### Harness

Guides the workflow, maintains the Work Record, applies effective rules, surfaces risk and policy findings, invokes deterministic checks, and prevents invalid transitions where technical enforcement exists.

## 4. Core Principles

### Engineering Starts from Product Intent

Engineering **MUST** escalate requirements that are contradictory, infeasible, unsafe, or materially ambiguous rather than silently reinterpret product intent.

### Human Accountability

Agents may investigate, propose, implement, and verify. Human engineers remain accountable for material decisions, accepted risk, and the delivered result.

### Durable State Over Chat

Work **MUST** remain understandable and resumable outside the current agent session. Chat history is temporary context, not an authoritative record.

### Evidence Over Confidence

Completion claims **MUST** be supported by evidence appropriate to the claim.

### Risk-Adaptive Control

Routine work **SHOULD** remain lightweight. Stronger controls **MUST** be applied when justified by risk or complexity.

### Keep It Simple

The workflow **SHOULD** reuse existing engineering systems and artifacts. New process, configuration, or tooling **SHOULD** be added only when it solves a demonstrated problem.

### Artifact Proportionality

A task **MUST** update durable product, architecture, contract, decision, or operational documentation when the change materially affects what that documentation describes.

It **MUST NOT** create or update artifacts merely to satisfy a uniform document sequence.

Existing authoritative artifacts **SHOULD** be referenced rather than restated.

## 5. Control Model

### Judgment Boundary

The harness does not decide whether the work is correct; it enforces objective workflow gates and surfaces judgment-heavy risks for review.

It does not validate plan quality, discovery sufficiency, implementation correctness, or evidence adequacy. It surfaces those for reviewer judgment. What the harness can enforce is that the structural artifacts the workflow requires — context, classification, plan, approvals, verification-method references, recovery state — are present, well-formed, and consistent with each other.

Passing CI does not by itself prove that the selected checks are sufficient. The Verification Record (§13.3) is a structured claim that reviewers can challenge, not proof in itself. Adequacy of the chosen verification method remains a review judgment unless the repository defines a deterministic evaluator for the criterion.

### Gates

Workflow gates define the conditions for advancing between checkpoints.

The workflow skill **SHOULD** prevent the agent from advancing when required information is missing. Human review validates judgment-based gates. Automated tools detect objective risks and violations. CI and repository policy enforce deterministic requirements where technical enforcement is available.

A normative requirement does not imply that every violation can be mechanically blocked.

The implementation **MUST** distinguish between:

- **Guidance:** behavior requested from the agent
- **Detection:** risks or violations reported
- **Enforcement:** actions technically prevented

A requirement **MUST NOT** be described as enforced unless a technical control blocks its violation.

## 6. Work Record

Every engineering task **MUST** have one canonical Work Record.

The Work Record is an index and decision log. It stores workflow state and material decisions and links to authoritative evidence in Jira, source control, CI, or other engineering systems.

The Work Record **MUST NOT** manually duplicate information that can be resolved reliably from an authoritative system.

Chat history **MUST NOT** be the only source of required task state.

The Work Record **MUST** expose, as applicable:

- Task Context
- risk and complexity decision
- material discoveries, assumptions, and decisions
- plan and Verification Plan
- required approvals and review results
- implementation reference
- verification evidence
- blockers, next action, and exceptions
- linked external follow-up, when required

When an agent stops before completing a task, the Work Record **MUST** identify:

- last completed step
- current branch, workspace, or revision
- unfinished work
- known failures or blockers
- next required action

For Moderate and Large tasks, the Work Record **MUST** be updated at checkpoint transitions, after material decisions or deviations, and before session end or handoff.

A new engineer or agent **MUST** be able to resume the work from the Work Record and linked artifacts.

There **MUST NOT** be multiple competing sources of truth.

## 7. Routine Fast Path

Routine, simple work **MAY** use one compact record rather than separate artifacts for each checkpoint.

The compact record **MUST** contain:

- outcome and scope
- risk classification and reason
- proposed approach
- verification method
- current readiness state or blocker

For routine work, an issue-tracker task or equivalent **MAY** serve as the complete Work Record. No separate Markdown file is required.

The minimum readiness states are:

- **Ready to implement**
- **Blocked or returned to planning**
- **Ready for review**

Git and GitHub remain authoritative for implementation, pull-request, CI, approval, and merge state.

Example:

```text
Outcome and scope:
Fix retry handling in WalletService. No public API changes.

Risk:
Routine. Localized and reversible; no sensitive surfaces detected.

Approach:
Reuse the existing retry utility and add a regression test.

Verification:
New regression test plus existing wallet-service CI.

State:
Ready to implement.
```

## 8. Risk and Complexity Model

Risk and complexity are assessed separately.

Risk determines required approvals, reviews, verification, and workflow restrictions.

Complexity determines planning depth, task decomposition, and recovery-state requirements.

### 8.1 Risk Levels

#### Routine

A localized and reversible change that does not touch known sensitive surfaces.

Typical controls:

- compact plan
- agent self-review may be sufficient
- standard verification
- normal pull-request review

#### Elevated

A change with meaningful behavioral impact, uncertainty, or sensitive surfaces.

Typical controls:

- explicit discovery and Verification Plan
- clean-context plan review
- additional risk-specific checks
- separate result review

#### High

A change where failure could materially affect security, tenant isolation, financial integrity, public compatibility, irreversible state, production operation, or regulatory obligations.

Typical controls:

- human-approved plan
- separate human result review
- specialist expertise where required
- explicit assumptions, invalidation conditions, and stop conditions

#### Boundary Violation

A prohibited, unauthorized, or policy-violating change.

A boundary violation **MUST** stop the workflow.

A boundary-violation finding **MUST NOT** be waived in place. If the underlying action should become permitted, the governing policy must be changed through its own reviewed change, after which the original change is reassessed.

### 8.2 Complexity Levels

#### Simple

One coherent change, normally in one repository, likely to complete in one working session.

#### Moderate

Several affected components, meaningful uncertainty, or likely work across multiple sessions.

The Work Record and recovery state **MUST** be explicit.

#### Large

Multiple repositories, services, delivery units, agents, or independently verifiable outcomes.

The work **SHOULD** be decomposed into linked delivery tasks under a parent engineering record.

Each delivery task **SHOULD** be independently verifiable — it delivers a working slice of the outcome rather than a layer of the implementation. Decomposition by layer (all persistence tasks first, then all service layer, then all API) produces tasks that cannot be verified until other layers exist, defeating the purpose of decomposition for review and recovery.

### 8.3 Reassessment

Risk and complexity **MUST** be reassessed:

- when scope materially changes
- when an important assumption fails
- when new affected surfaces are discovered
- before merge, using the actual final diff

Newly detected risk **MUST** trigger the required checks, approvals, and reviews.

Automated findings **SHOULD** contribute where reliable rules exist, but **MUST NOT** replace engineering judgment about impact, uncertainty, or task coherence.

## 9. Workflow Checkpoints

### 9.1 Establish Task Context

**Why:** Agents fill gaps confidently. Clear context prevents them from inventing the intended outcome, scope, or definition of done.

Before planning or implementation, engineering **MUST** record:

- **Outcome:** what should be true when complete
- **Target:** affected system, service, or repository
- **Scope:** what may change
- **Constraints:** what must not change or must remain true
- **Completion criteria:** observable outcomes that demonstrate success

Task Context **SHOULD** normally fit in 5 to 10 lines and **MUST NOT** prescribe the implementation approach.

Bad completion criterion:

```text
Add an idempotency table.
```

Good completion criterion:

```text
Concurrent retries create only one wallet.
```

The initial context **MUST** be sufficient to begin focused discovery. It **MAY** be refined during discovery.

**Gate:** Planning and implementation **MUST NOT** begin while the outcome, scope, constraints, or completion criteria remain materially unclear.

### 9.2 Discover Current State

**Why:** Plans based on assumptions or stale knowledge often solve the wrong problem or break existing behavior.

Before planning, the agent **MUST** inspect the relevant current system.

Focused discovery normally includes:

- affected code and tests
- repository guidance
- interfaces and schemas
- recent related changes
- relevant design decisions
- existing verification commands and CI checks
- logs, incidents, or other evidence when relevant

The agent **MUST** record only material findings:

- current behavior and relevant components
- constraints and dependencies
- verification capabilities and gaps
- unanswered questions or assumptions
- references to inspected evidence

Discovery **MUST NOT** become an open-ended documentation exercise.

When repository guidance, durable documentation, requirements, and observed system behavior disagree on a material point, the agent **MUST** identify which source is authoritative for that kind of question and resolve the disagreement, or record it as an explicit assumption with a validation condition, before planning proceeds. A disagreement is material when it would change scope, approach, completion criteria, or risk classification.

**Gate:** Planning **MUST NOT** proceed while a material uncertainty is neither verified nor recorded as an assumption with a validation or invalidation condition.

### 9.3 Assess Risk and Complexity

**Why:** Risk determines required control and validation. Complexity determines planning, decomposition, and recovery needs.

Before detailed planning or implementation, the task **MUST** receive an initial Risk and Complexity Decision using the shared model and effective group or repository rules.

The decision **MUST** record:

- risk level and reasons
- complexity level and reasons
- triggered rules
- required approvals and reviews
- required verification
- required workflow restrictions
- whether decomposition is required

**Gate:** Detailed planning or implementation **MUST NOT** proceed until the workflow path and task structure are known.

### 9.4 Plan and Review the Change

**Why:** Reviewing the approach before coding exposes hidden assumptions, missing failure cases, and unsafe decisions while they remain cheap to change.

For routine work, the plan **MAY** be a short description of:

- proposed approach
- affected surfaces
- required verification

The plan **MUST** identify any durable product, architecture, contract, decision, or operational documentation that requires updating. No documentation update is required when the existing authoritative artifacts remain accurate.

For elevated, high-risk, or complex work, the plan **MUST** also include:

- material assumptions
- unresolved decisions
- implementation sequence or delivery-task breakdown
- deviations from existing architecture or conventions
- stop conditions

For elevated and high-risk work, each material assumption **MUST** state:

- what evidence would disprove it
- what action follows if it is disproved

Example:

```text
Assumption:
The existing request identifier is stable across retries.

Disproving evidence:
Retry requests receive different identifiers.

Action:
Stop implementation and return to planning.
```

#### Verification Plan

The plan **MUST** connect each completion criterion and significant risk to a verification method.

For routine work, the Verification Plan **MAY** be one sentence or a short checklist.

Existing CI checks are sufficient only when they directly verify the completion criteria and relevant risks.

Verification evidence and result review **MUST** identify the revision evaluated. Changes made after verification or review **MUST** cause the affected evidence and findings to be re-evaluated before acceptance.

Example:

```text
Completion criterion:
Concurrent retries create one wallet.

Verification method:
Concurrency integration test.

Authoritative result:
wallet-service CI job for the final revision.
```

The Verification Plan **MAY** evolve during implementation. Removing or weakening required verification **MUST** receive the required approval.

Plan review or approval **MUST** be repeated only when scope, assumptions, approach, or risk materially change.

#### Plan Review

- **Routine:** agent self-review may be sufficient
- **Elevated:** clean-context agent review **SHOULD** be used
- **High:** a human reviewer **MUST** review the plan, and material decisions **MUST** receive human approval

Required approvals **MUST** be recorded in the Work Record before implementation begins.

**Gate:** Implementation **MUST NOT** begin until required reviews are complete, approvals are recorded, and blocking findings are resolved.

### 9.5 Implement Within Approved Scope

**Why:** Implementation may drift beyond approved scope, invalidate the plan, or become difficult to resume safely.

The agent **MUST** implement the approved plan in a dedicated version-controlled branch or equivalent task workspace based on a known revision.

During implementation, the agent **MUST**:

- remain within approved scope
- avoid unrelated refactoring
- create or update planned tests and checks
- record material decisions and deviations
- keep recovery state current
- pause when an assumption fails or material scope expansion is required
- stop when a boundary violation is detected

Material scope expansion **MUST** return the task to context, risk, and planning review before the expanded work continues.

The harness **SHOULD** detect prohibited or out-of-scope changes where technically possible.

**Gate:** Work **MUST** return to planning or human review when it materially diverges from the approved plan or scope.

### 9.6 Verify the Change

**Why:** Passing available tests does not prove correctness unless the evidence covers the intended outcome and relevant risks.

The agent **MUST** run the applicable pre-merge Verification Plan.

Evidence **MUST** identify:

- completion criterion or risk being verified
- check or observation
- result
- code revision tested
- authoritative result reference
- failures, skipped checks, or approved exceptions

A failed or unavailable required check **MUST NOT** be presented as success.

Bug fixes **SHOULD** include a regression test that fails before the fix when practical.

Local verification provides fast feedback. CI is authoritative for automated merge requirements.

**Gate:** Review may begin while verification is still in progress. The result **MUST NOT** be approved or accepted until every required pre-merge criterion has sufficient evidence or an explicitly approved exception.

### 9.7 Review the Result

**Why:** The implementing agent is biased toward its own solution and **MUST NOT** be the sole authority that declares the work complete.

The reviewer **MUST** evaluate:

- Task Context
- approved plan
- Risk and Complexity Decision
- Verification Plan
- final diff
- verification evidence

The review **MUST** check:

- whether completion criteria are satisfied
- whether the recorded verification methods are adequate to the criterion they cover (the harness cannot judge this; it falls to the reviewer)
- whether evidence is sufficient
- whether scope expanded unintentionally
- whether assumptions remain unresolved
- whether important security, compatibility, architecture, or operational risks were missed
- whether the final diff changes the risk classification

Review depth depends on risk:

- **Routine:** normal pull-request review may be sufficient; reviewer judges verification adequacy as part of normal review.
- **Elevated:** result review **MUST** be performed by someone other than the implementing agent. The reviewer **MAY** be a human or a clean-context agent, subject to repository and organizational policy. The reviewer **MUST** assess whether the recorded Verification Record is adequate to the criterion. Human review remains mandatory where required by policy or by the affected risk surface.
- **High:** a separate human reviewer **MUST** review the result, with specialist expertise where necessary. Verification adequacy assessment is part of the specialist review obligation.

**Gate:** The change **MUST NOT** be accepted while blocking findings remain unresolved or unapproved.

## 10. Parent Features and Delivery Tasks

Large work **MAY** use a parent engineering record linked to the product epic or story.

Delivery tasks inherit shared context, constraints, decisions, and risk rules from the parent by reference.

Each delivery task **MUST** record only:

- its own scope and completion criteria
- additional discoveries or assumptions
- risk differences
- implementation plan
- verification evidence
- review result

A child task **MUST NOT** silently contradict inherited decisions. A required deviation **MUST** be recorded and approved at the appropriate level.

A small, coherent feature **SHOULD NOT** create a separate parent record.

## 11. Extension and Exception Model

The portable workflow defines minimum guarantees.

Groups and repositories **MAY** define:

- Work Record location
- repository guidance
- risk and complexity triggers
- required verification
- reviewers and approvals
- workflow restrictions

Extensions **MAY** strengthen requirements. They **MUST NOT** silently weaken them.

Rule composition works as follows:

- **Additive requirements:** apply their union
- **Ordered requirements:** apply the stricter value
- **Contradictory requirements:** block until resolved

A task exception **MUST** record:

- rule being waived
- reason and scope
- approver
- expiry, where relevant
- compensating validation

Boundary-violation findings are not waivable through task exceptions.

---

# Part II: Minimum Harness Contract

## 12. Purpose

This contract defines the minimum guarantees required to implement Part I consistently.

A conforming harness does not need a custom workflow engine, dedicated database, or fixed storage schema. It may use existing Jira, source-control, CI, and repository-policy systems.

## 13. Required Guarantees

A conforming harness **MUST** provide the following guarantees.

### 13.1 Canonical Work Record

The harness **MUST** maintain or update one canonical Work Record that exposes:

- current readiness state
- Task Context
- risk and complexity decision
- material assumptions and decisions
- required approvals and review results
- completion-criterion-to-verification mappings
- implementation reference
- blockers, next action, and exceptions
- linked external follow-up and responsible owner, when required

The record may link to distributed authoritative artifacts.

The harness **MUST** expose the effective rules and their core, group, repository, or exception source.

### 13.2 Readiness Validation

In this contract, **readiness** means the objective state of the Work Record, evidence, approvals, policy signals, and findings — not correctness or quality. A task is ready when the structural artifacts the workflow requires are present, well-formed, and consistent with each other; whether those artifacts describe a sound plan or sufficient evidence is a reviewer judgment outside the harness's scope (see §5 Judgment Boundary).

The harness **MUST** validate readiness for:

- **implementation**
- **review**

Readiness for review **MUST** include reassessment of risk and complexity against the actual implementation diff. Newly triggered controls **MUST** be applied before the task is considered ready for review.

For routine work, the Work Record may expose only:

- Ready to implement
- Blocked
- Ready for review

GitHub or equivalent linked systems may provide implementation and completion state.

### 13.3 Verification Record

Every completion criterion and significant risk **MUST** identify a verification method. The Work Record **MUST** reference the resulting check, observation, or approval as a Verification Record carrying:

- the criterion or risk
- the verification method
- the current status
- an authoritative result reference
- the revision tested
- optional rationale

The harness validates the **presence and structural well-formedness** of the Verification Record's mapping — that each completion criterion is paired with a named method, that the field's grammar parses, that fields aren't empty. It does **not** validate the **content** of the evidence: whether the named check actually proves the criterion, whether a referenced result is fresh against the PR head, or whether a recorded status reflects a passing run, are all reviewer judgment outside the harness's scope per §5. A repository **MAY** define a deterministic evaluator for a specific criterion if it wants to move some of that judgment back inside the harness for that one criterion; absent such an evaluator, adequacy assessment stays with the reviewer.

A generic “CI passed” statement is insufficient unless the referenced CI checks directly cover the criterion or risk. Passing CI does not by itself prove that the selected checks are sufficient.

For Elevated and High work, the result reviewer **MUST** assess whether the proposed Verification Record is adequate to the criterion. This is a review obligation, not a harness gate.

### 13.4 Findings, Checkpoints, and Approvals

The harness **MUST** preserve:

- finding or rule identity
- advisory or blocking disposition
- explanation and affected scope
- checkpoint evidence
- required approvals
- exception references

Checkpoint satisfaction and human approval **MUST** remain distinct.

A clean-context agent review **MUST NOT** satisfy a human-approval requirement.

### 13.5 Missing Evidence, Unavailable Systems, and Resumability

When required evidence, approval, or policy evaluation is unavailable, the affected gate remains unsatisfied.

A fallback may be used only when the implementation profile explicitly defines it.

The harness **MUST NOT** convert unavailable evidence into a passing result.

When work stops before it is ready for review, the harness **MUST** preserve the current implementation reference, unfinished work, known blockers or failures, and next required action.

## 14. Rule and Finding Semantics

Automated tools may produce their own native output formats. The harness only requires equivalent access to:

- rule or finding ID
- category
- advisory or blocking disposition
- explanation
- affected paths or evidence
- required response, when applicable

Blocking findings **MUST** prevent the affected transition until resolved.

Advisory findings **MUST** remain visible to the agent and reviewer.

A boundary-violation finding **MUST** block until the structure is fixed or the governing policy is changed through its own reviewed change.

## 15. Conformance

A harness conforms when an authorized reviewer can determine from the Work Record and linked systems:

- whether the task is ready for implementation or review
- which effective rules apply
- which findings are unresolved
- which approvals are required and recorded
- how completion criteria map to verification methods
- whether the task may advance

A conforming harness **SHOULD**:

- keep routine records compact
- derive references from authoritative systems where possible
- avoid copying evidence
- automate deterministic checks

The harness **MUST NOT** require a complex state machine when these guarantees can be provided through existing systems and a small workflow skill.
