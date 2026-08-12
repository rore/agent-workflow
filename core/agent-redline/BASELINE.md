# agent-redline baseline

This directory is the bundled fork of the agent-redline project. agent-workflow owns the snapshot; any change here is a local change. There is no automated sync mechanism — when upstream evolves and we want to port changes, we do it manually by diffing.

## Snapshot metadata

- **Upstream reference (not auto-synced; manual port workflow below):** `github.com/rore/agent-redline`
- **Upstream commit:** `954b92bdfb0143ddf984331b07568ec887e6b67d`
- **Copy date:** 2026-06-23
- **Copied subtrees:** `core/skill/`, `core/reporter/`, `core/schema/`, `core/templates/`, `extensions/`, `tests/`, `LICENSE`
- **Skipped:** `.git/`, `.github/`, `dist/`, `demo-source/`, `demo-source-python/`, `docs/`, `examples/`, `scripts/`, top-level `README.md` / `CONTRIBUTING.md` / `CODE_OF_CONDUCT.md` / `SECURITY.md` / `INSTALL.md` / `AGENTS.md`

## Why these subtrees

- **`skill/`** — agent-workflow's `assess-risk.md` checkpoint loads `skill/agent-redline.md` and the mode files it points at. Required.
- **`reporter/`** — produces the verdict JSON the agent-workflow CI checker consumes. Required.
- **`schema/`** — `agent-policy.schema.json` for the per-repo policy redline reads from. Required.
- **`templates/`** — `agent-policy.yaml.template` and per-checkpoint guidance docs. Used by the future bootstrap (W12, slice C).
- **`extensions/`** — stack-specific (JVM/ArchUnit, Python). Useful for service repos that consume the harness; carried so the bundle is complete.
- **`tests/`** — redline's own tests. Run as part of `bash tests/run-all.sh` in a new `redline` layer (slice step B1a). Treating redline as inherent means its regression protection runs with ours.
- **`LICENSE`** — attribution stays with the copied source.

## What changes (and doesn't) over time

Redline content stays **verbatim** inside this directory. Edits to redline made here are intentional local tweaks; they remain owned by us and do not flow back to upstream unless someone deliberately ports them.

Skipped upstream artifacts (`dist/`, `demo-source*/`, `docs/`, `scripts/`, etc.) are development surface for the public redline project and not needed for bundling.

## Manual porting workflow

When you want to bring upstream changes in:

1. `git fetch` upstream; diff the upstream commit recorded above against newer upstream HEAD.
2. Inspect each change; decide whether it applies.
3. Apply selectively. Update this file's `Upstream commit` and `Copy date` to record the new baseline.
4. Open a normal PR.

No automated tooling — by design. This is an owned snapshot, not a sync.
