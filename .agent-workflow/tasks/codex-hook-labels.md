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
**Plan:** Add the two supported Codex statusMessage values using existing runtime registration/update logic; preserve other fields and Claude behavior. Extend existing installer checks for creation, legacy/stale-label upgrade, preservation and byte-identical repeat. Add concise trust-label and re-review guidance, regenerate package/local installs. Do not add name or file-level description, change commands, or modify trust state.
**Verification plan:** Fresh/legacy/stale-label installation, preservation, byte-identical repeat, malformed-input safety and unchanged Claude metadata -> existing tests/hooks/run.sh installer cases. Approval-title use -> execute the installed renderer title function with the two labels and fallback. Trust semantics -> official changed-definition trust documentation; no trust-setting writes. Regression/package consistency -> tests/run-all.sh. Baseline and verification adequacy -> independent result review.
**Plan review:** Agent technical review: /root/codex_labels_review, approved baseline revision 8b97bc2cdebcfbab943cdef5e3567bea14efc4b4; see Plan review below.
**Approvals:** Not required at this risk level; manager coordinates any genuinely new human gate.
**Exceptions:** —
**State:** Ready to implement
<!-- agent-workflow:end -->

## Implementation

- Official docs and bounded installed-app renderer inspection establish feasibility. Installer was inspected before context was persisted; this first commit records the unchanged authoritative requirement before product edits, not retroactive implementation evidence.
- Clean completed worktree reused at current main 7f20e060728748ba04cfaed68039a82cec289ffa; branch feat/codex-hook-labels. Root checkout remains untouched.
- Independent plan review complete; ready for metadata-only implementation.

## Plan review

Agent technical review: /root/codex_labels_review. Approved at 8b97bc2cdebcfbab943cdef5e3567bea14efc4b4. Inspected record, full installer/call sites, installer tests, integration guidance, policy and SPEC sections 8, 9.4, 9.7. No blockers; verification adequate. Preserve exact-command ownership, document possible renewed trust review, and do not broaden pre-existing duplicate-registration reconciliation. The criterion means upgrades add no duplicates.

## Evidence

Installed app.asar read-only evidence: webview/assets/hooks-settings-copy-1f0ea6fb4a93.js function a(e,t,n) trims e.statusMessage and chooses numberedHookTitle ({index} - {statusMessage}) or fallbackHookTitle (Hook {index}). hooks-settings-source-label-71972f8ce657.js imports that title function as I and calls I(e,r,y) in the hook row beside the Trust button. No app files changed; this proves the renderer path, not a live screenshot or future-version guarantee.
