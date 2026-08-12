# Contributing

## Repository layout

See [`README.md`](README.md) for the layout.

## Before opening a PR

1. Run the full local test suite:

   ```bash
   bash tests/run-all.sh
   ```

2. If you changed anything an agent loads mid-task (`core/skill/*.md`, `core/templates/**`, the AGENTS.md template), follow the [skill-authoring discipline](#skill-authoring-discipline) below. Read it before editing — it tells you what to keep, what to cut, and what to externalize.

3. If you made a substantive design decision, record it with rationale in the PR description or a project decision log.

4. If you changed the spec, update [`docs/SPEC.md`](docs/SPEC.md) first, then propagate to skill files, templates, and schemas.

## Skill-authoring discipline

Every line in a skill file is a recurring token cost. Per the Claude Code skills docs: *"Once a skill loads, its content stays in context across turns — every line is a recurring token cost."* Skill files are the *contract* the agent operates under; rationale and design discussion belong elsewhere ([`docs/skill-rationale.md`](docs/skill-rationale.md)).

The 2026-06 context-budget audit cut floor cost ~5,200 → ~3,000 tokens and elevated-task cost ~13,600 → ~7,800 tokens by re-deriving every ceiling from load-point reasonableness and trimming prose to fit. This section is how that discipline gets maintained.

### Audience

The audience is the agent, not a human reader. Write for an LLM at decision time, not a contributor reading on a Friday afternoon.

- Imperative voice. *"Write the Work Record before starting."* not *"It's important that you write the Work Record before starting."*
- No marketing tone. No "powerful," "robust," "comprehensive."
- No section intros that explain what the section is about — the heading does that.
- No "this is where most of the harness's value lives" framing. The agent doesn't care about your section's importance.

### The deletion test

For every sentence you'd add:

| Sentence type | Keep | Cut | Move to `docs/skill-rationale.md` |
|---|---|---|---|
| **Rule** — what the agent must / must not do | ✓ | | |
| **Anti-pattern** — a specific failure mode the agent pattern-matches against ("you started fixing X, discovered Y, started fixing Y") | ✓ | | |
| **Table** — lookup the agent does at decision time (e.g., redline-verdict → Risk) | ✓ | | |
| **Hard rule list** — non-derivable constraints at a phase boundary | ✓ | | |
| **Rationale** — *why* the rule exists, what failure mode it prevents in the abstract | | | ✓ |
| **Restatement** — the same rule said in different words | | ✓ | |
| **Narrative intro** — "This checkpoint is where..." or "The longest stretch..." | | ✓ | |
| **Historical context** — "Earlier versions of this file..." | | | ✓ |
| **Design-time commentary** — "We chose X over Y because..." | | | ✓ |
| **Cross-reference repeat** — the same SPEC §X cited three times in one file | | ✓ (keep one) | |

If you can't decide whether a sentence is a rule or rationale, ask: *would an agent that didn't see this sentence pattern-match a failure?* If yes, it's a rule or anti-pattern — keep. If no, it's rationale — move.

### Tables over prose

When the content is a lookup or a per-case rule, use a table. Tables compress 30–50% versus equivalent prose AND are easier for an agent to consume at decision time. Examples we've already converted:

- Redline-verdict → Risk translation (`templates/checkpoints/assess-risk.md`)
- Plan-review obligations by Risk level (`templates/checkpoints/plan-and-review.md`)
- "What counts as material scope expansion" (`templates/checkpoints/implement.md`)
- "Where to record what" by surface (`templates/checkpoints/implement.md`)

If you find yourself writing three bullet points that share a structure, that's a table.

### Cross-references over restatement

When two files need the same rule, define it once in the closest-loaded file and cross-reference from the others. The canonical example: clean-context delegation lives in `core/skill/operating-mode.md` §"Clean-context delegation"; `assess-risk.md` and `plan-and-review.md` link to it instead of restating the mechanism.

Rule of thumb: the rule lives in the file that's loaded *most often* among the files that need it. Operating-mode loads every turn; checkpoint files load only when their checkpoint is entered. Define shared rules in operating-mode.

### Externalize structured artifacts

For *fill-in-the-blanks artifacts* the agent produces once (not rules the agent has to remember), use a template under `core/templates/` rather than inlining. The agent loads the template only when it fills in the artifact, not for the duration of the skill's loaded life.

Established patterns:
- Work Record templates: `core/templates/work-record-{routine,expanded}.md`
- Phase 6 self-summary: `core/templates/bootstrap-summary.md.template`
- Consumer AGENTS.md section: `core/templates/agents-section.md.template`

When you add a new structured artifact: ask whether it's a rule (lives in the skill file) or a thing the agent produces once (lives in a template).

### Dist path conventions

Source files use *dist-relative* paths so the packager's substitutions produce valid dist paths. The substitutions are in `scripts/package-skill.sh`. Check the substitution list before adding a new cross-reference.

Common conventions in source:

| Source path | Resolves in source? | Substitutes to | Resolves in dist? |
|---|---|---|---|
| `templates/checkpoints/X.md` (from `core/skill/operating-mode.md`) | No (broken — `core/skill/templates/...` doesn't exist) | `templates/checkpoints/X.md` (same string) | Yes (`<pkg>/templates/checkpoints/X.md`) |
| `../../skill/operating-mode.md` (from `core/templates/checkpoints/X.md`) | Yes (`core/skill/operating-mode.md`) | `../../operating-mode.md` | Yes (`<pkg>/operating-mode.md`) |
| `agent-redline/core/skill/agent-redline.md` (from `core/skill/bootstrap-mode.md`) | No | `agent-redline/SKILL.md` | Yes (`<pkg>/agent-redline/SKILL.md`) |

When adding a new cross-reference: trace it in both source and dist. If either is broken, either add a substitution or pick a different convention. The link checker runs against dist files in CI.

### Budget discipline

`tests/budget/budget.yaml` declares per-file token ceilings. **Ceilings are the constraint, not the measurement.** Don't raise a ceiling because prose has grown into it without a corresponding load-point justification.

When you add content to a skill file:

1. Run `bash tests/budget/run.sh --verbose` first to see current utilization.
2. If the new content fits within the existing ceiling, ship it.
3. If it doesn't fit, decide whether the new content earns the ceiling bump:
   - Does it remove an ambiguity the agent currently has to resolve by judgment?
   - Does it prevent a failure mode the harness can't catch?
   - Does it close a cross-reference gap?
   - If yes to any: bump the ceiling and update the manifest's `why:` string to record the trade.
   - If no: trim the existing content to make room, or put the content in `docs/skill-rationale.md`.
4. Run `bash tests/budget/run.sh --verbose` again to confirm headroom.

The preamble of `tests/budget/budget.yaml` carries the operational totals (floor, routine task, elevated task, bootstrap one-shot). These are the *demand side*. Per-file ceilings are the *supply side*. When you bump a per-file ceiling, also check the operational totals — a 200-tok per-file bump can push the floor target past its operational ceiling.

### Anti-patterns to avoid

If you find yourself doing any of these, stop:

- **"This needs more explanation."** No — it needs less. If a rule isn't clear in one sentence, the rule isn't clear; fix the rule.
- **"I'll restate it for emphasis."** Once is enough. Restatement makes the agent pick the loosest phrasing as canonical.
- **"Let me add a paragraph of context first."** Context narration is filler. State the rule.
- **"This is the why behind the rule."** Move to `docs/skill-rationale.md`. The skill file carries the rule.
- **"Let me explain what this section covers."** The heading explains it.
- **"I'll add a 'When to use this checkpoint' subsection."** The checkpoint's name says when to use it.
- **"For completeness, the harness also..."** If it's not load-bearing, cut it. The agent doesn't need completeness; it needs operational clarity.

### When you trim

Make the cuts in small commits — one file per commit ideally — so a future reviewer can bisect what was removed if a regression turns up. The first-pass audit landed as 9 small commits; the second pass as 6. Both were easy to follow.

Run the clean-context functional review after substantial trimming: spawn an Explore-class subagent to read the trimmed files in isolation and answer *can you do your job from these files alone?* If the answer is no, name where the gap is. The 2026-06 second-pass audit caught one real gap (invocation-mechanism ambiguity) and one false positive (the reviewer recounted tokens without the script's locale pin) — both worth knowing about.

## What does NOT belong here

- Marketing tone. Developer-to-developer.
- Profile-specific guidance lives in `docs/DEFAULT_PROFILE.md`, not in `core/skill/`.
- Artifacts added "for symmetry" with another project. Each file earns its keep.
