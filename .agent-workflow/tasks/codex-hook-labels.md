# Codex hook approval labels

Source: Pallium Relay `relay-msg-f11c1b4e009645ec8ec18966ad045c15`; user request verified in manager thread `01a0d7cd-696b-76a0-8f2f-48a80a201905`, turn `01a0e35b-fad8-7450-92f0-8ae9c6057e6e`.

<!-- agent-workflow:start -->
**Outcome:** Codex hook trust entries explain the purpose of each Agent Workflow hook.
**Target:** agent-workflow
**Scope:** Codex hook metadata in core/skill/hooks/install-settings.py, existing hook installer tests, integration documentation, generated package mirrors, and this Work Record.
**Constraints:** Supported metadata only; preserve third-party entries, commands, matchers, execution and trust controls; no consumer repository edits or new infrastructure.
**Completion criteria:** Fresh installs and upgrades have meaningful seed/guard approval labels; repeated installation is unchanged; unrelated hooks and metadata survive; supported Codex renderer evidence establishes approval-title use; existing tests and packaging pass.
**Requirement baseline:** {"source":"relay-msg-f11c1b4e009645ec8ec18966ad045c15","outcome":"Codex hook trust entries explain the purpose of each Agent Workflow hook.","scope":"Codex hook metadata in core/skill/hooks/install-settings.py, existing hook installer tests, integration documentation, generated package mirrors, and this Work Record.","constraints":"Supported metadata only; preserve third-party entries, commands, matchers, execution and trust controls; no consumer repository edits or new infrastructure.","completion_criteria":"Fresh installs and upgrades have meaningful seed/guard approval labels; repeated installation is unchanged; unrelated hooks and metadata survive; supported Codex renderer evidence establishes approval-title use; existing tests and packaging pass."}
**Risk:** Elevated
**Complexity:** Simple
**Reason:** Independent pre-edit review /root/codex_labels_review classifies installer and generated mirrors gray/watch, tests/docs/record blue; no red surface or checkpoint. Metadata only, but shipped harness code requires independent reviews.
**Discovery:** Official https://learn.chatgpt.com/docs/hooks supports statusMessage. Installed Codex 26.924.2738.0 trust-row title function uses statusMessage, otherwise Hook N. Installer owns exact command matches and already upgrades commandWindows.
**Material assumptions:** statusMessage remains supported and displayed in the target version; unsupported metadata or changes to execution/trust would return to planning. No canonical roadmap item applies to this small installer improvement.
**Plan:** Await independent technical review. Add the two supported Codex statusMessage values using existing runtime registration/update logic; preserve other fields and Claude behavior. Extend existing installer checks for creation, legacy/stale-label upgrade, preservation and byte-identical repeat. Add concise trust-label and re-review guidance, regenerate package/local installs. Do not add name or file-level description, change commands, or modify trust state.
**Verification plan:** Fresh install has exact seed/guard labels and unchanged portable commands; legacy/stale labels upgrade without duplicates and preserve third-party hooks, description and owned timeout; repeated install is byte-identical; malformed input unchanged; Claude has no new Codex metadata. Run existing hook suite, package consistency and full tests/run-all.sh. Verify installed renderer title function against sample labels; inspect changed-hook trust behavior without writing trust settings. Independent result review checks baseline and adequacy.
**Plan review:** Pending independent agent technical review.
**Approvals:** Not required at this risk level; manager coordinates any genuinely new human gate.
**Exceptions:** —
**State:** Blocked
<!-- agent-workflow:end -->

## Implementation

- Official docs and bounded installed-app renderer inspection establish feasibility. Installer was inspected before context was persisted; this first commit records the unchanged authoritative requirement before product edits, not retroactive implementation evidence.
- Clean completed worktree reused at current main 7f20e060728748ba04cfaed68039a82cec289ffa; branch feat/codex-hook-labels. Root checkout remains untouched.
- Blocked only on required independent plan review.

## Evidence

Installed app.asar read-only evidence: webview/assets/hooks-settings-copy-1f0ea6fb4a93.js function a(e,t,n) trims e.statusMessage and chooses numberedHookTitle ({index} - {statusMessage}) or fallbackHookTitle (Hook {index}). hooks-settings-source-label-71972f8ce657.js imports that title function as I and calls I(e,r,y) in the hook row beside the Trust button. No app files changed; this proves the renderer path, not a live screenshot or future-version guarantee.
