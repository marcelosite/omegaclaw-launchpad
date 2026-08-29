"""Safe creation of local, file-backed Studio workspaces."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from .studio_templates import resolve_template


SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_SLUG_LENGTH = 63


def validate_workspace_slug(slug: str) -> str:
    """Validate the small, URL-safe workspace identifier used as a directory name."""
    if not isinstance(slug, str) or not SLUG_PATTERN.fullmatch(slug) or len(slug) > MAX_SLUG_LENGTH:
        raise ValueError(
            "Workspace name must use lowercase letters, numbers, and single hyphens (1-63 characters)."
        )
    return slug


def studio_workspaces_root(project_root: Path) -> Path:
    """Return the fixed Studio workspace root below a user-selected project directory."""
    return project_root.expanduser().resolve() / ".launchpad" / "studio" / "workspaces"


def workspace_path(project_root: Path, slug: str) -> Path:
    """Return a validated workspace destination without creating it."""
    validated_slug = validate_workspace_slug(slug)
    root = studio_workspaces_root(project_root)
    destination = root / validated_slug
    if destination.parent != root:
        raise ValueError("Workspace destination is outside the Studio workspace root.")
    return destination


def _assert_safe_source(source: Path) -> None:
    """Reject template symlinks so a future template cannot copy outside its tree."""
    for path in source.rglob("*"):
        if path.is_symlink():
            raise ValueError("Studio templates must not contain symbolic links: %s" % path.name)


def _create_private_workspace_root(project_root: Path) -> Path:
    """Create the fixed workspace ancestry without following user-controlled symlinks."""
    project = project_root.expanduser().resolve()
    current = project
    for name in (".launchpad", "studio", "workspaces"):
        current = current / name
        if current.is_symlink():
            raise ValueError("Studio workspace root must not contain symbolic links.")
        current.mkdir(mode=0o700, exist_ok=True)
        current.chmod(0o700)
    return current


def create_workspace(project_root: Path, slug: str, template_name: str) -> Path:
    """Copy one approved template to a new private local workspace.

    Existing workspaces are never overwritten. The source is selected exclusively
    from ``approved_templates`` and is left untouched by the copy operation.
    """
    source = resolve_template(template_name)
    _assert_safe_source(source)
    destination = workspace_path(project_root, slug)
    root = destination.parent

    if destination.exists() or destination.is_symlink():
        raise FileExistsError("Studio workspace already exists: %s" % destination)

    private_root = _create_private_workspace_root(project_root)
    if private_root != root:
        raise ValueError("Studio workspace root changed while creating the workspace.")

    shutil.copytree(source, destination, copy_function=shutil.copy2)
    for path in (destination, *destination.rglob("*")):
        if path.is_file():
            path.chmod(0o600)
        elif path.is_dir():
            path.chmod(0o700)
    return destination
