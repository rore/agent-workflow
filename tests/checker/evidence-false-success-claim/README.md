# Scenario: evidence-false-success-claim

Record whose Evidence prose claims that `WalletRetryTest` passed
*after* an earlier ❌ FAILED marker for the same identifier. The
predicate detects the contradiction and surfaces advisory.

The predicate is advisory per the slice-E stop condition (see the
slice-E Work Record for rationale) — the structural signal stays in
the verdict, but legitimate descriptive prose doesn't block PRs.
A follow-up will refine detection and re-promote to blocking.
