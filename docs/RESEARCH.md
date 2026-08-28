# Architecture research snapshot

This project is intentionally based on the upstream stack observed on 28 August 2026, not on an assumed agent architecture.

## OmegaClaw-Core

Source: [asi-alliance/OmegaClaw-Core](https://github.com/asi-alliance/OmegaClaw-Core), pinned for the MVP to `v0.1.19`.
The underlying [OpenCog Hyperon repository](https://github.com/trueagi-io/hyperon-experimental) documents MeTTa, Python/Docker installation, and the active pre-alpha status of the stack.

Observed facts:

- `run.metta` imports `OmegaClaw-Core` into the PeTTa runtime and calls `(omegaclaw)`.
- `src/loop.metta` owns the recursive turn loop: initialize config/memory/plugins/channels, receive a message, build prompt context, call the selected provider, repair/parse the response, dispatch skills, append history, sleep, and recurse.
- MeTTa is the control/reasoning surface; Python bridges provide LLM calls, embeddings, web search, file I/O, logging, channels, and provider/plugin registries.
- The default launcher is `scripts/omegaclaw`. It performs interactive configuration and starts a Docker container. It expects provider credentials in environment variables and passes channel/provider choices as arguments.
- Communication channels and LLM providers are plugin-registered. The core includes IRC, Telegram, Slack, Mattermost, WebSocket, and test adapters, plus a test provider.
- Memory is split into working memory (`pin`), persistent embedding memory (`remember`/`query`), AtomSpace reasoning state, and an episodic history file.
- The project contains a strong reference/tutorial corpus, but the newcomer path still assumes knowledge of Python, virtual environments, Docker, channels, API keys, and MeTTa.

## Hyperon/OpenCog/MeTTa relevance

OmegaClaw is not a generic Python chatbot. It is a MeTTa-based agent running on the OpenCog Hyperon stack. Hyperon describes MeTTa as the successor to OpenCog Classic Atomese and exposes Python and Docker installation paths. OmegaClaw uses that stack for the symbolic/control layer while delegating natural-language interpretation and orchestration to an LLM.

The Launchpad therefore does not reimplement AtomSpace, MeTTa evaluation, memory, or the agent loop. It teaches the dependency relationship and hands off to the upstream runtime.

## HyperSprint Track 2 fit

The official [HyperSprint #1 brief](https://bgicommons.org/hackathons/hypersprint-1-omegaclaw) says the sprint is about reusable building blocks that help the community learn, adopt, and expand OmegaClaw rather than changing OmegaClaw core. Track 2 asks for educational resources and onboarding experiences, with examples including interactive onboarding agents, documentation, tutorials, video demonstrations, and example projects. The [BGI Commons home page](https://bgicommons.org/) frames the community goal as building beneficial AI/AGI that serves all of humanity.

The MVP targets the smallest technically real subset: an interactive onboarding CLI plus a reusable, source-pinned launch handoff and a no-secret offline proof.
