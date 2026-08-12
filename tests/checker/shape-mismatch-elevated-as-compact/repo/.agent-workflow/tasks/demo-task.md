<!-- agent-workflow:start -->
**Outcome:** Mismatch demo: compact fields, Elevated classification.

**Target:** wallet-service.

**Scope:** Retry path.

**Constraints:** Public API unchanged.

**Completion criteria:** A regression test asserts the new behaviour.

**Risk:** Elevated

**Complexity:** Simple

**Reason:** Touches the persistence layer (Elevated trigger).

**Approach:** Quick patch — would actually need the expanded shape.

**Verification:** WalletRetryTest plus the required wallet-service CI job.

**State:** Ready to implement
<!-- agent-workflow:end -->
