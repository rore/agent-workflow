# Scenario: exceptions-against-boundary

An expanded Work Record records an Exception whose `rule` names
`risk.boundary_violation_absent` — a non-waivable predicate per SPEC
§11. The checker fails `exceptions.not_against_boundary` (blocking).
The exception is NOT honoured by the downgrade pass; any actual
boundary violation continues to block.

This fixture intentionally pairs the non-waivable exception with a
clean redline verdict so the test isolates the exception-validity
predicate. The verdict is blocking solely because of the bad
exception.
