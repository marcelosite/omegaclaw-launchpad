# Provider and secret boundary

The reproducible Launchpad proof uses OmegaClaw's `Test` provider in Docker. It is real runtime execution and needs no paid key.

For a future paid run, choose one upstream path explicitly:

- ASI Cloud: `ASICloud`, environment variable `ASI_API_KEY`, endpoint `https://inference.asicloud.cudos.org/v1`.
- Direct MiniMax: upstream `OpenAIAPI`, environment variable `OPENAIAPI_API_KEY`, endpoint `https://api.minimax.io/v1` (global) or `https://api.minimaxi.com/v1` (mainland), with an explicit MiniMax model.

These are different providers. A direct MiniMax key must not be placed in `ASI_API_KEY`. Do not paste either key into Git, `.env` committed to the project, examples, receipts, or chat. Supply it only at launch through a private secret mechanism and remove it from shell history where appropriate.

Launchpad does not claim a paid-provider proof until a human supplies a key and the run records a fresh receipt. The Test proof remains the acceptance path for installation and the Wizard.
