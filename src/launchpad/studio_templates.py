"""Approved, local-only Studio examples."""

from __future__ import annotations

from pathlib import Path
from typing import Dict


class TemplateNotFoundError(ValueError):
    """Raised when a caller requests a template outside the Studio allowlist."""


def repository_root() -> Path:
    """Return the checkout root that contains the approved Studio example."""
    return Path(__file__).resolve().parents[2]


def approved_templates() -> Dict[str, Path]:
    """Return the immutable allowlist of examples that Studio may copy."""
    return {"lighthouse-in-the-fog": repository_root() / "examples" / "lighthouse-in-the-fog"}


def resolve_template(template_name: str) -> Path:
    """Resolve one approved template without accepting an arbitrary filesystem path."""
    template = approved_templates().get(template_name)
    if template is None:
        raise TemplateNotFoundError("Unknown Studio template: %s" % template_name)
    if not template.is_dir():
        raise FileNotFoundError("Approved Studio template is missing: %s" % template_name)
    return template.resolve()
