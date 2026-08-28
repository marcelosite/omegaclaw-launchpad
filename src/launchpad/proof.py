"""Read-only readiness checks for the real OmegaClaw proof harness."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List


def proof_checks(project_root: Path, mission_root: Path) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    checks.append(
        {
            "name": "Mission context",
            "ok": (mission_root / "03-reflection" / "reflection-context.json").exists(),
            "detail": "run reflect init, run, validate, and prepare first",
        }
    )
    modern_python = None
    modern_version = None
    for candidate in ("python3.13", "python3.12", "python3.11", "python3.10", "python3"):
        path = shutil.which(candidate)
        if not path:
            continue
        result = subprocess.run(
            [path, "-c", "import sys; print('%d.%d' % sys.version_info[:2]); raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            modern_python = path
            modern_version = result.stdout.strip()
            break
    checks.append(
        {
            "name": "Python 3.10+",
            "ok": modern_python is not None,
            "detail": ("found %s at %s" % (modern_version, modern_python)) if modern_python else "not found",
        }
    )
    checks.append(
        {"name": "Git", "ok": shutil.which("git") is not None, "detail": "required to fetch pinned upstream"}
    )
    docker_path = shutil.which("docker")
    bundled_docker = Path("/Applications/Docker.app/Contents/Resources/bin/docker")
    if docker_path is None and bundled_docker.exists():
        docker_path = str(bundled_docker)
    docker_running = False
    if docker_path:
        result = subprocess.run(
            [docker_path, "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False
        )
        docker_running = result.returncode == 0
    checks.append(
        {
            "name": "Docker engine",
            "ok": docker_running,
            "detail": "required to build and run OmegaClaw-Core v0.1.19",
        }
    )
    runner = project_root / "scripts" / "run-omegaclaw-proof.sh"
    checks.append(
        {"name": "Proof runner", "ok": runner.exists(), "detail": str(runner)}
    )
    return checks
