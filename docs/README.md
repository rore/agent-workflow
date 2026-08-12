# Documentation map

This folder mixes user-facing docs, the normative spec, maintainer references, and generated bootstrap output. Use this index to find the right surface.

If you only read one thing first, read the top-level [`../README.md`](../README.md) — it carries the capability map and the "what a developer needs to know" walkthrough.

## Start here (using agent-workflow on a repo)

| Doc | When to read |
|---|---|
| [`../README.md`](../README.md) | Top-level overview. Capability map + what's in / out of scope + checkpoint summary. |
| [`INTEGRATION.md`](INTEGRATION.md) | Adopt agent-workflow on your repo, tune the risk policy, troubleshoot the CI checker. |

## Day-to-day use (per-checkpoint reference)

| Doc | When to read |
|---|---|
| [`agent-workflow/`](agent-workflow/) | One file per checkpoint. Plain copies of `core/templates/checkpoints/*.md` so the agent has a stable reference inside the install. |
| [`agent-redline/skills/`](agent-redline/skills/) | One file per redline zone / boundary signal. Bootstrap copies these in too. |

## Enforcement and risk reference

| Doc | When to read |
|---|---|
| [`ENFORCEMENT.md`](ENFORCEMENT.md) | Predicate-by-predicate reference of what the CI checker actually blocks on. |
| [`REDLINE.md`](REDLINE.md) | Risk-classification subsystem: vertical signals, policy schema, calibration window, suppression detection, language extensions. |

## Normative spec and profile

| Doc | When to read |
|---|---|
| [`SPEC.md`](SPEC.md) | The portable workflow + harness contract. Normative; the rest of the docs operationalise it. |
| [`DEFAULT_PROFILE.md`](DEFAULT_PROFILE.md) | Default profile mapping (GitHub, CI, Redline). Normative for default profile; not portable. |

## Maintainers only (working on agent-workflow itself)

| Doc | When to read |
|---|---|
| [`skill-rationale.md`](skill-rationale.md) | Why the skill files are shaped the way they are. Background a maintainer needs when editing them. |
| [`PACKAGING.md`](PACKAGING.md) | How the skill is built and shipped to consumers. |
