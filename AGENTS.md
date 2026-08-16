# AGENTS.md — orientation for agents working on agent-workflow

You're working on `agent-workflow` itself — the harness skill other repos install. We dogfood: this repo carries `agent-workflow.yaml`, every task has a Work Record under `.agent-workflow/tasks/`, and the skill is installed locally for this session.

## Setup

Skill source lives in `core/skill/` and `core/templates/`. After edits, re-install so this session picks them up:

```bash
bash scripts/install-skill-locally.sh
```

Same script regenerates `dist/agent-workflow/`. Before pushing: `bash scripts/package-skill.sh && git add dist/agent-workflow/` — `tests/package/check-package.sh` blocks the merge otherwise. Install Python deps once per checkout: `python -m pip install -r requirements-test.txt` (test runners use `python`, falling back to `python3`).

## Workflow

Every task uses `/agent-workflow`. Run the local checker after each State change:

```bash
python -m core.checker --repo-root . --slug <slug>
```

Running the skill on the project that builds it is intentional. If the skill says something unclear, wrong, or missing, fix the source in `core/skill/`, re-install, continue. Dogfooding has already caught real bugs.

## Load when relevant (not on session start)

| File | When to load |
|---|---|
| `docs/SPEC.md` | Touching workflow concepts, checkpoints, or harness contract. Use TOC; don't read whole. |
| `docs/DEFAULT_PROFILE.md` | Touching default profile fulfillment (GitHub, CI, Redline). |
| `docs/DECISIONS.md` | Touching a prior decision or wondering why. |
| `docs/INTEGRATION.md` | Bootstrap-mode, CI workflow template, onboarding story. |
| `docs/REDLINE.md` | Porting upstream redline, debugging a verdict, extending policy. |
| `docs/ENFORCEMENT.md` | Touching the checker or explaining a verdict. |
| `docs/PACKAGING.md` | Bumping `dist/`, cutting a release, changing what ships. |
| `docs/skill-rationale.md` | Editing a skill file and wondering why prose was trimmed. |
| `core/skill/*.md`, `core/templates/checkpoints/*.md` | Before editing any file an agent loads mid-task. |
| `.local/WORK_TRACKER.md` | Picking work back up (gitignored). |

## Hard rules

1. **KISS.** Add an artifact only when it has a concrete responsibility. Symmetry with agent-redline is not a reason.
2. **Skill-authoring discipline applies to every file an agent loads mid-task.** See [`CONTRIBUTING.md`](CONTRIBUTING.md) §"Skill-authoring discipline" before editing skill source — it carries the deletion test, the table-vs-prose rule, the cross-reference convention, dist path rules, and budget discipline.
3. **Run `bash tests/run-all.sh` before pushing.** CI runs the same suite.
4. **No marketing tone.** Developer-to-developer.
5. **Substantive decisions append to `docs/DECISIONS.md` with rationale.** Routine session work doesn't.
6. **SPEC is normative.** Edit `docs/SPEC.md` first for conceptual changes, then propagate.
7. **Re-install the skill after editing skill source.** Otherwise this session uses stale content.
8. **Repo-structure-agnostic.** Never hardcode a consumer's layout (e.g. `src/`). Read it from config with a sensible default; bootstrap detects and configures it; test ≥2 layouts. Every feature must consider that consumer repos differ in structure.

<!-- agent-workflow:agents-section:start -->
## agent-workflow + agent-redline (installed on this repo)

This repo dogfoods both skills it ships. The install is **deliberately partial** — it's the source of the skill, not a typical consumer.

| File | This repo | Typical consumer |
|---|---|---|
| `agent-workflow.yaml` | Present. `redline: required`. | Same shape, copied from template. |
| `agent-redline-policy.yaml` | Zone-only shape (no `pyproject.toml`). Red zone: schemas, SPEC, governance config, CI workflow. | Shape varies by language extension. |
| `.agent-redline/suppressions.yaml` | Stack-neutral defaults. | Bootstrap copies from chosen extension. |
| agent-redline reporter | **NOT vendored at repo root.** CI runs `python core/agent-redline/core/reporter/reporter.py` directly (dogfood) — a committed copy would drift. | Vendored from `dist/agent-workflow/agent-redline/scripts/` as `scripts/agent-redline-report.py`. |
| `scripts/agent-workflow-check.py` | **NOT vendored.** CI uses `python -m core.checker` directly — vendoring would be dead code. | Vendored from `dist/agent-workflow/scripts/`. |
| CI workflow | Two jobs (`agent-workflow` + `redline`). `agent-workflow` job runs `python -m core.checker`; `redline` job runs the reporter from source (`core/agent-redline/core/reporter/reporter.py`). | Two jobs from template; both invoke vendored scripts. |

## Where the surfaces live

| Surface | Path | Notes |
|---|---|---|
| Spec (normative) | [docs/SPEC.md](docs/SPEC.md) | Red-zone. Edits go through architecture-review. |
| Redline policy | [agent-redline-policy.yaml](agent-redline-policy.yaml) | Red-zone (self-protecting). |
| Suppression markers | [.agent-redline/suppressions.yaml](.agent-redline/suppressions.yaml) | Override via the policy's `suppressions.add/remove`, not by hand-editing. |
| Per-task Work Records | `.agent-workflow/tasks/{slug}.md` | Blue. Slug derived from branch name. |

## Redline shadow window

Policy ships in `modes.default: shadow`. After 4 weeks / 30 PRs, re-run `python scripts/agent-workflow-tune.py --repo rore/agent-workflow` and review calibration before flipping to `binding`. `boundary_violation` is already `binding` per SPEC.
<!-- agent-workflow:agents-section:end -->
