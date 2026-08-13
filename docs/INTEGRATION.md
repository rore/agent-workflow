# Integrating agent-workflow into a repo

This is the guide for adopting agent-workflow on a repository the first time. It tells you what to expect, what the agent needs permission to do, what gets committed, and what stays for you to apply by hand.

## Prerequisites

- The repo is a git repository with a `main` (or equivalent default) branch.
- You can open PRs and merge them — bootstrap commits artifacts via a normal PR, nothing privileged.
- The repo has a host that can run the CI workflow (GitHub Actions on github.com or GHES). The shipped workflow template defaults to `ubuntu-latest` (GitHub-hosted runners); if your organization runs its own runners, change `runs-on` to `[self-hosted]` (or your runner labels) during bootstrap.
- Python 3.11+ is available on CI runners (the checker is single-file Python; no extra packaging).

You do **not** need: a database, a service to deploy, an account anywhere, or admin rights on the repo. Branch protection changes are proposed for a human to apply; bootstrap never reaches into repo settings.

## Two ways to adopt

### A. Conversational bootstrap (recommended)

Open the repo in Claude Code with the `agent-workflow` skill installed (clone the `agent-workflow` repo and copy [`dist/agent-workflow/`](../dist/agent-workflow/) into the target repo's `.claude/skills/`, or wherever your Claude Code install loads skills from). In a new session, ask the agent to install agent-workflow on the repo. The skill detects the missing `agent-workflow.yaml` and enters bootstrap mode automatically.

Bootstrap is a six-phase conversation. You stay in the loop the whole time.

| Phase | What happens | Your decision |
|---|---|---|
| 1. Inspect | The agent reads the repo: existing agent-instruction files, CI workflows, CODEOWNERS, build tooling, recent PR flow. Reports a structured finding. | Confirm or correct the finding. |
| 2. Propose | The agent drafts `agent-workflow.yaml` and the risk-classification policy at `agent-redline-policy.yaml` — both inert, nothing written. | Read both drafts. |
| 3. Adapt | The agent walks the **zone-utility check**, optionally runs the **tuner** against your recent PRs, and asks the few questions inspection couldn't answer. See [§Risk classification and how to keep it useful](#risk-classification-and-how-to-keep-it-useful). | Sign off explicitly to advance. |
| 4. Write | The agent writes the committed artifacts: configs, vendored checker/reporter scripts, AGENTS.md reference section, per-checkpoint reference docs, `.agent-workflow/tasks/README.md`. | None — but review the diff afterwards. |
| 5. Confirm CI | The agent always writes `docs/agent-workflow-ci-proposal.md`. It then asks whether to install the workflow file at `.github/workflows/agent-workflow.yml` directly or leave it in the proposal doc only. | **Decide.** This is the integration point that gates every future PR. |
| 6. Self-summary | The agent writes `docs/agent-workflow-bootstrap-summary.md`, runs a local probe of the checker, and reports what's installed, what's proposed, and what still needs human action. | Read it. Branch protection and CODEOWNERS additions need you. |

After Phase 4, you have a normal-looking PR with new committed files. Review and merge it as you would any PR.

### B. Manual install

You can install agent-workflow without the conversational bootstrap. Useful when you already know the shape of the repo and want the artifacts in one shot.

1. Write `agent-workflow.yaml` at the repo root. Start from [`core/templates/agent-workflow.yaml.template`](../core/templates/agent-workflow.yaml.template).
2. Write the risk-classification policy: copy a starting `agent-redline-policy.yaml` and vendor `scripts/agent-redline-report.py`.
3. Vendor the checker: build it with `scripts/build-vendored-checker.sh /path/to/your-repo/scripts/agent-workflow-check.py` from the agent-workflow source tree, or copy `<install-root>/scripts/agent-workflow-check.py` (already pre-built in the packaged install).
4. Vendor the sticky-comment renderer: copy `scripts/format-verdict-comment.py`.
5. Create `.agent-workflow/tasks/` with a `README.md` explaining the `{slug}.md` convention.
6. Append the agent-workflow reference section to your `AGENTS.md` / `CLAUDE.md` (template: [`core/templates/agents-section.md.template`](../core/templates/agents-section.md.template)).
7. Copy per-checkpoint docs to `docs/agent-workflow/` and `docs/agent-redline/skills/`.
8. Install the CI workflow: copy [`core/templates/.github/workflows/agent-workflow.yml.template`](../core/templates/.github/workflows/agent-workflow.yml.template) to `.github/workflows/agent-workflow.yml`.

Bootstrap mode does all eight steps for you and inspects the repo first so the drafts fit. **Skip manual install if you can.** The conversational path's value is in Phase 3 — calibrating the risk policy against your codebase. A copy-pasted policy without that step almost always over-classifies.

## Allow the agent to integrate CI

This is the part most teams need to think about explicitly. The CI workflow is what makes the gates **enforced** rather than advisory. Without it, agent-workflow runs on trust: the skill still guides the agent, but no machine checks the result at PR time.

What you have to authorize:

1. **A new workflow file** at `.github/workflows/agent-workflow.yml`. Bootstrap will not write it without your explicit yes in Phase 5; you can choose `proposal-only` and apply it yourself when ready.
2. **Branch protection updates.** Add `agent-workflow / agent-workflow` and `agent-workflow / redline` to required status checks for PRs against `main`. Bootstrap cannot do this — it has no admin access. The proposal doc names the exact check names.
3. **CODEOWNERS additions.** Bootstrap proposes ownership for `agent-redline/` and `agent-workflow.yaml`. Again, you apply this; bootstrap only proposes.
4. **Shadow → binding flip.** Bootstrap installs the risk classifier in `shadow` mode (advisory, never blocking). See [§Risk classification](#risk-classification-and-how-to-keep-it-useful) for when and how to flip.

The CI workflow runs two jobs: the risk classifier (path-based classification, posts its own sticky) and agent-workflow (reads the classifier verdict + the Work Record, posts its own sticky). Both stickies stay independently legible in the PR conversation.

## Risk classification and how to keep it useful

The harness ships with a bundled risk-classification subsystem (the `agent-redline` subtree). It exists for one reason: **to decide whether a change is structural or routine, deterministically, before the agent plans or codes.** Everything downstream — the Work Record shape, required approvals, plan-review depth — depends on the classification being right.

It is not optional. agent-workflow's default config (`redline: required`) treats a missing verdict as a CI configuration error.

This section covers what you need to know at adoption time and during tuning. For the full feature set — policy schema, vertical signals (API / schema / security / runtime-config), suppression detection, boundary-backend adapters, language extensions, sticky-comment shape, exit codes — see [`REDLINE.md`](REDLINE.md).

### The zones

Every changed file lands in one zone. The zone is read from `agent-redline-policy.yaml`.

| Zone | Meaning | Effect |
|---|---|---|
| **Red** | Architectural decisions: contracts, modeling, security, persistence, shared behavior. | Raises the change to Elevated/High. May trigger a review checkpoint (architecture-review, api-review, etc.). |
| **Blue** | Autonomous-safe: tests, docs, isolated and replaceable code. | No risk uplift; agent proceeds. |
| **Gray** | Unclassified. | Cautious by default; surfaces in the sticky for visibility. |
| **Watch** | Additive tag, not a zone. Path surfaces in the PR comment but does not raise risk or trigger a checkpoint. | Visibility only — useful for things that change often but the team wants tracked. |

Plus one terminal state: **Boundary violation** — a forbidden cross-layer dependency (e.g. `domain` importing `adapter`). Stops the workflow before planning; never waivable through a task exception.

### The cardinal rule: red means "different review behavior", not "important code"

This is the single most common adoption failure. Teams come in thinking "domain code is important, mark it red." Then `domain/` changes on every feature PR, the architecture-review checkpoint fires on every PR, the team learns to rubber-stamp it, and the gate is dead.

Red costs review attention. If a path is in the red zone but changes on routine feature work, that attention is wasted. **Important + routine = watch, not red.** Reserve red for paths where the *change* is genuinely an architectural decision, not just paths that *contain* architectural code.

### What bootstrap does to calibrate

Phase 3 of bootstrap is where the policy gets adapted to your codebase. Three steps the agent walks you through:

1. **Zone-utility check.** For every red entry in the draft policy, the agent asks: does this path change in ordinary feature PRs? If yes — are most of those changes truly structural decisions? If routine — demote to watch (still surfaces, no checkpoint) or blue. This is a starting hypothesis; the next two weeks of shadow mode will confirm or correct it.
2. **Tuner (when ≥30 recent PRs exist).** The agent can run a tuner against the last 30 merged PRs and report which red zones fired how often. Paths firing on >50% of PRs are almost always over-classified. The tuner only suggests — you approve, override, or split each one. Never auto-applies. **Ask for this step in bootstrap if your repo has the history; it is the single best way to avoid alert fatigue.**
3. **Repo-specific questions.** Third-party adapter contracts to mark red? Customer-specific code that mustn't leak into shared core? Generated source directories to exclude? PR-size thresholds for your team?

If you skipped manual install in Phase 3, expect to come back and re-calibrate after a few weeks of shadow-mode PRs.

### Shadow mode and the flip

`agent-redline-policy.yaml` ships with `modes.default: shadow` and `perCheck.boundary_violation: binding`. Meaning:

- **Zone classification** is advisory — the sticky comment shows red/blue/gray verdicts but the CI does not block on them.
- **Boundary violations** block from day one — they are structural errors, not policy choices.

The bootstrap self-summary recommends a 4-week or 30-PR shadow window before flipping `modes.default` to `binding`. During that window, **read the stickies.** If a red zone fires constantly on routine work, demote it before flipping. If a checkpoint never satisfies cleanly, fix it before flipping. You only want to enable hard blocking on a calibrated policy.

To flip: edit `agent-redline-policy.yaml`, change `modes.default: shadow` to `modes.default: binding`, commit. This goes through a normal PR — it's a policy change, so it lands in a red-zone PR by definition.

### Tuning after install

A few patterns:

- **A red zone fires too often.** Re-read recent PRs that hit it. If the changes are routine — demote to watch. If most are routine but some are real — split the path (e.g. `domain/repository/*.java` red for the interfaces, `domain/repository/impl/**` blue for implementations).
- **Reviewers keep approving the same checkpoint without reading.** That's the rubber-stamp signal. Either the zone is over-classified, or the satisfying label is too easy to apply. Tighten the checkpoint's `satisfiedBy` (require CODEOWNER approval instead of a label).
- **A red zone never fires.** Probably wrong path, not "stable code." Check whether the glob matches anything via `git ls-files`.
- **Boundary violation fires on legitimate refactoring.** It is not a noise problem — the boundary rule is wrong or the refactor is the wrong shape. Address it in a separate change that touches only the boundary policy; never weaken the policy in the same PR as the violation.

The tuner can be re-run any time the policy feels wrong. Bootstrap runs it from the skill source tree; you can run it again the same way after install.

### What you should NOT do

- Don't add red zones for "important code." Add them for "code where the change is a structural decision."
- Don't waive a boundary-violation finding through a task exception. The checker enforces this — see [`ENFORCEMENT.md`](ENFORCEMENT.md). To change a boundary rule, change it through its own reviewed PR.
- Don't flip from shadow to binding on day one. The calibration window is the whole point of shadow mode.
- Don't edit `agent-redline-policy.yaml` outside its own PR. The policy file is itself red-zone — every change should be visible and reviewed.

## What you should notice after install

| Notice | Meaning |
|---|---|
| Two new sticky PR comments | Risk-classifier + agent-workflow verdicts. They refresh on every push. |
| A required field for every PR | The Work Record at `.agent-workflow/tasks/<slug>.md`. The slug is derived from the branch name. |
| `Risk` and `Complexity` in the Work Record | Mandatory. Determine the record's shape and the controls applied. |
| `shadow` in `agent-redline-policy.yaml` | Zone classification is advisory until you flip it. Boundary violations still block. |
| `redline: required` in `agent-workflow.yaml` | The checker treats a missing classifier verdict as a CI configuration error. Default; leave it. |

## Local check before pushing

Run the same checker CI runs:

```bash
python scripts/agent-workflow-check.py --repo-root . --slug <slug>
```

Exit codes: `0` clean, `1` advisory, `2` blocking. The output is JSON; pipe it through `scripts/format-verdict-comment.py` to see the rendered sticky.

## Updating agent-workflow on an installed repo

The vendored scripts are checked in; updating means re-vendoring. From the agent-workflow source tree:

```bash
bash scripts/build-vendored-checker.sh /path/to/your-repo/scripts/agent-workflow-check.py
```

Then re-copy `scripts/format-verdict-comment.py` and `core/agent-redline/core/reporter/reporter.py` (→ `scripts/agent-redline-report.py`) the same way. Commit the diff.

For skill source updates, pull the latest `agent-workflow` repo and copy the refreshed `dist/agent-workflow/` into your target repo's `.claude/skills/`.

## Re-bootstrap

Bootstrap is one-shot per repo. If you need to start over, delete `agent-workflow.yaml` and the per-task records under `.agent-workflow/tasks/`, then ask the agent to install agent-workflow again. The skill detects the missing config and enters bootstrap mode.

This is intentional: re-bootstrap should be deliberate, not accidental.

## When the repo doesn't fit

If your repo has no source code, no architecture to classify, or PRs aren't the dominant flow, agent-workflow is the wrong tool — its value comes from enforcing structural risk on PR diffs. Bootstrap will escalate this back to you in Phase 1.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Checker exits 2 with `workrecord.exists` failing | Branch name and slug don't match. The slug is derived by stripping `feat/`, `fix/`, `slice/`, etc. and replacing `/` with `-`. Check the file at `.agent-workflow/tasks/<expected-slug>.md`. |
| Checker exits 2 with `workrecord.markers_present` failing | The marker block (`<!-- agent-workflow:start --> … <!-- agent-workflow:end -->`) is missing, malformed, or duplicated. Use `core/templates/work-record-routine.md` or `work-record-expanded.md` as the reference. |
| Checker exits 2 with `risk.declared_not_below_detected` | The classifier detected risk above what the Work Record declares. Either re-classify upward in the Work Record (and migrate to the expanded shape if needed) or remove the offending changes. |
| `risk.redline_findings_available` blocks under `redline: required` | The classifier job didn't produce a verdict artifact. Check the `redline` job's logs in the same CI run. |
| Architecture-review checkpoint fires on every PR | Over-classification. Walk recent PRs that triggered it; if the changes are routine, demote the red zone or split the path. See [§Risk classification](#risk-classification-and-how-to-keep-it-useful). |
| Sticky comment doesn't refresh | The PR's `agent-workflow` job is failing before the `Post sticky PR comment` step. Open the CI run and check the earlier steps. |

For the full predicate list and exact disposition of each, see [`ENFORCEMENT.md`](ENFORCEMENT.md).
