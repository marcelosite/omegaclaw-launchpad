"""The local, artifact-reading OmegaClaw Launchpad Studio server.

P0 deliberately keeps this package separate from the proof runner.  It reads
the artifacts produced by the existing commands and offers one constrained
template-copy action, but never runs Docker, shell commands, or an OmegaClaw
process.
"""

from .artifacts import StudioArtifacts
from .server import HOST, PORT, create_server, serve

__all__ = ("HOST", "PORT", "StudioArtifacts", "create_server", "serve")
