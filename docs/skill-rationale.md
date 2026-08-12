# Skill rationale

Design-time rationale and prose moved out of agent-loaded skill files during the 2026-06 context-budget audit. The skill files themselves carry rules, tables, and load-bearing anti-patterns; this document carries the *why* a maintainer needs when editing them.

The Claude Code docs say: "Once a skill loads, its content stays in context across turns — every line is a recurring token cost." So everything that isn't actionable for the agent at the moment it loads the file is overhead. The rules below were moved here because they helped a human reader understand the design but did not change what an agent would do.

When you edit a skill file, read the relevant section here first so you don't unknowingly undo a design choice that has reasoning behind it but no longer states the reasoning in the file itself.

## Why we have two modes (operating vs bootstrap)

Bootstrap is conversational, one-shot, and configures the harness on a new repo. Operating is per-task, runs every session in a configured repo. They share almost no code path. Splitting them at the SKILL.md level means the per-session cost is only the operating-mode surface — bootstrap-mode never loads during day-to-day work.

The mode trigger is mechanical: presence of `agent-workflow.yaml` at repo root. That mechanical trigger is why hierarchy works here without confusing the agent — it doesn't have to judge which mode to be in.

## Why per-checkpoint files load on demand

The agent walks one checkpoint at a time. Loading all seven into context preemptively would pay ~7K tokens for content the agent uses sequentially. The skill is structured so each checkpoint file is referenced from operating-mode.md as a relative path under `templates/checkpoints/`, and the agent loads that file only when it enters the corresponding part of the walk.

This is also why we don't subdivide checkpoint files further. Per-field reference files would lose the gestalt of "what a checkpoint looks like." The current granularity is one file per orthogonal axis (mode × checkpoint), which is the right cut.

## Why anti-patterns stay verbatim

Anti-patterns in `implement.md` and the per-checkpoint files are the load-bearing prose that prevents the agent from rationalizing past a rule. Where a rule is "stay within approved scope," the anti-pattern is "you started fixing X, discovered Y, started fixing Y; the Work Record still says X." That second sentence is what the agent pattern-matches against its current state — without it, "approved scope" is abstract.

When trimming a checkpoint file, the rule of thumb: cut the *explanation* of why the rule exists; keep the *examples* of how it fails. The first is for human readers; the second is for the agent.

## Why we don't inline Work Record templates in operating-mode.md

Before the 2026-06 trim, operating-mode.md inlined the entire compact and expanded Work Record templates (~700 tokens). The agent already has these in `core/templates/work-record-{routine,expanded}.md` — it loads them when it initialises the record, not when it reads operating-mode.md. Inlining made operating-mode.md a one-stop reference for a human reader, but it was paid tokens for content the agent re-reads from a different file anyway.

## Why we externalize the bootstrap Phase 6 self-summary template

The Phase 6 self-summary in bootstrap-mode.md is a ~700-token Markdown table. The agent fills it in once per bootstrap and never references it again. Externalizing to `core/templates/bootstrap-summary.md.template` means the agent loads it only during Phase 6, not for the duration of the bootstrap conversation.

This is the same pattern as work-record templates: load-on-demand the structured artifact, load-on-skill-entry the *rules*.

## Why the Vocabulary table moved from SKILL.md to operating-mode.md

The Vocabulary table teaches terms like `Work Record`, `Slug`, `Compact/Expanded shape`, `Checkpoint`. The agent only needs these terms once it has entered operating-mode — they're not relevant for mode selection or for bootstrap. Moving them out of SKILL.md saves ~250 tokens on every session where the agent reads SKILL.md but never enters operating-mode (e.g., a glance during skill registry display), and on every session where the agent re-reads SKILL.md to remind itself of the resources list.

## Plan-and-Review by Risk level: the "cheating window" rationale

Earlier versions of `plan-and-review.md` contained a ~250-token essay explaining that High-risk Approvals are self-attested: the harness cannot verify that the human was actually in the loop, and an agent can fabricate `Approved by user <timestamp>: "ok"`. The decision (DECISIONS.md 2026-06-23) accepted this as the cost of traceability-not-identity.

The rule the agent needs is one line: "Record the human's verbatim response in the Approvals field." The rationale — why we accept self-attestation, what the reviewer can do with the recorded text — is for the human reading the design doc, not the agent following the rule.

## Verification plan grammar: why we have multiple accepted shapes

The Verification plan accepts five shapes (`→`, `->`, `—`, method-first colon, `manual:`). This is for human convenience — different writers reach for different conventions. The agent doesn't need to *understand* why we accept all five; it needs to *parse* the line. The grammar table stays in `verify.md` (the checkpoint that uses it); the parser handles all five shapes via the `evidence.criteria_have_methods` predicate.

We removed the verbatim duplication of the grammar table in operating-mode.md. The agent reads it once when it enters Verify, not every operating-mode turn.

## Why the consumer-repo AGENTS.md section is short

`core/templates/agents-section.md.template` is appended to consumer repos' `AGENTS.md` files during bootstrap. Once appended, it lives in the consumer repo's session floor — every agent in that repo pays for it on every turn.

Pre-trim, the template was 665 tokens of narrative ("This repository uses agent-workflow…", a re-explanation of what the skill already knows, a marketing-style introduction). Post-trim, it's a pointer + the rules a developer must keep in mind that aren't derivable from the skill files themselves (where Work Records live, how to invoke the skill, the re-bootstrap path).

The bias: anything the agent already knows from the skill itself does NOT belong in the consumer AGENTS.md section. The section is for facts the skill cannot infer about *this* consumer repo.

## What we did not externalize

Kept in skill files because the agent needs them at decision time:

- The redline-verdict → Risk translation table in `assess-risk.md` — the agent reads this to translate redline's output into a Risk classification.
- The per-Risk-level review obligations in `plan-and-review.md` — the agent reads this to know whether to invoke a clean-context subagent or stop for human approval.
- The "State allowed values" list in `operating-mode.md` — the agent reads this to know what to write in the State field.
- The Anti-patterns lists everywhere — these are the failure modes the agent pattern-matches against.
- Hard rules blocks (in bootstrap-mode.md's "Hard rules" section, and the per-checkpoint refuse/forbidden lists) — these are non-derivable constraints the agent must hold while executing.

Everything else was a candidate for trimming.
