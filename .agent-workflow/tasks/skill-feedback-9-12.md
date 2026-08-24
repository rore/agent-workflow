# skill-feedback fixes: #9 (State hint parsed) + #12 (dangling skill-feedback link)

<!-- agent-workflow:start -->
**Outcome:**
Two skill-feedback issues resolved: (#9) a Work Record whose State field is followed by the template's allowed-values hint comment parses to a clean, valid state; (#12) the generated `docs/agent-workflow/` reference tree no longer contains a dangling `../skill-feedback.md` link.

**Target:**
agent-workflow harness — OSS (`github.com/rore/agent-workflow`).

**Scope:**
- #9: `core/work_record/parser.py` `_extract_fields` — strip HTML comments from field values; parser test in `tests/work-record/test_parser.py`.
- #12: `core/skill/bootstrap-mode.md` Phase 4.7 copy instruction; `tests/budget/budget.yaml` ceiling for bootstrap-mode.md.
- Regenerated artifacts: `dist/agent-workflow/**`, `.claude/skills/agent-workflow/**`, and `.agents/skills/agent-workflow/**` (the bundled `agent-workflow-check.py` is rebuilt from `core/checker/`, which imports the parser).

**Constraints:**
- Source `core/templates/checkpoints/review-result.md` link (`../skill-feedback.md`) stays unchanged — it is correct for the skill tree; #12 is a bootstrap copy-layout fix, not a source-link fix.
- No behavior change to any valid existing Work Record. Structural markers (`agent-workflow:start/end`) are outside the extracted block and unaffected.
- bootstrap-mode.md stays within its token ceiling.

**Completion criteria:**
- A record with `**State:** Ready for review` followed by `<!-- Ready to implement | Blocked | Ready for review -->` passes `workrecord.state_valid`.
- Following the Phase 4.7 instruction produces a docs tree where `../skill-feedback.md` from the copied review-result.md resolves to an existing file.
- `bash tests/run-all.sh` green (parser, budget, package-drift layers included).

**Risk:** Elevated

**Complexity:** Moderate

**Reason:**
Redline pre-edit verdict on intended scope = GRAY (parser.py, bootstrap-mode.md gray; test blue; no red zone, no boundary violation, no required checkpoints). Gray → Elevated (conservative default); not High — no contract/security/persistence/financial surface. Moderate: two distinct fixes across parser code + bootstrap doc + tests + regenerated package.

**Discovery:**
- #9 root cause: `_extract_fields` captures each field value from its `**Label:**` header to the next header; for the last field (State) `value_end = len(block)`, so the value swallows the trailing hint comment on the following line. `.strip()` trims whitespace only, not the comment, so `workrecord.state_valid` sees `"Ready for review\n<!-- ... -->"` and blocks.
- `_extract_block` returns the substring strictly between markers (markers excluded), so stripping HTML comments from field values cannot touch the structural markers.
- #12 root cause: Phase 4.7 flattened `templates/checkpoints/*.md` into `docs/agent-workflow/`, dropping the `checkpoints/` subdir. The copied review-result.md keeps `../skill-feedback.md`, which in the flattened tree points at `docs/skill-feedback.md` (never generated). `skill-feedback.md` lives one level up in `templates/`, so it is not swept by the `checkpoints/*.md` copy.
- Packaging: `parser.py` is not shipped as a file; the checker is rebuilt into a single `agent-workflow-check.py` at package time, so the #9 change requires a repackage.

**Material assumptions:**
- A1: No valid field value legitimately contains an HTML comment as meaningful content. Disproof: a checker/parser test asserting a comment-bearing value. Action if disproved: narrow the strip to trailing comments only. (Comments in the marker block are always hints or structural markers — assumption holds.)
- A2: Preserving the skill's template layout under `docs/agent-workflow/` (checkpoints/ subdir + skill-feedback.md sibling) makes every relative link that resolves in the skill tree resolve in the docs tree. Disproof: a checkpoint doc with a link that only works when flattened. Action: rewrite that link during copy. (Only `../skill-feedback.md` is checkpoint-adjacent; `../../skill/` refs point at skill machinery absent from any docs tree and are out of scope.)

**Plan:**
1. #9: add module-level `_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)`; in `_extract_fields` strip it from the value before `.strip()`. Add a parser test.
2. #12: rewrite Phase 4.7 to copy `templates/checkpoints/` preserving the subdir **and** `templates/skill-feedback.md`, mirroring layout so `../skill-feedback.md` resolves; bump `tests/budget/budget.yaml` bootstrap-mode ceiling 4500→4600 with a why-note.
3. Repackage via `scripts/package-skill.sh`; commit regenerated dist/ + skill mirrors.
4. Run `tests/run-all.sh`; confirm all layers ok.

**Verification plan:**
- #9 → new `tests/work-record/test_parser.py` case (comment-after-State parses clean) + `tests/checker` state_valid still green.
- #9 no-regression → full `tests/work-record` pytest.
- #12 → re-read of Phase 4.7 wording; `tests/budget` green post-bump; `tests/links` green.
- Package drift → `tests/package` green after repackage.
- Whole suite → `tests/run-all.sh` green.

**Plan review:**
Clean-context review returned SOUND-WITH-ADJUSTMENTS. Two adjustments: (1) audit inbound bare-filename links before commit — done, only `review-result.md → ../skill-feedback.md` (fixed) and `skill-feedback.md → checkpoints/review-result.md` (kept working by the subdir); (2) make Phase 4.7 copy-source explicit, naming `templates/skill-feedback.md` and `templates/checkpoints/` — done in the updated wording.

**Approvals:**
Not required at this risk level (Elevated).

**Exceptions:**
—

**State:** Ready for review
<!-- agent-workflow:end -->

## Implementation

- #9: added module-level `_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)` in `core/work_record/parser.py`; `_extract_fields` now strips it from each field value before `.strip()`. Shared fix — repairs every field, not just State. Structural markers are outside the extracted block, so they are untouched.
- #9 test: `tests/work-record/test_parser.py::test_template_hint_comments_are_stripped_from_field_values` — a record with hint comments after both Risk and State parses to clean values.
- #12: rewrote `core/skill/bootstrap-mode.md` Phase 4.7 to copy `templates/checkpoints/` preserving the `checkpoints/` subdir **and** `templates/skill-feedback.md` as a sibling, so the docs tree mirrors the skill tree and `../skill-feedback.md` resolves.
- #12: bumped `tests/budget/budget.yaml` bootstrap-mode.md ceiling 4500→4600 with why-note.
- Repackaged via `scripts/package-skill.sh` — regenerated `dist/agent-workflow/`, `.claude/skills/`, and `.agents/skills/` mirrors (all committed in OSS repo).

## Plan review

Clean-context review (Sonnet, read-only, no planning context): **SOUND-WITH-ADJUSTMENTS**.
- A (strip mechanics): correct — value is already sliced per-field before stripping, so a `**Label:**` inside a comment cannot confuse the header regex; non-greedy DOTALL handles multi-line; strip-before-`.strip()` order is right.
- B (altitude): correct — `_extract_fields` is the sole raw→value path; fixing there repairs all fields.
- C (subdir resolves link): arithmetic correct. Adjustment 1: audit inbound bare-filename links before commit. **Done** — only checkpoint links are `review-result.md → ../skill-feedback.md` (fixed) and `skill-feedback.md → checkpoints/review-result.md` (kept working by the subdir).
- D (classification): (Elevated, Moderate) confirmed sound. Adjustment 2: make Phase 4.7 copy-source explicit. **Done** — wording names `templates/skill-feedback.md` and `templates/checkpoints/`.

## Evidence

- `python -m pytest tests/work-record -q` → 49 passed (incl. the new #9 regression test).
- `bash tests/budget/check-budget.sh` → all 17 files within budget (post-4600 bump).
- `bash tests/run-all.sh` → all 9 layers ok (budget, schema, work-record, checker, redline, tuner, hooks, links, package). Package-drift layer green after repackage.
