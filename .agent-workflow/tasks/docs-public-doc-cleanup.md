<!-- agent-workflow:start -->
**Outcome:**
Public-facing docs carry no dead references and no internal contradictions, and the top-level `README.md` is legible to a newcomer within a minute. Specifically: no reference to the non-existent `rore/agent-workflow-demo` repo survives anywhere in the repo; no doc points a reader at a `DECISIONS.md` entry that does not exist; and `README.md` is restructured to lead with problem → how it works → a concrete Work Record example → quick start → what CI enforces → what it can't prove → risk model → docs map, with internal-development vocabulary removed and two first-screen overclaims tightened.

**Target:**
agent-workflow repository — the top-level `README.md`, narrative docs, and the code/fixture comments that reference the demo repo.

**Scope:**
- `README.md` — (a) remove the "See it on a real PR" section (dead demo-repo link); (b) **restructure** for a newcomer: reorder to lead with problem/value and a concrete short Work Record example; add a 5-step quick start high up; add an explicit agent-compatibility statement; move reference detail (zone table, shadow/binding, exit codes, config YAML) down to the already-existing linked docs; cut internal vocab (`slice W18`, `engineering-change slice`); tighten "blocks the merge" and "contradicted by the actual diff". No claim the docs don't already support.
- `.gitattributes` — drop the demo-repo clause from a comment.
- `scripts/build-vendored-checker.sh` — drop the demo-repo clauses from the header comment.
- `tests/fixtures/work-record/expanded-pass/work-record.md` — drop the demo-repo clause from fixture prose.
- `docs/ENFORCEMENT.md`, `docs/skill-rationale.md` — reword the two citations that point at a non-existent "2026-06-23" DECISIONS.md entry so they no longer imply a log entry exists (no backfill, per developer instruction).
- `docs/SPEC.md` — drop "Jira," from the L8 profile-mapping parenthetical for consistency with DEFAULT_PROFILE.md.

**Constraints:**
No behavioral/code change — comment and prose text only. No change to the checker, reporter, or any executable logic. `docs/SPEC.md` normative content unchanged (the edit is one word in a non-normative parenthetical). Do not add DECISIONS.md entries.

**Completion criteria:**
- `grep -ri "agent-workflow-demo\|demo repo\|companion demo" .` returns no matches outside this Work Record.
- No doc cites a dated DECISIONS.md entry while DECISIONS.md says "No entries yet."
- `docs/SPEC.md` L8 parenthetical matches DEFAULT_PROFILE.md's framing.
- `README.md` opens with problem/value, shows a Work Record example and a 5-step quick start before the reference material, states agent compatibility explicitly, and contains no `slice W18` / `engineering-change slice` vocab.
- `bash tests/run-all.sh` passes (fixture edit must not break expanded-pass; README internal links must all resolve via the `links` stage).

**Risk:** Elevated

**Complexity:** Moderate

**Reason:**
Redline classifies `docs/SPEC.md` as red (architecture-review checkpoint) and `.gitattributes` as gray → Elevated (conservative default per assess-risk table; may not be lowered). `README.md` is blue and adds no risk. Complexity bumped Simple→Moderate on the mid-task scope expansion: the README restructure is public-facing and carries real wording/accuracy uncertainty (must not introduce overclaims or drop information the linked docs don't already carry), though it stays one repo / one session.

**Discovery:**
- `rore/agent-workflow-demo` does not exist: `gh repo view rore/agent-workflow-demo` returns "Could not resolve to a Repository". Every reference to it is therefore dead.
- Four references found: `README.md` §"See it on a real PR" (public link), `.gitattributes:22-23`, `scripts/build-vendored-checker.sh:9-10`, `tests/fixtures/work-record/expanded-pass/work-record.md:8`.
- `docs/DECISIONS.md` contains only "_No entries yet._", yet `docs/ENFORCEMENT.md:118` ("Per the 2026-06-23 decision…") and `docs/skill-rationale.md:43` ("(DECISIONS.md 2026-06-23)…") cite it as a source. Reader-facing contradiction.
- All 13 `core/…` paths referenced by the narrative docs resolve — no other broken links found.
- Redline runs in `shadow` (advisory) on this repo, so the SPEC red-zone/architecture-review checkpoint surfaces in the sticky but does not block; `risk.declared_not_below_detected` still requires declared Risk ≥ Elevated.
- **Scope expansion (mid-task):** developer directed a full README restructure, prompted by an external agent's README review. That review's central recommendation — elevate the demo repo — is discarded (the repo does not exist). Adopted, sound recommendations: quick-start near the top, show the Work Record artifact early, cut internal jargon, state agent compatibility explicitly, tighten two first-screen overclaims, move reference detail into the already-existing docs. Returned to planning per the material-scope-expansion rule.

**Material assumptions:**
- The fixture prose at `tests/fixtures/.../work-record.md` is not asserted against by any test (only the marker-block fields are). Disproof: `tests/run-all.sh` fails after the edit. Action: revert the fixture line and leave its demo-repo clause, or adjust to satisfy the assertion. (Confirmed by clean-context review: the demo sentence sits above the marker block; the parser never reads it.)
- Rewording (not deleting) the two DECISIONS citations preserves each sentence's technical claim. Disproof: a reworded sentence changes what the checker/rationale actually does. Action: keep the factual clause, drop only the "per the DECISIONS.md entry" pointer.
- The README restructure only moves/compresses content that the linked docs (INTEGRATION, ENFORCEMENT, REDLINE, SPEC) already cover in full. Disproof: a fact lives only in the README and would be lost. Action: keep that fact in the README or confirm it exists in the target doc before cutting.

**Plan:**
1. `/agent-workflow` + Work Record (this file) — done before any edit.
2. Clean-context plan review (Elevated) — done for the original cleanup scope; recorded under `## Plan review`.
3. Edit the four demo-repo references (delete README section; strip demo clause from the three comments/prose). — done.
4. Reword the two DECISIONS citations to drop the dead pointer while keeping the technical claim. — done.
5. Drop "Jira," from SPEC.md L8. — done.
6. Verify cleanup: grep sweep + `tests/run-all.sh`. — done (package stage via pyshim).
7. **README restructure** (expanded scope): rewrite `README.md` to the newcomer-first shape in Scope. Follow the developer-approved outline from the external review (minus the demo recommendation). Keep every internal link resolving; introduce no claim not already supported by the docs.
8. **Clean-context review of the drafted README** (repeats the Elevated plan review for the expanded scope): fresh Explore agent checks factual accuracy, overclaims, newcomer-legibility, and link integrity. Record under `## Plan review`.
9. Apply review fixes.
10. Verify: `tests/run-all.sh` (incl. `links` stage) via pyshim; grep README for residual internal vocab.
Stop condition: if the restructure would drop a fact not carried by the linked docs, or introduce an unsupported claim, pause and return here.

**Verification plan:**
- No demo-repo reference survives → `grep -ri "agent-workflow-demo\|demo repo\|companion demo"` returns only this Work Record.
- No dead DECISIONS pointer → manual re-read of the two reworded lines; DECISIONS.md still "No entries yet" and nothing points at a dated entry.
- SPEC parenthetical consistent → diff review against DEFAULT_PROFILE.md framing.
- README newcomer-legible, accurate, no overclaims → clean-context Explore review of the drafted README.
- README internal links resolve → `links` stage of `tests/run-all.sh`.
- Internal vocab gone → `grep -n "W18\|engineering-change slice" README.md` returns nothing.
- Nothing broke → `bash tests/run-all.sh` green (package stage via working `python3`).

**Plan review:**
Original cleanup scope: clean-context Explore subagent (Elevated) — sound, two cautions. Expanded scope (README restructure): clean-context review repeated against the drafted README. Both recorded under `## Plan review` below.

**Approvals:**
Not required at this risk level.

**Exceptions:**
—

**State:** Ready for review
<!-- agent-workflow:end -->

## Plan review

Clean-context Explore subagent, read-only, no prior context. Verdict: **plan is sound as written**, with two implementation cautions:

1. **`.gitattributes`** — the demo clause is only in the line-22 comment; line 23 (`scripts/agent-workflow-check.py text eol=lf`) is a functional rule. Edit the comment text only; do not touch the rule. (Discovery's ":22-23" range was imprecise.)
2. **`scripts/build-vendored-checker.sh`** — the second demo clause (lines 10-11) carries the *why-we-rebuild* rationale ("so the demo repo and the dev repo do not drift"). Reword to preserve the "keep the vendored copy in sync with source" point rather than deleting it.

Confirmed: scope lists every demo-repo reference (no misses); both DECISIONS rewords are safe with the load-bearing claims identified (ENFORCEMENT: presence-of-approval enforced, authorship not verified, cheating window acknowledged; skill-rationale: High-risk approvals self-attested, traceability-not-identity tradeoff); no test/checker/link-checker/anchor couples to the changed text (the fixture's demo sentence sits above the marker block, so the parser never reads it). Residual "2026-06-23 decision" mentions in `core/checker/predicates.py` are code comments, out of scope for a reader-facing doc cleanup.

### Expanded scope — README restructure

Repeated the Elevated clean-context review against the *drafted* README (fresh Explore agent, verified against SPEC/ENFORCEMENT/REDLINE/INTEGRATION/PACKAGING/DEFAULT_PROFILE + both config files). Verdict: newcomer test passes, links resolve, tone clean — with three accuracy nits, all fixed:
1. The Work Record example declared `(Elevated, Moderate)` but showed fewer fields than the expanded shape requires → would fail `workrecord.shape_matches_classification`. Rewritten as a valid `(Routine, Simple)` compact record.
2. "any triggered review checkpoint is satisfied" was listed flatly as blocking, but `review.checkpoints_satisfied` is advisory under shadow (the default) → scoped to binding mode.
3. "compact form for routine work" → "`(Routine, Simple)` work".

Two further review rounds from the developer's external reviewers, adopted as precision edits (no restructuring):
- Round 2: "the harness won't advance" → guidance-vs-enforcement wording; "A short one" → "A simplified example"; Redline paragraph reworked to "declared intent at planning / deterministic diff classification at PR time" (there is no diff before implementation). **Declined** the reviewer's proposed "Project status" metrics — the specific numbers (66 tasks, 28 reviews, 17 findings) were not substantiated by any measurement I can verify; adding them would violate the honesty constraint.
- Round 3: restored **visibility** as a headline capability (it had been demoted to an enforcement fallback in the first draft) — added a compact "What you get" triad (durable state / risk-aware visibility / objective gates) and tied the reviewer bullet to risk-driven attention. Faithful to the original README's first-class-visibility framing; no new claim.
- Round 4 (precision): "stays visible" → "recorded and surfaced"; Problem closer now names the risk/visibility dimension ("uses risk to focus reviewer attention"); "govern" → "trust" (less enterprise-toned); and the bootstrap-consent sentence made exact — "Bootstrap asks before installing the CI workflow; branch-protection and CODEOWNERS changes are proposal-only — you apply them yourself" (matches INTEGRATION.md: CI written on explicit yes; the other two proposal-only, no admin access).

## Implementation

- Removed the `## See it on a real PR` section from `README.md` (dead `rore/agent-workflow-demo` link), collapsing the two horizontal rules into one before `## Where to read more`.
- `.gitattributes` — reworded the line-22 comment ("consuming repos invoke it with `python`"), leaving the line-23 `eol=lf` rule untouched.
- `scripts/build-vendored-checker.sh` — reworded the header comment to keep the don't-drift-from-source rationale ("a consumer's vendored copy does not drift from the checker source in this repo") without the demo repo.
- `tests/fixtures/work-record/expanded-pass/work-record.md` — dropped the "and the demo repo's first PR scenario" clause from prose above the marker block.
- `docs/ENFORCEMENT.md` — reworded the "human actually wrote a given approval" bullet to drop the "Per the 2026-06-23 decision" pointer while keeping the claim (presence enforced, authorship not verified, cheating window acknowledged).
- `docs/skill-rationale.md` — reworded to drop "(DECISIONS.md 2026-06-23)" while keeping the self-attested / traceability-not-identity claim.
- `docs/SPEC.md` L8 — dropped "Jira," from the non-normative profile-mapping parenthetical.

No `core/skill/`, `core/templates/`, redline-subtree, or vendored-script source changed, so `dist/` did not drift.

### README restructure (expanded scope)

- Rewrote `README.md` to the newcomer-first shape: positioning line → what it is → value/visibility → scope boundary → "what it runs on" (agent-compatibility) → Problem → What you get (triad) → How it works (pipeline + dev/PR/reviewer lenses) → checkpoints → Work Record (with a valid compact example) → Quick start (5 steps) → What CI enforces → What it can't prove → Risk-aware workflow → Documentation table.
- Cut internal vocab (`slice W18`, `engineering-change slice`), moved the zone table / shadow-binding detail / exit codes / config YAML / local-check command out to the already-existing docs (linked), and kept every internal link resolving.
- Applied clean-context-review + two external-review rounds as precision edits (see `## Plan review`): valid `(Routine, Simple)` example, checkpoint-satisfied scoped to binding, guidance-vs-enforcement wording, Redline "intent-first / diff-later" framing, and visibility restored as a headline capability. Declined unverifiable "Project status" metrics.

## Evidence

- Demo-repo sweep: `grep -rin "agent-workflow-demo\|companion demo\|demo repo"` returns matches only inside this Work Record. ✅
- DECISIONS alignment: both citations reworded; `docs/DECISIONS.md` still "No entries yet" and no doc points at a dated entry. ✅
- README internal-vocab check: `grep -n "W18\|engineering-change slice" README.md` → clean. ✅
- README links + drift: `bash tests/run-all.sh` (via a `python3`→CPython shim, since this machine's `python3` is broken) → **EXIT 0**, all nine stages green including `links` (README references resolve) and `package` (dist matches sources; no drift). ✅
- Files changed: `README.md`, `.gitattributes`, `scripts/build-vendored-checker.sh`, `tests/fixtures/work-record/expanded-pass/work-record.md`, `docs/ENFORCEMENT.md`, `docs/skill-rationale.md`, `docs/SPEC.md` + this Work Record.
- Not committed — held on branch `docs/public-doc-cleanup` per developer instruction (may want more changes).

## Result review

_Pending — PR review (not yet opened)._
