# Skill packaging

How agent-workflow's skill is built, where consumers install it from, and what travels with each install.

## Two surfaces

agent-workflow has two surfaces that get distributed independently:

1. **The skill** — markdown the agent reads at session start and during checkpoints. Lives in `core/skill/` (source) and `core/templates/checkpoints/` (per-checkpoint guides). `scripts/package-skill.sh` assembles it into the Agent Skills standard layout. The committed [`dist/agent-workflow/`](../dist/agent-workflow/) tree is the install source — consumers copy it into their `.claude/skills/`.
2. **The CI checker** — a single-file Python script the consumer's repo executes at PR time. Vendored into each consuming repo as `scripts/agent-workflow-check.py`. Distributed via `scripts/build-vendored-checker.sh`, not via the skill tree.

A consumer needs both. The skill alone is just guidance; the checker alone has no source of truth to validate against. Bootstrap-mode installs both.

## What's in the skill package

The committed `dist/agent-workflow/` tree (52 files), produced by `scripts/package-skill.sh`. After install (clone the repo, copy the directory into your `.claude/skills/`), the skill directory looks like:

```
agent-workflow/
├── SKILL.md                                  # entry (Agent Skills standard name)
├── operating-mode.md                         # the everyday checkpoint loop
├── bootstrap-mode.md                         # the install-on-a-new-repo conversation
├── templates/
│   ├── checkpoints/*.md                      # 7 per-checkpoint reference docs
│   ├── agents-section.md.template            # AGENTS.md fragment bootstrap appends
│   ├── work-record-routine.md                # compact-shape Work Record template
│   ├── work-record-expanded.md               # expanded-shape Work Record template
│   ├── agent-workflow.yaml.template          # per-repo config bootstrap writes
│   └── .github/workflows/agent-workflow.yml.template
├── assets/
│   └── schema/agent-workflow.schema.json
├── scripts/
│   ├── agent-workflow-check.py               # vendored CI checker (pre-built)
│   ├── format-verdict-comment.py             # CI sticky renderer
│   └── agent-workflow-tune.py                # one-shot calibration tuner
└── agent-redline/                            # self-contained bundled subsystem
    ├── SKILL.md                              # redline's skill entry
    ├── operating-mode.md
    ├── bootstrap-mode.md
    ├── references/per-checkpoint/*.md        # 8 zone- and checkpoint-specific guides
    ├── assets/
    │   ├── schema/*.json                     # 3 policy/boundary/suppression schemas
    │   └── templates/                        # policy + AGENTS fragment + pr-template + pre-push + suppressions
    ├── scripts/agent-redline-report.py       # vendored reporter (the source for the consumer-side vendor)
    └── extensions/
        ├── jvm-archunit/                     # JVM/ArchUnit profile + adapter
        └── python/                           # Python/import-linter profile + adapter + scripts/
```

The CI checker source (`core/checker/`), the parser (`core/work_record/`), and the dev-repo tests do **not** ship as part of the skill — only the pre-built `agent-workflow-check.py` does, so consumers can install without running any build. Inside `agent-redline/`, the layout intentionally mirrors what `agent-redline`'s own packaged release produces; the skill text inside it reads as if redline were installed standalone, and the path substitutions `scripts/package-skill.sh` applies make that true.

The packaged skill is self-resolving: every internal link in the markdown points at a file that exists inside the package. `tests/package/check-references.sh` enforces this on every PR.

The bundled risk-classification subtree (`agent-redline/`) is part of agent-workflow's surface to the consumer — its skill files travel with the install so the agent can read them when classifying a change. See [`INTEGRATION.md`](INTEGRATION.md#risk-classification-and-how-to-keep-it-useful) for the consumer-facing view.

## SKILL.md frontmatter

The skill's discovery surface for Claude Code / Agent Skills consumers. Keep the description tight and triggering: it is what determines whether the agent invokes the skill.

```yaml
---
name: agent-workflow
description: Use when starting, advancing, pausing, or resuming an engineering task. Maintains the Work Record, validates readiness gates between checkpoints, and routes risk classification to agent-redline (bundled, required by default).
---
```

Source: [`core/skill/agent-workflow.md`](../core/skill/agent-workflow.md). When `scripts/package-skill.sh` mirrors it into `dist/agent-workflow/SKILL.md` (and any per-developer `.claude/skills/agent-workflow/SKILL.md`), the frontmatter travels verbatim.

## Distribution

### Today: install from this repo

This repo is the install source. The flow:

1. Clone `agent-workflow`.
2. Copy [`dist/agent-workflow/`](../dist/agent-workflow/) into your target repo's `.claude/skills/` (or wherever your Claude Code install loads skills from).
3. Open your target repo in Claude Code and ask the agent to install agent-workflow — bootstrap-mode runs from there.

The committed tree is the single artifact a consumer needs. `tests/package/check-package.sh` runs on every PR in this repo and blocks merges when `dist/agent-workflow/` drifts from `core/skill/`, so what's checked in is always what `scripts/package-skill.sh` would produce from the current sources.

### Later: agent-skills registry

The `agent-skills` registry is the eventual home — `/plugin install` and `npx skills add` consume from there. That sync is deferred until agent-workflow is approved for registry inclusion. When it lights up, the publish flow at release time will be:

1. Cut a release tag on this repo.
2. Verify `dist/agent-workflow/` matches `core/skill/` (`bash tests/package/check-package.sh`).
3. Sync `dist/agent-workflow/` into the agent-skills repo's `skills/agent-workflow/` directory.
4. Open a PR against agent-skills. The agent-skills repo's CI validates the SKILL.md frontmatter.
5. Vendored binaries are not re-built by the publish flow. Consumers re-run bootstrap-mode in their repo, which re-vendors `scripts/agent-workflow-check.py` etc. from the latest source.

The agent-redline subtree is vendored inside agent-workflow under `core/agent-redline/`. It is not consumed as a separate package; agent-workflow's release process bumps the vendored copy as needed. Treat it as internal — when its upstream source publishes changes worth pulling in, sync the relevant files into `core/agent-redline/` and ship them in the next agent-workflow release.

## Versioning

Skill changes are tied to dev-repo tags. The vendored checker carries the dev-repo commit SHA in its bootstrap summary (`docs/agent-workflow-bootstrap-summary.md`) so consumers can tell which version they have.

There is **no separate skill version** — the skill ships at whatever shape `core/skill/` is at the release tag. If the consumer's skill drifts from their vendored checker (e.g. they updated one without the other), the predicate names and the skill's checkpoint guidance can disagree. The bootstrap-mode summary names both versions so the drift is visible.

## What does NOT belong in the skill package

- Marketing tone. The skill is dev-to-dev; the user reading it is an agent or an engineer mid-task. Cut anything that sounds like a pitch.
- Profile-specific terminology in `core/skill/*`. The skill ships into any repo; profile-specific mappings live in [`docs/DEFAULT_PROFILE.md`](DEFAULT_PROFILE.md), not in the skill body.
- Implementation detail of the checker. The skill references predicate **names** (so the agent can explain failures) but does not embed the checker's implementation. The predicate semantics live in [`docs/ENFORCEMENT.md`](ENFORCEMENT.md) and the predicate source.
- "Symmetry" files. Each file in `core/skill/` earns its keep — `operating-mode.md` and `bootstrap-mode.md` are the only modes; per-checkpoint references load on demand.

## Re-installing the skill in the dev repo

The dev repo dogfoods the skill on itself. After editing anything under `core/skill/` or `core/templates/checkpoints/`, the source no longer matches the committed `dist/`. Re-run both:

```bash
bash scripts/package-skill.sh         # refresh dist/agent-workflow/
bash scripts/install-skill-locally.sh # refresh .claude/skills/agent-workflow/
```

The install script delegates to the package script, so the two targets always match — there's one file list, in `package-skill.sh`. `git add dist/agent-workflow/` before pushing; `tests/package/check-package.sh` runs on every PR and blocks merges when sources have drifted from the committed tree.

Your current Claude Code session is using the previously-installed copy until you re-install.
