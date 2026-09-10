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

## The Work Record

The central artifact: one file per task at `.agent-workflow/tasks/<slug>.md`, committed with the code and updated as work proceeds. A simplified example:

```md
Outcome: Fix retry handling in WalletService — a transient failure retries once, not in a loop
Target: wallet-service
Scope: the retry path and its tests; no public API or schema change
Constraints: public API and tenant isolation unchanged
Completion criteria: a transient failure produces a single retry
Risk: Routine
Complexity: Simple
Approach: reuse the existing retry utility; add a regression test
Verification: WalletRetryTest + existing wallet-service CI
State: Ready to implement
```

Its shape is fixed by `(Risk, Complexity)`: this compact form for `(Routine, Simple)` work, an expanded form (adding discovery, material assumptions, plan review, approvals) for everything else. Templates: [`core/templates/work-record-routine.md`](core/templates/work-record-routine.md), [`core/templates/work-record-expanded.md`](core/templates/work-record-expanded.md). The backend is a local Markdown file today; a Jira backend is reserved in the schema but not implemented.

## Quick start

The workflow model and CI checker are agent-independent; the checker is a single-file Python script that reads repository files. The packaged skill currently targets Claude Code / Agent Skills–compatible environments under `.claude/skills/`. Claude Code hooks add plan-mode enforcement, and bootstrap also installs an OpenCode plugin.

Adopt agent-workflow on a repo:

```text
1. Clone agent-workflow.
2. Copy dist/agent-workflow/ into your repo's .claude/skills/.
3. Open your repo in Claude Code.
4. Ask: "Install agent-workflow on this repo."
5. Review the integration PR it proposes.
```

Step 4 runs a six-phase bootstrap conversation — inspect, propose, adapt, write, confirm CI, self-summary — and you stay in the loop throughout. Bootstrap asks before installing the CI workflow; branch-protection and CODEOWNERS changes are proposal-only — you apply them yourself. Full walkthrough: [`docs/INTEGRATION.md`](docs/INTEGRATION.md).

**OpenCode.** Bootstrap installs [`core/skill/opencode/agent-workflow.mjs`](core/skill/opencode/agent-workflow.mjs) at `.opencode/plugins/agent-workflow.mjs`. OpenCode auto-loads it and injects a Work Record reminder each turn. The CI checker remains the enforcer.

## What CI enforces

The checker reads the Work Record and the classifier's verdict — it does not re-run your tests. It fails CI on blocking violations (and blocks merge where configured as a required check):

- The Work Record exists, is well-formed, and its shape matches its `(Risk, Complexity)`.
- Declared risk is not below what the classifier detected on the diff.
- No architectural-boundary violation.
- Required reviews/approvals are recorded for Elevated/High work. (Once the classifier is in binding mode, any triggered review checkpoint must also be satisfied.)
- State is valid and recorded exceptions are well-formed.

Per-predicate reference: [`docs/ENFORCEMENT.md`](docs/ENFORCEMENT.md).

## What it deliberately can't prove

By design — these stay reviewer judgments the checker never touches:

- Whether the plan is sound, discovery thorough, or the code correct.
- Whether the chosen verification method actually proves the criterion.
- Whether the tests pass — GitHub already knows that.
- Whether a human genuinely approved. The checker confirms approval-shaped text exists, not who wrote it; this "cheating window" is acknowledged openly. Its answer is visibility — the recorded approvals, classifications, and claims land in the PR conversation and the reviewer's notification, where a human can see them and object.

## Evidence from use

On an internal repository, agent-workflow has governed its own development across dozens of pull requests, and it has since been used on real application code in another project. In that use it has surfaced correctness, scope, verification, and risk issues before merge — in some cases changing the engineering decision, not just documenting it. The signal isn't any single review step but the combination: risk decides when stronger review is required, findings and decisions are preserved in the Work Record, and CI independently checks the agent's declarations against the final diff. This isn't yet evidence of lower defect rates or ROI — it's evidence the workflow acts as an engineering control rather than just producing paperwork.

## Documentation

| Topic | Doc |
|---|---|
| Adopt on a repo, tune the risk policy, troubleshoot | [`docs/INTEGRATION.md`](docs/INTEGRATION.md) |
| Risk classification: feature set, policy schema, calibration | [`docs/REDLINE.md`](docs/REDLINE.md) |
| Predicate-by-predicate reference of what CI blocks on | [`docs/ENFORCEMENT.md`](docs/ENFORCEMENT.md) |
| The normative workflow + harness contract | [`docs/SPEC.md`](docs/SPEC.md) |
| Default profile mapping (risk triggers, GitHub, CI) | [`docs/DEFAULT_PROFILE.md`](docs/DEFAULT_PROFILE.md) |
| Publishing the skill | [`docs/PACKAGING.md`](docs/PACKAGING.md) |
| Working on agent-workflow itself | [`AGENTS.md`](AGENTS.md), [`CONTRIBUTING.md`](CONTRIBUTING.md) |
