"""Checkout shim so ``python3 -m launchpad`` works before installation."""

from pathlib import Path

__version__ = "0.3.0"
__path__.append(str(Path(__file__).resolve().parent.parent / "src" / "launchpad"))
