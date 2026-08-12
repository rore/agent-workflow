# agent-workflow

A skill for AI coding agents, plus a CI checker that validates its output.

The skill makes the agent work through a defined sequence of checkpoints and write a per-task **Work Record** — a structured markdown file at `.agent-workflow/tasks/<slug>.md` capturing the state of the work as it goes. The CI checker reads the Work Record at PR time and blocks the merge if it is missing, malformed, or contradicted by the actual diff.

The goal: make AI-driven engineering work durable, reviewable, and risk-aware. A reviewer can pick up a PR and see what was decided and why; classification matches reality; the harness refuses to advance past gaps it can detect.

Just as important as enforcement is **visibility**. Most of what the harness produces — the Work Record, the risk classification, the recorded approvals, the per-PR stickies — is there to surface what the agent did to a human reviewer. A determined agent can satisfy some gates structurally without genuine human intent (a "cheating window" the harness openly acknowledges); the harness's answer is to put those acts in front of a reviewer's eyes — in the PR conversation, in their notification email — where a human can see them and push back. Enforcement catches what it can; visibility catches the rest.

Scope is the engineering-change slice — discovery → risk → plan → implement → verify → review. Product discovery, deployment, and production operation stay with the systems that already own them. This is one component in a workflow harness, not a complete harness — it composes with Jira, GitHub, and branch protection rather than replacing them.

---

## Capability map

What agent-workflow does:

- **Skill (operating mode)** — guides the agent through the checkpoint sequence and writes/updates the Work Record as it goes.
- **Skill (bootstrap mode)** — installs the harness on a new repo: config, risk-classification policy, vendored scripts, AGENTS.md reference section, per-checkpoint docs, optional CI workflow.
- **CI checker** — single-file Python script vendored per repo. At PR time, validates structural and policy predicates against every touched Work Record; posts a sticky comment; blocks merge on blocking failures.
- **Risk classifier (agent-redline)** — bundled subsystem. Maps changed paths to zones, detects boundary violations, surfaces watch-path signals. Pre-edit during the skill; PR-time as a separate CI job and sticky.
- **Surfaces what the agent did to a human** — every PR carries two stickies (classifier verdict + Work-Record verdict) plus the Work Record itself. Risk declarations, recorded approvals, satisfied checkpoints, and verification claims all land where the reviewer sees them. Visibility is a first-class output, not a side-effect of enforcement.

What agent-workflow does NOT do:

- It does not judge **plan adequacy, discovery sufficiency, test adequacy, or code correctness.** Those stay reviewer judgments.
- It does not re-run **CI tests** — GitHub already does that. The checker only reads Work Records and the classifier verdict.
- It does not prove **human identity** behind a recorded approval. It checks that approval-shaped text exists; the cheating window is acknowledged openly.
- It does not replace **branch protection, CODEOWNERS, or your reviewers.** Those remain authoritative.
- It does not currently support the **Jira Work-Record backend** — the schema reserves the shape; implementation lands with slice W18. Local Markdown backend only today.

---

## What a developer needs to know

### 1. The checkpoints

Every task walks the same sequence in order. Each checkpoint has a readiness gate; the harness refuses to advance until the gate is satisfied.

> Establish Context → Discover → Assess Risk → Plan and Review → Implement → Verify → Review the Result

The agent writes the planning fields *before* touching code. State updates at every transition. A planned stop leaves recovery state explicit (current revision, what's unfinished, what the next agent should do first). Full spec: [`docs/SPEC.md`](docs/SPEC.md) §9.

### 2. The Work Record

One file per task at `.agent-workflow/tasks/<slug>.md`. Marker-bounded markdown block; prose around the markers is human notes (Implementation, Evidence, Result-review references), structured fields go inside.

- **Slug** is derived from the branch name (strip `feat/`, `fix/`, `slice/`, `chore/`, etc.; replace remaining `/` with `-`).
- **Shape** is fixed by `(Risk, Complexity)`:
  - `(Routine, Simple)` → compact shape: Outcome, Target, Scope, Constraints, Completion criteria, Risk, Complexity, Reason, Approach, Verification, State.
  - Anything else → expanded shape with Discovery, Material assumptions, Plan, Verification plan, Plan review, Approvals.
- **State** values: `Ready to implement`, `Blocked`, `Ready for review`. Update at every transition.
- Templates: [`core/templates/work-record-routine.md`](core/templates/work-record-routine.md), [`core/templates/work-record-expanded.md`](core/templates/work-record-expanded.md).

### 3. Risk and complexity

Two independent axes — they answer different questions:

- **Risk:** `Routine` | `Elevated` | `High`. What's the structural / architectural consequence of getting this wrong? Determines required approvals and reviews.
- **Complexity:** `Simple` | `Moderate` | `Large`. How much planning and recovery state does the work itself need? Determines Work-Record shape and plan depth.

A trivial change to a contract can be `(High, Simple)`. A large refactor of test scaffolding can be `(Routine, Large)`. The two are assessed independently.

Plan-review obligation grows with risk:

- Routine → agent self-review.
- Elevated → clean-context subagent review (recorded in the Work Record).
- High → clean-context review **plus** the agent stops and waits for a verbatim human approval.

Engineering judgment may raise the declared risk above the structural minimum the classifier detected; it may not lower it.

### 4. Risk classification — zones

A bundled classification subsystem maps changed paths to zones from `agent-redline-policy.yaml`.

| Zone | Meaning | Effect |
|---|---|---|
| **Red** | Architectural decisions: contracts, modeling, security, persistence. | Raises risk; may trigger a review checkpoint. |
| **Blue** | Autonomous-safe: tests, docs, isolated/replaceable code. | No uplift. |
| **Gray** | Unclassified. | Cautious by default; surfaced in sticky. |
| **Watch** | Additive tag, not a zone — any file can carry a watch tag regardless of its zone. | Visibility only — no risk uplift, no checkpoint. |

Plus one terminal state: **Boundary violation** — forbidden cross-layer dependency. Stops the workflow before planning; never waivable through a task exception.

**Cardinal rule:** red zones trigger mandatory review checkpoints. If that checkpoint fires on every routine feature PR, reviewers stop taking it seriously and the gate dies. So red means *different review behavior*, not *important code* — if a path is in red and changes on routine work, demote it. For "important + routine" use the `watch` tag instead. Full feature set (vertical signals — API/schema/security/runtime-config, suppression detection, boundary backends, language extensions) and the policy schema: [`docs/REDLINE.md`](docs/REDLINE.md). Adoption-time tuning workflow: [`docs/INTEGRATION.md`](docs/INTEGRATION.md#risk-classification-and-how-to-keep-it-useful).

### 5. Shadow vs binding

The classifier ships with `modes.default: shadow` and `perCheck.boundary_violation: binding`. Meaning:

- Zone classification is **advisory** during the calibration window — sticky shows the verdict, CI does not block.
- Boundary violations **block from day one** — they are structural errors.

Calibration window: ~4 weeks or 30 PRs. Read the stickies during that window; demote zones that fire on routine work; tighten checkpoints that get rubber-stamped. Then flip `modes.default` to `binding` via a normal PR.

### 6. The CI checker

Single-file Python, vendored at `scripts/agent-workflow-check.py`. Runs against every Work Record the PR touched.

| Exit | Meaning | CI |
|---|---|---|
| `0` | Every predicate passed. | Green. |
| `1` | Advisory failures only. | Green; sticky surfaces the warning. |
| `2` | At least one blocking predicate failed. | Red; merge blocks if check is required. |

**What it enforces:** Work Record present and well-formed; shape matches `(Risk, Complexity)`; State value valid; declared Risk ≥ detected Risk; no boundary violations; required approvals recorded for Elevated/High; review checkpoints satisfied; exceptions well-formed.

**What it does NOT enforce:** plan quality, discovery sufficiency, test adequacy, code correctness, whether tests actually pass (GitHub already knows). Those stay reviewer judgments. Per-predicate reference: [`docs/ENFORCEMENT.md`](docs/ENFORCEMENT.md).

### 7. Local check before pushing

```bash
python scripts/agent-workflow-check.py --repo-root . --slug <slug>
```

Pipe the JSON through `scripts/format-verdict-comment.py` to see the rendered sticky.

### 8. Adopting on a new repo

The skill ships from this repo's [`dist/agent-workflow/`](dist/agent-workflow/) tree — clone the repo and copy that directory into your target repo's `.claude/skills/` (or wherever your Claude Code install loads skills from). Then open the target repo in Claude Code and ask the agent to install agent-workflow. The bootstrap is a six-phase conversation: **inspect → propose → adapt → write → confirm CI → self-summary**. You stay in the loop throughout.

- **CI integration is your explicit yes.** Bootstrap will not write `.github/workflows/agent-workflow.yml` without confirmation.
- **Branch protection and CODEOWNERS additions** are always proposal-only — bootstrap has no admin access; you apply them.
- **Phase 3 calibration** is the most valuable step. Don't skip it; the tuner against your last 30 PRs is the single best way to avoid alert fatigue.

Full walkthrough: [`docs/INTEGRATION.md`](docs/INTEGRATION.md).

### 9. Two stickies on every PR

Both refresh on every push:

- `agent-redline` — the classifier's zone verdict, boundary findings, watch-path surfacing.
- `agent-workflow` — the per-Work-Record predicate verdict.

They stay independently legible — either can be red while the other is green.

### 10. Config knobs

`agent-workflow.yaml` at the repo root:

```yaml
workRecord:
  backend: local                              # only backend today (Jira backend planned)
  local: { taskPath: ".agent-workflow/tasks/{slug}.md" }
redline: required                             # treats missing verdict as CI config error
redlineVerdictPath: build/redline-verdict.json
```

`agent-redline-policy.yaml` carries the zones, boundaries, checkpoints, PR-size thresholds, modes. This file is itself red-zone — changes go through architecture-review.

---

## See it on a real PR

A companion demo repo carries one PR per scenario, kept open as living examples. Each sticky shows how the verdict comment reads in that situation.

[**rore/agent-workflow-demo — open PRs**](https://github.com/rore/agent-workflow-demo/pulls)

---

## Where to read more

| Topic | Doc |
|---|---|
| Adopt agent-workflow on a repo, tune the risk policy, troubleshoot | [`docs/INTEGRATION.md`](docs/INTEGRATION.md) |
| Risk-classification subsystem: full feature set, policy schema, calibration | [`docs/REDLINE.md`](docs/REDLINE.md) |
| Predicate-by-predicate reference of what the CI checker blocks on | [`docs/ENFORCEMENT.md`](docs/ENFORCEMENT.md) |
| The normative spec — workflow + harness contract | [`docs/SPEC.md`](docs/SPEC.md) |
| Publishing the skill to the skill registry | [`docs/PACKAGING.md`](docs/PACKAGING.md) |
| Default profile mapping (risk triggers, GitHub, CI) | [`docs/DEFAULT_PROFILE.md`](docs/DEFAULT_PROFILE.md) |
| Working on agent-workflow itself | [`AGENTS.md`](AGENTS.md), [`CONTRIBUTING.md`](CONTRIBUTING.md) |
