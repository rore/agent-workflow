# agent-redline reference

The risk-classification subsystem bundled inside agent-workflow. This page covers the full feature set and configuration; the consumer-facing tuning workflow is in [`INTEGRATION.md`](INTEGRATION.md#risk-classification-and-how-to-keep-it-useful).

Lives under `core/agent-redline/` in this repo. Vendored from `github.com/rore/agent-redline` (see [`core/agent-redline/BASELINE.md`](../core/agent-redline/BASELINE.md) for the snapshot baseline and manual-port workflow). Treat it as an internal component of agent-workflow — consumers do not install it separately; bootstrap installs both together.

## What it does

Two surfaces:

- **Skill side (pre-edit).** The agent reads `agent-redline-policy.yaml` before any change. It classifies the intended change as blue / red / gray / boundary-risk and slows down or refuses accordingly. The skill body is loaded by agent-workflow's [`assess-risk`](../core/templates/checkpoints/assess-risk.md) checkpoint.
- **CI side (post-PR).** A single-file Python reporter (`scripts/agent-redline-report.py`, vendored from `core/agent-redline/core/reporter/`) runs against the PR diff, emits a verdict JSON, and posts a sticky comment. agent-workflow's checker reads the verdict and surfaces it through its own predicates.

The skill closes the "agent took the local shortcut before CI could catch it" gap; the reporter closes the "agent missed its own discipline" gap. They are not redundant — they fire on different sides of the edit.

## The classification model

Every changed file lands in exactly one **zone**, and may additionally carry one or more **watch** tags.

| Zone | Meaning | Effect on the verdict |
|---|---|---|
| **Blue** | Autonomous-safe: tests, docs, isolated/replaceable code. | None — proceed. |
| **Red** | Structurally consequential: contracts, modeling, security, persistence, shared behavior. | Raises verdict to `RED`. May trigger a checkpoint. |
| **Gray** | Unclassified (didn't match any red or blue glob). | Raises verdict to `GRAY`. Surfaces in the sticky; signal to extend the policy. |
| **Watch** | Additive tag (not a zone). | Path surfaces in the sticky regardless of zone. No checkpoint, no merge gate. Pure visibility. |

Plus three "vertical" change signals that are independent of the path-based zone:

| Signal | Detected by | Triggers |
|---|---|---|
| **API change** | `api.type` block — `openapi-spec-file` / `openapi-from-controllers` / `graphql` / `proto` | `api-review` checkpoint |
| **Schema change** | `persistence.migrationPaths` | `persistence-review` checkpoint |
| **Security change** | `security.paths` | `security-review` checkpoint |
| **Runtime-config change** | `runtimeConfig.paths` | `ops-review` checkpoint |

And one terminal state:

| State | Meaning |
|---|---|
| **Boundary violation** | A forbidden cross-layer dependency was added (e.g. `domain` importing `adapter`). Stops the workflow before planning; never waivable through a task exception. CI exits non-zero; PR cannot merge. |

The combined verdict the reporter posts is one of `BLUE`, `GRAY`, `RED`, `MIXED`, or `BOUNDARY_VIOLATION` — the most-restrictive applicable signal wins.

## Checkpoints

A checkpoint is required human attention. **Triggered** when the diff hits any signal the policy associates with that checkpoint — a red-zone path that names the checkpoint (the `checkpoint:` field on a zone entry), or a vertical-signal block that names it (`api.checkpoint`, `persistence.checkpoint`, `security.checkpoint`, `runtimeConfig.checkpoint`). Once triggered, the checkpoint must be **satisfied** before the PR can merge. Defined under `checkpoints:` in the policy; `satisfiedBy:` uses OR-semantics.

| Entry | Satisfied when |
|---|---|
| `codeownerApproval` | A CODEOWNER for any of the touched red-zone paths approves the PR. |
| `label: <name>` | The named label is applied to the PR. |

Built-in checkpoint IDs the policy can reference: `architecture-review`, `api-review`, `persistence-review`, `security-review`, `ops-review`. You can define others.

agent-workflow's checker reads the reporter's already-computed `satisfied` field for each triggered checkpoint via the `review.checkpoints_satisfied` predicate. It does not re-implement satisfaction logic.

## The policy file

`agent-redline-policy.yaml`. Schema reference below; the full normative schema lives in agent-redline's upstream docs but the shape that ships here is what bootstrap writes.

```yaml
version: 1

project:
  name: <repo-name>
  extension: <extension-name>           # optional; jvm-archunit | python | other; omit for zone-only

zones:
  red:
    - path: <glob>                      # required
      reason: <string>                  # required; surfaced in sticky
      checkpoint: <checkpoint-id>       # optional; the checkpoint a red-zone change must satisfy
  blue:
    - path: <glob>
      reason: <string>
  watch:                                # additive tag; surfaces touched paths regardless of zone
    - path: <glob>
      reason: <string>
  # Files not matched by red/blue/watch are gray.
  # Red and blue are exclusive zone classifications; watch composes with all three.

boundaries:                             # deterministic dependency rules
  - id: <kebab-case>
    description: <string>
    from: <glob>
    forbidImports: [<glob>, ...]
    severity: error                     # error | warn (default: error)

api:                                    # optional
  type: openapi-spec-file               # openapi-spec-file | openapi-from-controllers | graphql | proto | none
  specPath: <path>                      # for static-spec types
  generationCommand: <string>           # for openapi-from-controllers
  diffMode: structural                  # structural | full
  checkpoint: api-review

persistence:                            # optional
  migrationPaths: [<glob>, ...]
  checkpoint: persistence-review

security:                               # optional
  paths: [<glob>, ...]
  checkpoint: security-review

runtimeConfig:                          # optional
  paths: [<glob>, ...]
  checkpoint: ops-review

prRules:                                # optional; defaults shown
  maxChangedFiles: { warn: 50, fail: 100 }
  maxLinesChanged: { warn: 1000, fail: 2000 }

checkpoints:                            # required if any zone references one
  architecture-review:
    description: <string>               # optional
    satisfiedBy:
      - codeownerApproval
      - label: architecture-reviewed

modes:                                  # see "Shadow vs binding" below
  default: shadow                       # shadow | binding (default: shadow)
  perCheck:
    boundary_violation: binding         # hardcoded default; almost always binding from day one
    pr_size: shadow
    report: shadow
    suppression: binding                # hardcoded default

excludes:                               # optional; paths excluded from all classification
  - <glob>

boundaryAdapter:                        # how the backend's output is read by the reporter;
                                        # bootstrap copies this from the chosen extension
  outputFormat: junit-xml               # junit-xml | json-violations | none
  outputPath: <path-or-glob>

suppressions:                           # optional; absence => suppression detection OFF
  useExtensionDefaults: true            # default within the block
  add: { inlineComments: [...], annotations: [...], configEdits: [...] }
  remove: { ... }
  exemptPaths: [<glob>, ...]            # typically "**/tests/**"
```

### Validation rules

A policy is invalid if:

1. `version` is missing or not `1`.
2. `project.name` is missing.
3. Both `zones.red` and `zones.blue` are empty.
4. A `checkpoint:` reference points to an undefined checkpoint.
5. A `boundaries[].forbidImports` is empty.
6. A `boundaries[].id` is duplicated.
7. The policy does not protect its own architecture-test directory (e.g. `src/test/**/architecture/**`) as a red zone.
8. A glob is malformed.
9. A non-empty `boundaries:` block exists without an explicit `boundaryAdapter:` block.

Bootstrap produces a valid policy. The reporter refuses to run on an invalid policy with a clear error.

### Glob syntax

Standard shell globs: `*`, `**`, `?`, `[abc]`, `[!abc]`. **Brace expansion is not supported.** Use multiple entries instead. Paths are repo-relative.

## Shadow vs binding

`modes.default` is the fallback for all rule modes; `modes.perCheck` overrides per rule.

| Rule | Used to decide | Default |
|---|---|---|
| `boundary_violation` | Whether reported boundary violations fail the check | `binding` (hardcoded) |
| `suppression` | Whether suppression markers on guarded surfaces fail the check | `binding` (hardcoded) |
| `report` | Whether unmet required checkpoints fail the check | follows `modes.default` |
| `pr_size` | Whether exceeding `prRules.*.fail` fails the check | follows `modes.default` |

Important: `modes.default: shadow` does **not** downgrade `boundary_violation` or `suppression` — only an explicit `modes.perCheck.<rule>: shadow` flips those.

The recommended rollout is:

1. **Ship in shadow.** `modes.default: shadow` (the bootstrap default). Zone classification is advisory; CI does not block on red/gray/checkpoint-unmet. Boundary violations still block from day one.
2. **Calibrate.** Read the stickies for 4 weeks or 30 PRs. Demote red zones that fire on routine work; tighten checkpoints that rubber-stamp; add `watch` entries for things you want surfaced but not gated.
3. **Flip.** Change `modes.default` to `binding`. This goes through a normal PR — the policy file is itself red-zone.

The `boundary_violation = binding` from day one is not a typo; it is a deliberate choice. Boundary rules express invariants the team already committed to (via ArchUnit / Import Linter / etc.). They are not "new policy" that needs calibration.

## How the reporter consumes backend output

`boundaryAdapter` declares how the boundary-rule backend's output reaches the reporter.

| `outputFormat` | Backend | What's read |
|---|---|---|
| `junit-xml` | ArchUnit (JVM/Spring), other JUnit-XML producers | `<testsuite>/<testcase>/<failure>` shapes at `outputPath`. `violationFilter.matchClassName` / `matchTestNamePattern` distinguish architecture failures from unrelated test failures in a shared JUnit XML. |
| `json-violations` | import-linter via the python extension's adapter; any backend that emits the schema at `core/agent-redline/core/schema/boundary-violations.schema.json` | A JSON document; each entry becomes a `BoundaryViolation` carrying `source` from the document's top-level field. |
| `none` | Repos that opt out (data pipelines, mixed monorepos, zone-only setups) | The reporter skips the boundary leg entirely. |

Bootstrap copies the chosen extension's `adapter.yaml` into the policy. CI snippets that pass `--boundary-report` and `--boundary-format` directly still work; the policy-level block is the fallback for non-CI invocations (e.g. local pre-push).

## Suppression detection

Adding `# noqa`, `# type: ignore`, `@SuppressWarnings`, `@ArchIgnore`, `ignore_imports`, `per-file-ignores`, or similar markers on guarded surfaces is the same shape of shortcut as a boundary workaround. The reporter scans added lines for suppression markers and routes additions on non-exempt paths to `architecture-review`.

Marker categories:

| Category | Match style | Examples |
|---|---|---|
| `inlineComments` | substring on added lines | `# noqa`, `# type: ignore`, `// archunit: ignore` |
| `annotations` | word-bounded token | `@SuppressWarnings`, `@ArchIgnore` |
| `configEdits` | structural-assignment match in declared config files | `ignore_imports = [...]` in `**/pyproject.toml` |

Vendored defaults ship per-extension at `.agent-redline/suppressions.yaml`. The policy declares overrides-only via the `suppressions:` block (`add` / `remove` / `exemptPaths`).

**Opt-in:** a policy with no `suppressions:` block keeps detection OFF. agent-workflow's bootstrap installs the block with `exemptPaths: ["**/tests/**"]` by default.

## Language extensions

A language extension provides the ecosystem-specific defaults: zone globs, boundary rules, the backend's output adapter, suppression markers, and PR-size thresholds calibrated against the stack.

| Stack | Extension | Boundary backend |
|---|---|---|
| JVM (Java, Kotlin) — generic + Spring addendum | `jvm-archunit` | [ArchUnit](https://www.archunit.org/) → JUnit XML |
| Python services and libraries (incl. Django) | `python` | [import-linter](https://import-linter.readthedocs.io/) → JSON violations |
| Other stacks | none shipped | zone-only (no boundary backend); pick a third-party tool such as dependency-cruiser, go-arch-lint, cargo-deny, or Semgrep |

Bootstrap detects the stack from build files and source layout (Gradle/Maven + Spring deps → `jvm-archunit` + Spring; pyproject + FastAPI/Flask/Django → `python`; nothing matches → zone-only fallback). For the layered-vs-library-vs-zone-only shape selection logic, see `core/agent-redline/core/skill/bootstrap-mode.md` §"JVM shape selection" / "Python shape selection".

## Calibrating the policy

Red zones that fire on ordinary feature PRs cause alert fatigue. The Spring defaults were tuned against three production services after the first round fired on ~50% of PRs. Same caveat applies to whatever bootstrap drafts for your repo: it's a starting hypothesis, not a final answer.

### What bootstrap does

Phase 3 of agent-workflow's bootstrap walks three calibration steps:

1. **Zone-utility check.** For each red entry in the draft policy, the agent asks: does this path change in ordinary feature PRs? If routine, demote to `watch` (visibility only) or `blue`. "Important" + "routine" = `watch`, not red.
2. **History-based tuner.** When ≥30 recent PRs (or push-driven changesets) exist, the agent can run the tuner against the last 30 and report which red rules fired how often. Paths firing on >50% of PRs are almost always over-classified. The tuner only suggests; you approve, override, or split each one. **Never auto-applies.** This is the single most effective step against alert fatigue — opt in if your repo has the history.
3. **Repo-specific questions.** Third-party adapter contracts? Customer-specific code that mustn't leak into shared core? Generated source directories to exclude? PR-size thresholds for your team?

Skipping these is the most common adoption failure. A copy-pasted default policy will almost always over-classify red zones.

### What to do later

| Symptom | Action |
|---|---|
| A red zone fires too often | Walk recent PRs. If routine, demote to `watch` or split the path (e.g. `domain/repository/*.java` red, `domain/repository/impl/**` blue). |
| Reviewers rubber-stamp the same checkpoint | Tighten `satisfiedBy` (require CODEOWNER approval instead of a label), or reconsider whether the zone earns the checkpoint at all. |
| A red zone never fires | Glob is probably wrong. Run `git ls-files <glob>` to confirm. |
| Boundary violation fires on legitimate refactoring | The boundary rule is wrong or the refactor is the wrong shape. Address it in a separate change that touches **only** the boundary policy; never weaken the policy in the same PR as the violation. |

The tuner is re-runnable any time the policy feels wrong. Bootstrap invokes it from agent-redline's source tree; you can run it the same way after install.

### What NOT to do

- Don't add red zones for "important code." Add them for "code where the *change* is a structural decision."
- Don't waive a boundary-violation finding through a task exception. The checker's `risk.boundary_violation_absent` is non-waivable. To change a boundary rule, change it through its own reviewed PR.
- Don't flip from shadow to binding on day one. The calibration window is the point.
- Don't edit `agent-redline-policy.yaml` outside its own PR. The file is itself red-zone — every change should be visible and reviewed.

## The sticky comment

The CI workflow runs the reporter and posts a sticky comment per PR (`marocchino/sticky-pull-request-comment@v2`, header `agent-redline`). Real example (from the `mixed` fixture):

```markdown
## agent-redline: RED

**Red-zone files changed.**

| Zone | Files |
|---|---|
| Red  | `src/main/java/com/example/orders/domain/Order.java` |
| Blue | `src/test/java/com/example/orders/OrderServiceTest.java` |
| Gray | `src/main/java/com/example/orders/util/DateNormalizer.java` |

**Required checkpoints:**
- [ ] `architecture-review` — red-zone change: src/main/java/com/example/orders/domain/Order.java. Satisfy by: CODEOWNER approval or label `architecture-reviewed`

**Boundary check:** passed
**API check:** no changes
**PR size:** 3 files / 0 lines (ok)
```

A boundary violation looks the same shape with the `Boundary check` line listing the violated rule and the failing class — and CI exits non-zero so the PR cannot merge.

The agent-workflow CI workflow posts a *second* sticky (header `agent-workflow`) covering the Work Record predicates. The two stay independently legible.

## Exit codes (reporter)

| Exit | Meaning | Effect |
|---|---|---|
| `0` | Clean — `BLUE`, or `GRAY` with no checkpoint, or shadow-mode warnings. | CI job green. |
| `1` | Advisory failures only (shadow-mode RED, PR-size warnings, etc.). | CI job green (in PR-driven flow); the sticky surfaces the warning. |
| `2` | Boundary violation, or binding-mode RED with unmet checkpoint, or other binding-mode hard fail. | CI job red. Merge blocks if the check is required. |

In **push-driven flow** the workflow fails on `EXIT != 0` (RED and BOUNDARY_VIOLATION both fire GitHub's default email-on-failure). In **PR-driven flow** the workflow fails only on exit 2 — exit 1 is shadow-mode advisory and stays green.

## Files in a consuming repo after bootstrap

| Path | Role |
|---|---|
| `agent-redline-policy.yaml` | The policy. Edits go through architecture-review (file is itself red-zone). |
| `agent-redline/boundary-violations.json` *(optional)* | Where an external boundary backend writes its findings, if `boundaryAdapter.outputFormat` is `json-violations` and the consumer wires it. The CI workflow picks it up automatically. |
| `.agent-redline/suppressions.yaml` | Vendored marker defaults; bootstrap copies from the chosen extension. The policy's `suppressions.add/remove` work relative to this file. |
| `scripts/agent-redline-report.py` | Vendored single-file reporter. CI invokes it. |
| `scripts/format-verdict-comment.py` | Renders the agent-workflow sticky from the predicate JSON. |
| `docs/agent-redline/skills/` | Per-checkpoint reference docs (`blue-zone`, `red-zone`, `gray-zone`, `boundary-violation`, `pr-discipline`) the agent loads when escalating to a checkpoint. |

## What this page does NOT cover

- **Building a new language extension.** The two shipped extensions cover JVM and Python. Adding a third stack requires authoring an `extensions/<name>/` folder with `profile.md`, `scaffold.md`, `adapter.yaml`, and (optionally) an adapter script. The relevant upstream doc is `docs/EXTENSIONS.md` in the agent-redline source repo.
- **The full reporter implementation.** Source lives at [`core/agent-redline/core/reporter/`](../core/agent-redline/core/reporter/). Read it when authoring a new boundary backend or debugging a verdict.
- **The skill-side operating-mode loop.** That's the agent's discipline, not the developer's. Read it if you're working on agent-workflow's `assess-risk` checkpoint or porting redline changes from upstream — file is at [`core/agent-redline/core/skill/operating-mode.md`](../core/agent-redline/core/skill/operating-mode.md).

For agent-workflow's own predicate-level enforcement (including how the reporter's verdict gets surfaced into agent-workflow's PR sticky), see [`ENFORCEMENT.md`](ENFORCEMENT.md).
