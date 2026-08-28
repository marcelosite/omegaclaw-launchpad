"""Configuration and upstream facts used by the onboarding journey."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any


UPSTREAM_REPOSITORY = "https://github.com/asi-alliance/OmegaClaw-Core.git"
UPSTREAM_REF = "v0.1.19"
UPSTREAM_COMMIT = "642c53676cf795cb7a0030823b36018c029b1416"
UPSTREAM_IMAGE = "omegaclaw-launchpad:v0.1.19"

PROVIDER_ENV = {
    "Anthropic": "ANTHROPIC_API_KEY",
    "OpenAI": "OPENAI_API_KEY",
    "ASICloud": "ASI_API_KEY",
    "ASIOne": "ASIONE_API_KEY",
    "OpenRouter": "OPENROUTER_API_KEY",
    "OpenAIAPI": "OPENAIAPI_API_KEY",
}

PROVIDERS = tuple(PROVIDER_ENV)
CHANNELS = ("irc", "telegram", "slack", "websocket", "test")
CHANNEL_ENV = {
    "telegram": "TG_BOT_TOKEN",
    "slack": "SL_BOT_TOKEN",
    "websocket": "WS_URL",
}


def build_config(workspace: Path, provider: str, channel: str, irc_channel: str) -> Dict[str, Any]:
    """Return a JSON-serializable onboarding manifest without credentials."""
    return {
        "schema_version": 1,
        "workspace": str(workspace.resolve()),
        "upstream": {
            "repository": UPSTREAM_REPOSITORY,
            "ref": UPSTREAM_REF,
            "commit": UPSTREAM_COMMIT,
            "image": UPSTREAM_IMAGE,
        },
        "provider": provider,
        "provider_env": PROVIDER_ENV[provider],
        "channel": channel,
        "channel_env": CHANNEL_ENV.get(channel),
        "irc_channel": irc_channel,
        "journey": {
            "orientation": "pending",
            "preflight": "pending",
            "configuration": "pending",
            "first_run": "pending",
        },
    }
