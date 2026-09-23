# agent-workflow

**A risk-aware, enforceable engineering workflow around AI coding agents.**

agent-workflow makes agent work inspectable outside the chat. It guides each task through a fixed sequence of checkpoints — establish context, discover, assess risk, plan, implement, verify, review — and records scope, assumptions, risk classification, and verification in a per-task **Work Record** committed alongside the code.

At PR time, CI classifies the actual diff, checks it against the Work Record, and fails on objective violations. Judgment stays with people: higher-risk changes are surfaced with the context and required checkpoints reviewers need, while routine changes do not demand the same attention.

It covers the change itself — from discovery through review. Product discovery, deployment, and production operation stay with the systems that already own them; agent-workflow composes with GitHub, CI, and branch protection rather than replacing them.

> Part of the [Rore collection](https://github.com/rore/rore-collection): three local tools for developers working with coding agents.

---

## The problem

Agents produce code quickly, but the reasoning behind it — what was decided, what was assumed, what was actually verified — lives in a chat log that disappears. A reviewer inherits a diff with no durable record of scope or risk. A stalled task is hard for the next agent (or human) to resume. And "the tests pass" quietly becomes "this is correct."

agent-workflow makes that state durable, uses risk to focus reviewer attention, and puts objective guardrails at the pull request.

## What you get

- **Durable task state** — scope, assumptions, decisions, and verification live in the committed Work Record, so work can be reviewed and resumed rather than lost in a chat log.
- **Behavioral integrity** — the Work Record preserves the requirements implementation started with, and selected behavior-contract paths stay red, classified, and linked to PR verification. Requirement changes also need approval under the selected protection—even in solo repositories without CODEOWNERS or branch protection.
- **Risk-aware visibility** — the risk classification decides where a reviewer's attention goes, and what the agent decided and verified is on the record.
- **Objective CI gates** — mechanically detectable violations fail CI, so they don't depend on the agent reporting itself correctly.

## Risk-aware workflow

Risk and complexity are assessed separately:

- **Risk** — `Routine` / `Elevated` / `High`: how bad is it if this change is wrong? It determines required approvals and reviews, focusing human attention on the PRs and files with the highest blast radius.
- **Complexity** — `Simple` / `Moderate` / `Large`: how much planning and recovery state does the work need? It determines the Work Record's shape.

A one-line contract change can therefore be `(High, Simple)`.

The bundled classifier, [`agent-redline`](https://github.com/rore/agent-redline), maps changed paths to zones: red for structural decisions, blue for autonomous-safe work, and gray for unclassified work. Watch paths add visibility without adding a gate. During planning, the skill assesses the intended scope against repository policy. At PR time, CI independently classifies the actual diff and posts the classified files and required checkpoints, giving reviewers a prioritized attention queue. Human review remains the authority for judgments CI cannot prove.

Zone classification starts in **shadow** mode — advisory in the PR, not blocking — so teams can calibrate it against their own changes before making it binding. Forbidden cross-layer dependency violations block from day one. Feature set, policy schema, and calibration: [`docs/REDLINE.md`](docs/REDLINE.md).

## How it works

```
developer request
  → agent works the checkpoints, writing the Work Record as it goes
    → PR (Work Record committed with the code)
      → CI: classify the diff, check it against the Work Record, post two comments
        → human review
```

- **During development** — the skill walks the agent through the checkpoint sequence and writes/updates the Work Record. Planning fields go in *before* any code.
- **At PR time** — CI compares the classified diff against the Work Record, enforces objective workflow rules, and posts the results for reviewers.

The checkpoints, in order:

> Establish Context → Discover → Assess Risk → Plan and Review → Implement → Verify → Review the Result

Each checkpoint has a readiness gate; the skill requires the agent to satisfy it before advancing, and CI independently enforces the subset it can verify. Full spec: [`docs/SPEC.md`](docs/SPEC.md).

## Protecting intended behavior

An agent can produce a green change by quietly changing the promise: narrowing scope, weakening completion criteria, or editing a regression test to accept less. agent-workflow protects against both forms of drift:

| Protection | What is preserved | What happens when it changes |
|---|---|---|
| **Task requirements** | The Outcome, Scope, Constraints, and Completion criteria that implementation started with. | The agent records the exact before/after meaning. A real requirement change needs explicit task-owner approval; otherwise the task stays blocked. |
| **Repository behavior contracts** | Selected acceptance, contract, E2E, or regression paths declared in Agent Redline and exercised by a named PR check. | Redline treats the path as red and Agent Workflow requires semantic classification plus verification linkage. For requirement changes, choose repository protection for CODEOWNERS/branch-enforced approval, or workflow protection for explicit task-owner approval without claiming merge enforcement. |

This does not make requirements or tests immutable. Equivalent rewrites and coverage improvements remain possible and visible. Product obligations may change too, but only as an explicit, approved decision—not as an implementation shortcut.

For example, if a task promises delivery while a recipient is offline but the implementation can only deliver after the recipient restarts, the agent cannot silently rewrite the completion criteria or weaken the protected test. It must propose the exact requirement change and remain blocked until the appropriate owner approves it.

Developer guide: [`docs/BEHAVIORAL_INTEGRITY.md`](docs/BEHAVIORAL_INTEGRITY.md).

## The Work Record

The central artifact: one file per task at `.agent-workflow/tasks/<slug>.md`, committed with the code and updated as work proceeds. A simplified example:

```md
Outcome: Fix retry handling in WalletService — a transient failure retries once, not in a loop
Target: wallet-service
Scope: the retry path and its tests; no public API or schema change
Constraints: public API and tenant isolation unchanged
Completion criteria: a transient failure produces a single retry
Requirement baseline: {"source":"work-record-initial","outcome":"Fix retry handling in WalletService — a transient failure retries once, not in a loop","scope":"the retry path and its tests; no public API or schema change","constraints":"public API and tenant isolation unchanged","completion_criteria":"a transient failure produces a single retry"}
Risk: Routine
Complexity: Simple
Approach: reuse the existing retry utility; add a regression test
Verification: WalletRetryTest + existing wallet-service CI
State: Ready to implement
```

Its shape is fixed by `(Risk, Complexity)`: this compact form for `(Routine, Simple)` work, an expanded form (adding discovery, material assumptions, plan review, approvals) for everything else. Templates: [`core/templates/work-record-routine.md`](core/templates/work-record-routine.md), [`core/templates/work-record-expanded.md`](core/templates/work-record-expanded.md). The backend is a local Markdown file today; a Jira backend is reserved in the schema but not implemented.

## Quick start

Claude Code, Codex, and stable OpenCode 1.x install the same skill, applicability-first seed, and shared checker-backed evaluator. Native mutation coverage is version-, execution-surface-, and tool-specific: verification requires an observed denial with an unchanged target. Shell mutations and unverified native paths are degraded; PR CI remains authoritative for final artifacts and applicability. OpenCode 2 beta is excluded.

Adopt agent-workflow on a repo:

```text
1. Clone agent-workflow.
2. Copy dist/agent-workflow/ identically into your repo's `.claude/skills/agent-workflow/` and `.agents/skills/agent-workflow/`.
3. Open the repo in Claude Code, Codex, or stable OpenCode 1.x.
4. Ask: "Install agent-workflow on this repo."
5. Review the integration PR it proposes.
```

Step 4 runs a six-phase bootstrap conversation — inspect, propose, adapt, write, confirm CI, self-summary — and you stay in the loop throughout. For behavior contracts, bootstrap explains repository versus workflow protection and asks you to choose; it never silently downgrades. Bootstrap also asks before installing the CI workflow, while branch-protection and CODEOWNERS changes remain proposal-only — you apply them yourself. Full walkthrough: [`docs/INTEGRATION.md`](docs/INTEGRATION.md).

**Runtime limits.** OpenCode 1.x plugin callback loading and denial are tested, but the existing evidence does not record an exact runtime version, native tool, and unchanged target, so native coverage is degraded under this standard. On the tested Windows host, Codex 0.153.4 desktop `apply_patch` did not enter `PreToolUse`; CLI `bypassPermissions` entered the hook but ignored its exit-2 denial. Claude Code's seed ran, but mutation denial could not be tested because its API credential was unavailable to the CLI process. Treat every unverified runtime/version/surface/tool combination as degraded. Installed or trusted hooks and direct evaluator tests do not prove interception; CI remains authoritative.

## What CI enforces

The checker reads the Work Record and the classifier's verdict — it does not re-run your tests. It fails CI on blocking violations (and blocks merge where configured as a required check):

- The Work Record exists, is well-formed, and its shape matches its `(Risk, Complexity)`.
- Its Requirement baseline and any ordered Behavior changes are complete, consistent, and authorized.
- Every changed configured behavior-contract path is classified; each `requirement-change` is approved under its selected protection mode; at least one affected Work Record references its PR verification identifier.
- Declared risk is not below what the classifier detected on the diff.
- No architectural-boundary violation.
- Required reviews/approvals are recorded for Elevated/High work. (Once the classifier is in binding mode, any triggered review checkpoint must also be satisfied.)
- State is valid and recorded exceptions are well-formed.

Per-predicate reference: [`docs/ENFORCEMENT.md`](docs/ENFORCEMENT.md).

## What it deliberately can't prove

By design — these stay reviewer judgments the checker never touches:

- Whether the plan is sound, discovery thorough, or the code correct.
- Whether the chosen verification method actually proves the criterion.
- Whether a behavior-change classification is semantically honest or the stored baseline was never rewritten.
- Whether a configured contract check is actually required or passed; bootstrap/review validates required-check status and CI reports execution.
- Whether the tests pass — GitHub already knows that.
- Whether a human genuinely approved. The checker confirms approval-shaped text exists, not who wrote it; this "cheating window" is acknowledged openly. Its answer is visibility — the recorded approvals, classifications, and claims land in the PR conversation and the reviewer's notification, where a human can see them and object.

## Evidence from use

Agent-workflow has now governed its own development and substantial development in Pallium across many pull requests. In our use, it has repeatedly surfaced correctness, scope, verification, and risk issues before merge — sometimes changing the engineering decision, not just documenting it. The strongest signal remains the combination: risk determines when stronger review is required, findings and decisions survive in the Work Record, and CI checks the agent's declarations against the final change. That is not evidence of lower defect rates or ROI, but it is evidence that the workflow changes how work is planned, reviewed, and completed rather than merely adding paperwork.

## Documentation

| Topic | Doc |
|---|---|
| Adopt on a repo, tune the risk policy, troubleshoot | [`docs/INTEGRATION.md`](docs/INTEGRATION.md) |
| Risk classification: feature set, policy schema, calibration | [`docs/REDLINE.md`](docs/REDLINE.md) |
| Predicate-by-predicate reference of what CI blocks on | [`docs/ENFORCEMENT.md`](docs/ENFORCEMENT.md) |
| The normative workflow + harness contract | [`docs/SPEC.md`](docs/SPEC.md) |
| Default profile mapping (risk triggers, GitHub, CI) | [`docs/DEFAULT_PROFILE.md`](docs/DEFAULT_PROFILE.md) |
| Why and how requirements and behavior contracts are protected | [`docs/BEHAVIORAL_INTEGRITY.md`](docs/BEHAVIORAL_INTEGRITY.md) |
| Publishing the skill | [`docs/PACKAGING.md`](docs/PACKAGING.md) |
| Working on agent-workflow itself | [`AGENTS.md`](AGENTS.md), [`CONTRIBUTING.md`](CONTRIBUTING.md) |
