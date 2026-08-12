# Scenario: multi-record-mixed

Two Work Records changed in one PR; one passes, one blocks (missing
required fields). Overall verdict is blocking. Locks the rule that one
record's failure does not short-circuit the others — both records'
predicate sets must run independently — and that the overall verdict
escalates to the worst per-record status.
