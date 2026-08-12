<!-- agent-workflow:start -->
**Outcome:**
`LICENSE` holds the full, verbatim Apache-2.0 text so GitHub's license detector recognizes the repo as Apache-2.0 (it previously showed "Other").

**Target:**
agent-workflow repository — `LICENSE` file and GitHub's repository license metadata.

**Scope:**
`LICENSE` only.

**Constraints:**
No code change; guarded paths (`core/`, `scripts/`) untouched. The license itself does not change — Apache-2.0 before and after; only the file's text is completed from the abbreviated notice to the canonical full text. Copyright attribution to Rotem Hermon preserved.

**Completion criteria:**
`LICENSE` contains the verbatim canonical Apache-2.0 body; GitHub license detection reports Apache-2.0; CI checks on PR #2 (`test`, `redline`, `agent-workflow`) are green.

**Risk:** Elevated

**Complexity:** Simple

**Reason:**
Redline classified `LICENSE` as a gray-zone path → Elevated (conservative default per the redline→Risk table; may not be lowered). Simple: a single-file, one-session change.

**Discovery:**
GitHub showed the license as "Other" because `LICENSE` held an abbreviated Apache-2.0 notice, not the full text GitHub's `licensee` detector matches against. The canonical text was fetched from apache.org. Note the two-layer governance: the guarded-path hook only fires for `core/`/`scripts/` (so it did not force the skill for `LICENSE`), but the CI checker's `workrecord.required_for_branch_changes` requires a Work Record for any file-touching PR — which is why this record exists.

**Material assumptions:**
- GitHub's `licensee` detects Apache-2.0 from the full canonical body. Disproof: repo still shows "Other" after merge. Action: check for stray edits to the license body.
- Filling the appendix line `Copyright 2026 Rotem Hermon` does not break detection (`licensee` ignores the appendix). Disproof: detection fails. Action: restore the appendix placeholder text.

**Plan:**
Replace the `LICENSE` body with the verbatim Apache-2.0 text from apache.org; fill the appendix copyright line with `Copyright 2026 Rotem Hermon`. One commit on `docs/apache-2.0-license`; PR to `main`. Stop condition: if redline escalates the path beyond gray, reassess before merge.

**Verification plan:**
- "Full text present" → diff review + line count (202 lines).
- "License detected as Apache-2.0" → GitHub license API after merge.
- "CI green" → PR #2 checks: `test`, `redline`, `agent-workflow`.

**Plan review:**
self — retroactive Work Record for a single-file, verbatim canonical-text replacement. A clean-context review was not warranted for the content; the `workrecord.commit_order` advisory is expected to fire because the code commit preceded this record.

**Approvals:**
Not required at this risk level.

**Exceptions:**
—

**State:** Ready for review
<!-- agent-workflow:end -->

## Implementation

- Replaced `LICENSE` (abbreviated Apache-2.0 notice) with the verbatim canonical Apache-2.0 text fetched from apache.org; filled the appendix copyright line with `Copyright 2026 Rotem Hermon`. Committed as `a01fc32` on `docs/apache-2.0-license`, pushed, opened PR #2.
- This Work Record was added retroactively after the checker flagged the branch — recorded honestly rather than backdated.

## Evidence

- PR: https://github.com/rore/agent-workflow/pull/2
- CI on commit `a01fc32`: `test` ✅, `redline` ✅ (gray — cautious review), `agent-workflow` ⛔ (blocked pending this Work Record; expected to pass once this record lands).
- `LICENSE` line count: 202; copyright line at L190 (`Copyright 2026 Rotem Hermon`).
