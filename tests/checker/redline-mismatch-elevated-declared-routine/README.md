# redline-mismatch-elevated-declared-routine

`redline: required`, verdict file parses, no boundary violation, but
redline classified one gray-zone file → detected `Elevated`. The Work
Record declares `Risk: Routine` — a deliberate mis-declaration.

Drives `risk.declared_not_below_detected` to a blocking failure. The
other two redline predicates pass cleanly.

Note: the Work Record IS the routine fast path (compact shape) because
its own declaration is `(Routine, Simple)`. The shape-matches predicate
sees nothing wrong — it gates on the *internal consistency* of the
record, not on whether the declaration is correct against reality.
Redline catches the mis-declaration via the diff, which is precisely
the predicate's purpose.
