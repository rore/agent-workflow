"""Per-repository ``agent-workflow.yaml`` config.

Loads and validates the file against ``core/schema/agent-workflow.schema.json``.
The loader exposes typed fields the rest of the harness consumes; the
raw mapping is kept on ``Config.raw`` for forward compatibility.

Public API:

- :class:`Config` — typed config view.
- :class:`LocalBackendConfig`, :class:`WorkRecordConfig` — Work Record sub-types.
- :class:`RedlineConfig` — agent-redline integration.
- :func:`load` — read + validate a config file into a :class:`Config`.
- :exc:`ConfigError` — raised on any malformed input.
"""

from .applicability import (
    ApplicabilityConfig,
    ApplicabilityDecision,
    DocumentationOnlyConfig,
    evaluate_applicability,
)
from .loader import (
    Config,
    ConfigError,
    LocalBackendConfig,
    RedlineConfig,
    WorkRecordConfig,
    load,
)

__all__ = [
    "ApplicabilityConfig",
    "ApplicabilityDecision",
    "Config",
    "ConfigError",
    "DocumentationOnlyConfig",
    "LocalBackendConfig",
    "RedlineConfig",
    "WorkRecordConfig",
    "evaluate_applicability",
    "load",
]
