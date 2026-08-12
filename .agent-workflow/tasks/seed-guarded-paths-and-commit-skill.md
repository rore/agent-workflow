<!-- agent-workflow:start -->
**Outcome:** A fresh clone of this repo, opened as a Claude Code project, is governed by `/agent-workflow` with no manual install step, and the plan-mode seed reminder states the repo's actual guarded paths instead of a hardcoded `src/`.

**Target:** rore/agent-workflow (this repo) — the dogfooded harness install: `.gitignore`, the seed hook, and the package-layer test suite.

**Scope:** (1) `core/skill/hooks/seed-workflow.sh` + its active copy `.claude/hooks/seed-workflow.sh` — remove hardcoded `src/`; (2) `.gitignore` — stop ignoring `.claude/skills/agent-workflow/` so the skill is committed; (3) commit the `.claude/skills/agent-workflow/` tree; (4) `tests/package/check-committed-skill.sh` (new) + `tests/package/run.sh` — drift check keeping the committed skill in lockstep with `dist/`; (5) regenerated `dist/agent-workflow/` from the fixed source; (6) *(added on reassessment)* `.github/workflows/agent-workflow.yml` — bump `actions/upload-artifact` / `download-artifact` from the retired `@v3` to `@v4`. No changes to checker logic, schemas, or SPEC.

**Constraints:** The committed skill MUST remain byte-identical to `dist/agent-workflow/` (both are packager output). The seed hook MUST stay fail-open and dependency-free (Rule 8: repo-structure-agnostic — never hardcode a consumer's layout). Consumer-repo bootstrap *mechanics* MUST be unchanged (bootstrap already commits the skill and never gitignores it) — note this refers to the commit/gitignore behavior, not the seed message itself, whose wording deliberately changes for consumers as the fix (removing the wrong hardcoded `src/`). The CI-workflow fix (added on reassessment, below) MUST NOT weaken or bypass any gate — it only restores the artifact steps to a non-deprecated action version.

**Reassessment (2026-08-12, after first CI run):** PR #1's first CI run failed — the committed `.github/workflows/agent-workflow.yml` pinned `actions/upload-artifact@v3` / `download-artifact@v3`, which GitHub retired on github.com (the file's "not supported on GHES" comment assumed a GHES host). Scope grew to include bumping both to `@v4`. This touches a **RED zone** (CI gate workflow; `architecture-review` checkpoint per `agent-redline-policy.yaml`). Risk stays **Elevated** (red → Elevated minimum; the CI gate is governance, not a contract/security/persistence/financial surface, so not forced to High). **Not a boundary violation** — the change restores the gate to a working state; it does not weaken or bypass a required check. The red-zone `architecture-review` checkpoint is satisfied by maintainer codeowner approval (or the `architecture-reviewed` label) on PR #1 — flagged for the maintainer before merge.

**Completion criteria:**
- When the seed hook fires, the injected rule names "a guarded path" (no `src/`), so it is correct for this repo (`core/`, `scripts/`) and every consumer regardless of layout.
- When `bash tests/run-all.sh` runs, the new `check-committed-skill.sh` passes (committed `.claude/skills/agent-workflow/` == `dist/agent-workflow/`) and all other layers stay green.
- When the repo is cloned fresh, `.claude/skills/agent-workflow/SKILL.md` is present (committed), so the committed `.claude/hooks/` no longer reference a missing skill.

**Risk:** Elevated

**Complexity:** Moderate

**Reason:** Redline classifies every touched path as watch (`core/**`, `.claude/skills/**`, `dist/**`) or blue (`tests/**`) — no red/gray, i.e. Routine by the table. Raised to Elevated by judgment: the seed hook is a verification-control surface that ships to every consumer, and DEFAULT_PROFILE §3 puts "changes to CI / verification controls" at at-least-Elevated. Moderate complexity — several coordinated surfaces (hook source + active copy, `.gitignore`, new test + runner wiring, regenerated `dist/` and committed skill tree).

**Discovery:** Tracing a fresh-clone edit showed the committed plan-mode gate (`check-plan.py`, reads `guarded-paths.json` → `core/`, `scripts/`) instructs the agent to invoke `/agent-workflow`, but `.claude/skills/agent-workflow/` was gitignored — a dead reference until a manual `install-skill-locally.sh`. Separately, `seed-workflow.sh` hard-coded "code under src/" in its injected message while this repo has no `src/`; the gate reads the sidecar correctly, but the *seed message* was wrong. `.claude/skills/agent-workflow/` was confirmed byte-identical to `dist/agent-workflow/` (both are `package-skill.sh` output), so committing it adds no new source of truth — only a copy to keep in sync. The hardcoded-`src/` seed also exists upstream in the internal source repo (flagged separately to the maintainer); this Work Record fixes it in the OSS copy.

**Material assumptions:**
- The committed `.claude/skills/agent-workflow/` equals `dist/agent-workflow/` — disproved if `diff -r` reports differences; action if disproved: re-run `scripts/install-skill-locally.sh` and `scripts/package-skill.sh` so both regenerate from source, then re-stage.
- Claude Code auto-loads a committed project skill from `.claude/skills/` on clone — disproved if a fresh clone does not surface `/agent-workflow`; action if disproved: revisit whether a symlink or settings pointer is needed (rejected here for Windows-checkout fragility).

**Plan:**
1. Generalize `seed-workflow.sh` message to "a guarded path" (drop `src/`); sync the active `.claude/hooks/` copy from the `core/skill/hooks/` source of truth.
2. Change `.gitignore` from `.claude/skills/` to `.claude/skills/*` + `!.claude/skills/agent-workflow/`; leave `.agents/skills/` ignored.
3. Add `tests/package/check-committed-skill.sh` (diff committed skill vs `dist/`, exit 2 on drift) and wire it into `tests/package/run.sh` right after `check-package.sh`.
4. Re-run `scripts/package-skill.sh` so `dist/` and `.claude/skills/` carry the fixed hook.
5. Commit the Work Record first, then the implementation (respect `workrecord.commit_order`).

**Verification plan:**
- Seed message correct → `grep "guarded path" .claude/hooks/seed-workflow.sh dist/agent-workflow/hooks/seed-workflow.sh .claude/skills/agent-workflow/hooks/seed-workflow.sh` (no `src/`).
- Drift check + no regressions → `bash tests/run-all.sh` all layers green, including the new `check-committed-skill.sh`.
- Skill committed & resolvable → `git ls-files .claude/skills/agent-workflow/SKILL.md` returns the path.
- Redline verdict + checker → run `scripts/agent-redline-report.py` then `python -m core.checker --slug seed-guarded-paths-and-commit-skill --redline-verdict …`; PR-time CI re-runs both.

**Plan review:** Clean-context subagent review — see `## Plan review` below.

**Approvals:** Not required at this risk level (Elevated; High-risk human approval not applicable).

**Exceptions:** —

**State:** Ready for review
<!-- agent-workflow:end -->

## Implementation

- **Assess-Risk:** redline maps all touched paths to watch/blue (Routine by table); raised to Elevated by judgment because the seed hook is a control surface shipping to consumers.
- **Plan-and-Review:** plan + clean-context review below.
- **Implement:** (1) `seed-workflow.sh` message generalized to "a guarded path", active copy synced from source; (2) `.gitignore` now commits `.claude/skills/agent-workflow/` only (other skill installs still ignored); (3) `tests/package/check-committed-skill.sh` added and wired into `run.sh`; (4) repackaged so `dist/` + committed skill carry the fix; (5) *(reassessment)* bumped the two artifact actions in `.github/workflows/agent-workflow.yml` `@v3 → @v4` after the first CI run failed on GitHub's deprecation of v3 artifact actions.
- **Verify:** see `## Evidence`.

## Plan review

Clean-context subagent review (fresh context, no planning-conversation history; read the WR + changed files and verified the load-bearing facts directly).

**Verdict: APPROVE WITH NITS** — no changes required to proceed.

Verified independently: `diff -rq .claude/skills/agent-workflow dist/agent-workflow` empty (byte-identical — core assumption holds); no `src/` in any of the three seed-hook copies and the two active copies identical; `check-committed-skill.sh` wired into `run.sh` immediately after `check-package.sh`; `.gitignore` un-ignores only `.claude/skills/agent-workflow/` so a sibling install (e.g. `.claude/skills/agent-redline/`) stays ignored while the bundled `agent-workflow/agent-redline/` sub-tree rides along.

- Classification Elevated/Moderate judged **defensible, conservative** — strictly Routine by the redline table (all watch/blue), but erring upward is right because the change ships to every consumer and alters what a fresh clone activates; the only cost is this cheap review.
- Seed-hook change **safe** — pure static-string edit; stays fail-open (`set +e`, unconditional `exit 0`) and dependency-free (`printf`).
- Drift hazard **adequately guarded** — committing the skill adds a copy, not a new source of truth; `check-committed-skill.sh` (`--strip-trailing-cr`, exit 2, `set -e` short-circuit) blocks a merge if source is edited without repackaging.
- **No unintended consumer-behavior change** — gitignore/commit mechanics are repo-local; the seed-message wording change is the deliberate fix, consistent with Hard Rule 8.

Nits (non-blocking, both addressed/expected): (1) clarified the "consumer bootstrap unchanged" constraint to mean commit/gitignore mechanics, not the message correction; (2) the "SKILL.md committed" criterion is satisfied by plan step 5 (commit) — `git ls-files` verification passes post-commit.

## Evidence

Verified on branch `fix/seed-guarded-paths-and-commit-skill` (diff vs `main`):

- **Full suite** `bash tests/run-all.sh` → all layers green (budget, schema, work-record, checker, redline, tuner, hooks, links, package), including the new `check-committed-skill.sh` confirming committed `.claude/skills/agent-workflow/` == `dist/agent-workflow/`.
- **Seed message** — `grep "guarded path"` matches in `core/skill/hooks/`, `.claude/hooks/`, and `dist/agent-workflow/hooks/` copies of `seed-workflow.sh`; no `src/` remains.
- **Skill committed** — `git ls-files .claude/skills/agent-workflow/SKILL.md` returns the path (criterion satisfied post-commit).
- **Redline reporter** on the final diff → `GRAY`, exit 1 (non-blocking shadow); 0 red, PR-size `ok`. Gray corroborates the Elevated declaration, so `risk.declared_not_below_detected` holds.
- **Checker** `python -m core.checker --slug seed-guarded-paths-and-commit-skill --redline-verdict <verdict>` → `status: clean`, exit 0; the record's predicates pass.
- **Diff hygiene** — only intended dist changes: `dist/agent-workflow/hooks/seed-workflow.sh` + regenerated `manifest.txt`; `agent-workflow-tune.py` content unchanged.
