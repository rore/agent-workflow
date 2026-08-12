"""Entry point for ``python -m core.checker``."""

from __future__ import annotations

import sys

from .checker import main

if __name__ == "__main__":
    sys.exit(main())
