<!-- agent-workflow:start -->
**Outcome:** Review-evidence gates reject placeholder values that do not identify a review, revision, or adequacy assessment.

**Target:** agent-workflow repository.

**Scope:** Shared review-evidence parser, focused checker regression tests, and regenerated distribution.

**Constraints:** Preserve acceptance of valid review references and the distinction between attested evidence and verified reviewer identity. Do not change policy or workflow requirements.

**Completion criteria:** Elevated/High plan and result gates reject `unknown` and `not provided`, accept real references, and the packaged checker passes the repository suite.

**Requirement baseline:**
{"source":"Pallium PR #250 CodeRabbit inline review 4106872028 and user bug-fix instruction","outcome":"Review-evidence gates reject placeholder values that do not identify a review, revision, or adequacy assessment.","scope":"Shared review-evidence parser, focused checker regression tests, and regenerated distribution.","constraints":"Preserve acceptance of valid review references and the distinction between attested evidence and verified reviewer identity. Do not change policy or workflow requirements.","completion_criteria":"Elevated/High plan and result gates reject `unknown` and `not provided`, accept real references, and the packaged checker passes the repository suite."}

**Risk:** Routine

**Complexity:** Simple

**Reason:** Source and generated checker are watched but blue under the zone-only policy; this is one parser guard and focused test.

**Approach:** Extend the existing placeholder predicate in the shared parser, add a parameterized regression to the existing review-evidence test, regenerate dist, and re-sync Pallium from the corrected source.

**Verification:** Focused checker review-evidence test and `bash tests/run-all.sh`; package check; PR CI.

**State:** Ready to implement
<!-- agent-workflow:end -->

## Implementation

Isolated branch `feat/reject-review-placeholders` from upstream `origin/main` at 7d6d46d. Pallium PR #250 remains unmerged while this source defect is corrected.
