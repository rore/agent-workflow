# redline-boundary-violation

`redline: required`, verdict file present and parses, but reports one
boundary violation. Drives `risk.boundary_violation_absent` to a
blocking failure with the rule named.

`risk.declared_not_below_detected` skips (passed=true, blocking=true,
"skipped — boundary violation already blocks") so the PR comment names
exactly one redline blocker.

The Work Record is `(Elevated, Simple)` — well-formed expanded shape,
matching the gray zone redline detected. Risk-level comparison would
have passed; the boundary violation is the standalone gate.
