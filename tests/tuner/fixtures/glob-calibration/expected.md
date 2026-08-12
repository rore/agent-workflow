## Calibration suggestions

Each red rule was checked against the recent merged PRs to see how often it fires. Rules firing very often (>70%) may produce alert fatigue; rules firing zero times may be misconfigured.

| Path | Firing rate | Suggestion |
|---|---|---|
| `src/main/java/**/*Controller.java` | 1/3 (33%) | Keep as-is |
| `src/main/java/**/infrastructure/external/**` | 1/3 (33%) | Keep as-is |


## Proposed `.github/CODEOWNERS`

Based on inspection of the last 3 approvals across the recent merged PRs:

```
# Default codeowner: @ACME/acme-team accounts for 3/3 approvals (100%).
*    @ACME/acme-team
```

**Apply with:** a maintainer commits this file at `.github/CODEOWNERS`, then enables `Require Code Owner review` in branch protection.

