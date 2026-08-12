# redline-missing-optional

`redline: optional` in the per-repo config and no verdict file. Drives
`risk.redline_findings_available` to an **advisory** failure (passed
false, blocking false). The remaining redline predicates skip cleanly.

Aggregate verdict stays `advisory` because no blocking predicate
failed — the explicit opt-out is the contract: redline is encouraged
but not required.
