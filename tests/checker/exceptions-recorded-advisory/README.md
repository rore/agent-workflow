# Scenario: exceptions-recorded-advisory

An expanded Work Record declares Risk=Elevated/Complexity=Moderate
but the verification plan has a known gap. The Work Record records an
Exception waiving `risk.declared_not_below_detected` because — for
this PR — the agent declared Routine while the redline verdict
detected Elevated. The exception is well-formed, names a waivable
predicate, and has a future expiry.

Expected verdict: advisory (the blocking `risk.declared_not_below_detected`
failure is downgraded to advisory by the exception; the exception's
own predicates pass). Other predicates pass as normal.

Locks the slice-F downgrade behaviour as a golden.
