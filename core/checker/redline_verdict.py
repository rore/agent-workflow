"""agent-redline verdict reader.

Loads the JSON document agent-redline's reporter writes (see
``core/agent-redline/tests/reporter/*/expected-verdict.json`` for the
shape) and exposes a small typed view the checker's redline predicates
consume.

Why a dedicated module:

- Redline's verdict has no JSON Schema in our copy of the source — the
  reporter goldens are the contract today. Centralising the read here
  keeps that coupling in one place; the predicates downstream don't
  need to know about defensive ``dict.get`` chains.
- Upstream redline may grow keys. The parser ignores anything it does
  not recognise and defaults missing keys to safe values. A new
  ``verdict`` string variant or a new ``*Changes`` flag won't break the
  checker — it will simply not influence the detected risk until we
  teach the parser about it.

The single classification helper here mirrors the translation table
documented in ``core/templates/checkpoints/assess-risk.md``. Keep them
in sync — the skill tells the agent how to pre-classify; this module
tells the checker how to post-classify on the final diff.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Risk vocabulary the agent-workflow checker speaks. Kept here as a
# tuple ordered low → high so callers can compare with the index. The
# string constants are deliberately not imported from
# ``core.work_record`` — that module's ``ALLOWED_RISK`` is a set, not
# ordered, and re-using its frozenset would obscure the ordering this
# module depends on.
_RISK_ORDER: tuple[str, ...] = ("Routine", "Elevated", "High")


class RedlineVerdictError(ValueError):
    """Raised when the verdict file is present but malformed.

    A missing file is not an error — :func:`load` returns ``None`` for
    that case so the caller can distinguish "absent" from "broken".
    """


@dataclass(frozen=True)
class RedlineVerdict:
    """Defensive view over redline's verdict JSON.

    Only the fields the checker reads are surfaced. The raw payload is
    kept on :attr:`raw` so downstream callers that need an upstream-
    introduced key can reach for it without waiting for a parser
    update. The structural accessors (``boundary_violations``,
    ``zones``, ``checkpoints``, the four ``*_changed`` booleans) drive
    the predicates.
    """

    boundary_violations: list[dict[str, Any]]
    """List of boundary-violation entries; each at least carries
    ``rule``, ``detail``, ``severity``, ``source``. Empty list when
    redline saw no violations on this diff."""

    zones: dict[str, list[str]]
    """``{"blue": [...], "gray": [...], "red": [...], "watch": [...]}``
    with missing keys defaulted to an empty list. Files redline could
    not classify don't appear here at all."""

    checkpoints: list[dict[str, Any]]
    """Redline's review checkpoints triggered by the diff (e.g.
    ``persistence-review``, ``api-review``). Used as a tie-breaker when
    a red-zone change has no ``*Changes.detected`` flag set."""

    api_changed: bool
    schema_changed: bool
    security_changed: bool
    runtime_config_changed: bool
    """Disambiguators for red-zone → High vs Elevated. Pulled from
    ``apiChanges.detected``, ``schemaChanges.detected``,
    ``securityChanges.detected``, ``runtimeConfigChanges.detected`` —
    each defaults to ``False`` when the key is absent."""

    modes: dict[str, Any] = field(default_factory=dict)
    """The reporter echoes the policy's ``modes`` block. Shape:
    ``{"default": "shadow"|"binding", "perCheck": {<name>: ...}}``.
    Empty dict when the reporter pre-dates the modes-echo change — in
    that case, :meth:`is_binding` defaults to ``True`` (the previously
    hardcoded behaviour) to preserve backward compatibility."""

    raw: dict[str, Any] = field(default_factory=dict)
    """The full parsed payload. Forward-compatibility escape hatch."""

    # ------------------------------------------------------------------
    # Derived properties
    # ------------------------------------------------------------------

    @property
    def has_boundary_violation(self) -> bool:
        """``True`` when redline flagged at least one boundary violation.

        Boundary violations are a separate gate in the predicate set —
        they're not a Risk-level question. The checker reads this and
        ``risk.boundary_violation_absent`` blocks on it.
        """
        return bool(self.boundary_violations)

    def detected_risk(self) -> str:
        """Translate zones + checkpoints + change flags into our Risk vocabulary.

        Translation table (in step with
        ``core/templates/checkpoints/assess-risk.md``):

        - **High** when any contract / schema / security surface
          changed (``api_changed``, ``schema_changed``,
          ``security_changed``) or when a triggered checkpoint id is
          in the well-known High set (``api-review``,
          ``persistence-review``, ``security-review``,
          ``financial-review``). These are contract-class surfaces
          where a mis-declaration matters most.
        - **Elevated** when any red or gray zone was touched, or when
          runtime configuration changed (operational surface), or when
          redline raised any unsatisfied checkpoint (the policy is
          telling us this needs human attention).
        - **Routine** otherwise (blue-only changes with no checkpoint
          and no change flag — the routine fast path).

        Boundary violations are handled by a separate predicate and do
        not affect this return value — the workflow rule is that a
        boundary violation blocks regardless of risk-level matching,
        so risk-level comparison still applies cleanly to the
        non-boundary part of the verdict.
        """
        # Step 1: High signals — contract/schema/security changes,
        # plus High-class checkpoint ids. Wins over any zone-based
        # baseline.
        if self.api_changed or self.schema_changed or self.security_changed:
            return "High"
        if self._has_high_checkpoint():
            return "High"

        # Step 2: Elevated signals — any red or gray zone touched, any
        # runtime config change, any redline checkpoint raised. We
        # don't differentiate red from gray here: that distinction
        # only affects High disambiguation (handled above).
        if self.zones.get("red") or self.zones.get("gray"):
            return "Elevated"
        if self.runtime_config_changed:
            return "Elevated"
        if self.checkpoints:
            return "Elevated"

        # Step 3: nothing flagged — blue-only or empty diff.
        return "Routine"

    def is_binding(self, check_name: str) -> bool:
        """Whether ``check_name`` is binding under the verdict's modes config.

        Mirrors the reporter's own ``_binding`` semantics so the
        agent-workflow checker arrives at the same disposition the
        reporter used when computing exit_code / recommendedAction:

        - ``perCheck.<name>`` wins when explicit (``"binding"`` or
          ``"shadow"``).
        - Otherwise falls back to ``modes.default``.
        - ``boundary_violation`` is hardcoded ``binding`` unless an
          explicit ``perCheck.boundary_violation: shadow`` flips it —
          matches the reporter (see SPEC §10.3, REDLINE.md §"Modes").

        When the verdict pre-dates the modes-echo change (``modes`` is
        empty), defaults to ``True`` — the previously hardcoded
        behaviour. Consumers that need to fail loud on an older
        reporter should check :attr:`modes` directly.
        """
        if not self.modes:
            return True
        per_check = self.modes.get("perCheck") or {}
        if check_name in per_check:
            return per_check[check_name] == "binding"
        if check_name == "boundary_violation":
            # Hardcoded default; only an explicit perCheck override flips it.
            return True
        default = self.modes.get("default") or "shadow"
        return default == "binding"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    # The set of checkpoint ids that, when triggered by redline, push a
    # red-zone finding from Elevated to High. These names are the ones
    # redline's policy templates ship today — see
    # ``core/agent-redline/core/templates/agent-policy.yaml.template`` for
    # the canonical list. ``architecture-review`` is intentionally *not* in this set:
    # it's the default checkpoint for any red-zone change and would
    # collapse the Elevated/High distinction. The four below name
    # contract/schema/security/persistence surfaces — the same
    # categories the ``*_changed`` booleans cover.
    _HIGH_CHECKPOINT_IDS: frozenset[str] = frozenset(
        {
            "api-review",
            "persistence-review",
            "security-review",
            "financial-review",
        }
    )

    def _has_high_checkpoint(self) -> bool:
        """``True`` iff a triggered checkpoint id matches the High set."""
        for cp in self.checkpoints:
            cp_id = cp.get("id")
            if isinstance(cp_id, str) and cp_id in self._HIGH_CHECKPOINT_IDS:
                return True
        return False


# ---------------------------------------------------------------------------
# Risk comparison helper
# ---------------------------------------------------------------------------


def risk_at_least(declared: str, detected: str) -> bool:
    """``True`` when ``declared`` Risk is at least ``detected`` Risk.

    Uses :data:`_RISK_ORDER` (Routine < Elevated < High). An unknown
    value on either side returns ``False`` defensively — the checker's
    ``risk.declared`` predicate already gates on a valid declared
    value, so this only fires in the post-`risk.declared` path where
    both sides are guaranteed valid.
    """
    try:
        return _RISK_ORDER.index(declared) >= _RISK_ORDER.index(detected)
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def load_redline_verdict(path: Path) -> RedlineVerdict | None:
    """Read redline's verdict at ``path`` and return the typed view.

    Returns:
    - ``RedlineVerdict`` when the file exists and parses as a JSON object.
    - ``None`` when the file does not exist. The checker treats this as
      "missing" — the ``risk.redline_findings_available`` predicate
      decides whether that is a block (``redline: required``) or
      advisory (``redline: optional``).

    Raises:
    - :exc:`RedlineVerdictError` when the file exists but is not valid
      JSON or does not deserialise to a JSON object at the top level.
      Predicates downstream surface this as a parse failure rather than
      ignoring it — silent fallback would let a corrupt verdict pretend
      to be a clean run.
    """
    if not path.exists():
        return None

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RedlineVerdictError(
            f"could not read redline verdict at {path}: {exc}"
        ) from exc

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RedlineVerdictError(
            f"redline verdict at {path} is not valid JSON: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise RedlineVerdictError(
            f"redline verdict at {path} must be a JSON object at the root "
            f"(got {type(data).__name__})"
        )

    return _from_mapping(data)


def _from_mapping(data: dict[str, Any]) -> RedlineVerdict:
    """Build the typed view, defaulting missing keys to safe values.

    Kept private so the only public construction path is :func:`load`
    (which is responsible for surfacing IO and decode errors). Tests
    can build verdicts via ``RedlineVerdict(...)`` directly.
    """
    raw_zones = data.get("zones") or {}
    zones: dict[str, list[str]] = {
        "blue": list(raw_zones.get("blue") or []),
        "gray": list(raw_zones.get("gray") or []),
        "red": list(raw_zones.get("red") or []),
        "watch": list(raw_zones.get("watch") or []),
    }

    return RedlineVerdict(
        boundary_violations=list(data.get("boundaryViolations") or []),
        zones=zones,
        checkpoints=list(data.get("checkpoints") or []),
        api_changed=bool((data.get("apiChanges") or {}).get("detected", False)),
        schema_changed=bool((data.get("schemaChanges") or {}).get("detected", False)),
        security_changed=bool(
            (data.get("securityChanges") or {}).get("detected", False)
        ),
        runtime_config_changed=bool(
            (data.get("runtimeConfigChanges") or {}).get("detected", False)
        ),
        modes=dict(data.get("modes") or {}),
        raw=data,
    )
