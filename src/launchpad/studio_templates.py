"""Approved, local-only Studio templates."""

from __future__ import annotations

from pathlib import Path
from typing import Dict


class TemplateNotFoundError(ValueError):
    """Raised when a caller requests a template outside the Studio allowlist."""


def repository_root() -> Path:
    """Return the checkout root that contains the approved Studio templates."""
    return Path(__file__).resolve().parents[2]


def approved_templates() -> Dict[str, Path]:
    """Return the immutable allowlist of templates that Studio may copy."""
    return {"community-care": repository_root() / "templates" / "community-care"}


def resolve_template(template_name: str) -> Path:
    """Resolve one approved template without accepting an arbitrary filesystem path."""
    template = approved_templates().get(template_name)
    if template is None:
        raise TemplateNotFoundError("Unknown Studio template: %s" % template_name)
    if not template.is_dir():
        raise FileNotFoundError("Approved Studio template is missing: %s" % template_name)
    return template.resolve()
