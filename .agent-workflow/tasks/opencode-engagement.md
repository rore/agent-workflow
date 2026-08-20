# Add OpenCode engagement to agent-workflow's install

<!-- agent-workflow:start -->
**Outcome:** A repo with agent-workflow installed nudges an agent running under **OpenCode** to use the workflow, the same way `.claude/hooks/seed-workflow.sh` nudges Claude Code today. OpenCode does not read `.claude/` or run those hooks, so the install lays down an OpenCode-side engagement artifact (a plugin) alongside the Claude hooks.

**Target:** This repo (agent-workflow harness). Skill source, packager, bootstrap instructions, docs, tests. dist/ regenerates. Consumer repos pick it up on next bootstrap/re-bootstrap.

**Scope:**
- NEW `core/skill/opencode/agent-workflow.mjs` — the OpenCode plugin. Injects the seed reminder into the system prompt via `experimental.chat.system.transform`. Fail-open (try/catch, never breaks a turn). Static string, no deps, no state.
- MODIFY `scripts/package-skill.sh` — copy `core/skill/opencode/` into `dist/agent-workflow/opencode/`; add to `required_paths`. Manifest regenerates.
- MODIFY `core/skill/bootstrap-mode.md` — Phase 4 step: copy `<install-root>/opencode/agent-workflow.mjs` → consumer `.opencode/plugins/agent-workflow.mjs`.
- MODIFY `core/templates/bootstrap-summary.md.template` — add the OpenCode plugin row.
- MODIFY `README.md` — OpenCode install/engagement note.
- MODIFY `tests/hooks/run.sh` — assert seed-text parity (plugin SEED == `seed-workflow.sh` CTX) and fail-open structure.
- MODIFY `tests/package/check-install-probe.sh` — require the plugin in the install manifest.
- REGEN `dist/agent-workflow/opencode/agent-workflow.mjs`, `dist/agent-workflow/manifest.txt`, and the committed `.claude/skills/agent-workflow/` mirror.

**Constraints:**
- Keep the Claude hooks' semantics: **nudge, fail-open, not a hard gate**. The CI checker stays the sole enforcer. Do NOT build a plan-gate/permission gate in the plugin.
- Do NOT touch `core/templates/agents-section.md.template` — it is at the 400-token budget ceiling and the plugin needs no AGENTS.md mention (auto-loads from `.opencode/plugins/`; existing "read SKILL.md" fallback covers discovery).
- Keep `core/skill/bootstrap-mode.md` under its token ceiling — new Phase 4 step is terse.
- No new CI dependency (no `node` in the test path). Parity/structure test is bash.
- Skip the plan-gate hook (OpenCode has no `ExitPlanMode` analog) and the reinforce hook (OpenCode *does* have `tool.execute.after`, but reinforce is a fail-open nudge the CI gate backstops — out of minimal scope).

**Completion criteria:**
- All 9 test layers green (`tests/run-all.sh`), including the new parity/structure assertion.
- `dist/` matches source (package drift check clean); plugin present in `manifest.txt`; committed `.claude/skills/` mirror in sync.
- Bootstrap instructions + summary template name the OpenCode plugin destination.
- CI green on the PR.

**Risk:** Elevated

**Complexity:** Moderate

**Reason:** Redline verdict on the intended scope is GRAY (gray/watch paths under `core/skill/`, `core/templates/`, `dist/`; zero red, zero boundary violations, zero checkpoints) → Elevated by the conservative default; no contract/security/persistence/financial surface → not High. Moderate: several coordinated components (plugin + packager + bootstrap doc + summary template + README + tests) with real uncertainty (experimental OpenCode hook API, install-wiring integration), one working session.

**Discovery:**
- The install is **agent-driven**, not a monolithic script: `core/skill/bootstrap-mode.md` Phase 4 has the agent `cp` files out of the installed skill tree (`dist/agent-workflow/`) into the consumer's repo. `install-settings.py` only generates `.claude/settings.json`; it does not copy the plugin. So the OpenCode plugin wires in as a new Phase 4 copy step to repo-root `.opencode/plugins/` (sibling of the `.claude/hooks/` copy), NOT inside `.claude/skills/`.
- Reference: the Pallium OpenCode plugin (`pallium.mjs`) confirms the hook name `experimental.chat.system.transform`, its `(input, output)` signature, appending to `output.system[]`, that OpenCode reads `AGENTS.md`, and that plugins auto-load from `.opencode/plugins/` (no `opencode.json` entry needed at repo root).
- Our seed is a **static string** (`core/skill/hooks/seed-workflow.sh`), unlike Pallium's daemon-queried memory — so the plugin is ~15 lines with no session state.
- `package-skill.sh` copies `core/skill/hooks/*` and gates on `required_paths`; manifest is written last and excludes itself. `tests/package/check-package.sh` diffs a fresh rebuild against committed `dist/` (drift → exit 2). So packaging the plugin + drift/manifest coverage comes for free once it is added to the packager.

**Material assumptions:**
- A1: `experimental.chat.system.transform` is the current OpenCode plugin hook for system-prompt injection. Disproof: OpenCode renamed/removed it. Evidence for: the maintained `pallium.mjs` uses it. If disproved: the seed still fails open (no crash); update the hook name and re-verify against a live OpenCode run.
- A2: OpenCode auto-loads plugins from repo-root `.opencode/plugins/` with no `opencode.json` entry. Disproof: a live OpenCode run does not load the plugin. If disproved: add the `opencode.json` `"plugin"` entry to the bootstrap step.
- A3: The committed `.claude/hooks/seed-workflow.sh` CTX text is the canonical seed. Duplicating it as a JS const is acceptable because the parity test pins the two copies; runtime coupling (plugin reading the .sh) is rejected since OpenCode consumers may not ship `.claude/`.

**Plan:**
1. Write this Work Record. 2. Port from the reviewed internal change (clean-context plan review already recorded there; scope identical). 3. Write `core/skill/opencode/agent-workflow.mjs`. 4. Wire `package-skill.sh`. 5. Phase 4 step + summary row. 6. README note. 7. Parity/fail-open check + probe require. 8. Regenerate dist + committed `.claude/skills/` mirror. 9. `bash tests/run-all.sh` green. 10. Re-run redline on the final diff. 11. Commit, push, PR, drive CI. Stop condition: any test layer red that isn't a trivial fix → return to plan.

**Verification plan:**
- Parity/fail-open → new `tests/hooks/run.sh` assertion (SEED == CTX; hook name + try/catch present).
- Plugin packaged + no drift → `tests/package/check-package.sh` + `manifest.txt` contains `opencode/agent-workflow.mjs`; committed `.claude/skills/` mirror matches dist (OSS `test` job).
- Bootstrap correctness → e2e bootstrap test still green; summary template names the plugin.
- Full suite → `bash tests/run-all.sh` (9 layers) green.
- Behavioral ("seed reaches the model under OpenCode") → **manual**: cannot run OpenCode in this environment; recorded as a manual verification note. The identical hook is proven by the running `pallium.mjs` plugin.

**Plan review:** Ported from the internal clean-context review (verdict: sound with adjustments; all three load-bearing fixes + smaller notes applied). Scope is byte-identical; no OSS-specific delta beyond host-neutral doc wording. See `## Plan review` below.

**Approvals:** Not required at this risk level (Elevated). No red-zone checkpoint fires on this diff (redline: zero checkpoints). Clean-context review satisfies the gate.

**Exceptions:** —

**State:** Ready for review
<!-- agent-workflow:end -->

## Implementation

- Ported from the reviewed internal change (same scope, host-neutral). Added `core/skill/opencode/agent-workflow.mjs` (static SEED == seed-workflow.sh CTX, `experimental.chat.system.transform`, fail-open guard). Wired `package-skill.sh`, bootstrap Phase 4 step 4.3o + Output row, bootstrap-summary row, README note, `check-install-probe.sh` require, `tests/hooks/run.sh` parity/fail-open check. Regenerated dist + committed `.claude/skills/` mirror.

## Plan review

Ported from the internal repo's clean-context review. Verdict: **sound with adjustments**. Plugin belongs at repo-root `.opencode/plugins/`, wired as a Phase 4 copy sibling to `.claude/hooks/`, packaged like the Claude hooks; drift/manifest/reference/e2e layers auto-cover it. Three load-bearing fixes applied: budget headroom (terse Phase 4 step, no ceiling bump), packager `mkdir "$TARGET/opencode"`, README link hygiene (link the in-repo source, code-span the consumer path). Smaller: fail-open `Array.isArray(output.system)` guard, pinned-format comment on SEED, `require` in the probe, corrected reinforce rationale. Scope identical to internal PR — no OSS-specific delta.

## Evidence

- `bash tests/run-all.sh` → all 9 layers ok.
- Redline final-diff verdict: GRAY (no red / boundary-violations / checkpoints).
- `python -m core.checker --slug opencode-engagement --redline-verdict <verdict>` → clean, exit 0.
- **Behavioral (manual, not CI):** the plugin uses the identical `experimental.chat.system.transform` hook proven by the running `pallium.mjs` OpenCode plugin; a live run was not executable in this environment.
