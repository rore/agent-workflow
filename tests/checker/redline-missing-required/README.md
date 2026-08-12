# redline-missing-required

`redline: required` in the per-repo config and no verdict file at the
configured path. Drives `risk.redline_findings_available` to a blocking
failure with the "CI configuration error" detail. The boundary and
declared-vs-detected predicates skip cleanly (passed=true with a
"skipped — redline verdict unavailable" detail) because the previous
predicate already names the root cause.

The Work Record itself is well-formed `(Routine, Simple)` — every
slice-A predicate passes. The block is entirely on the missing
verdict.
