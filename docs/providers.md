# Providers

Tau's provider layer lives in `tau_ai`.

Providers translate external model APIs into Tau's provider-neutral event stream.

## OpenAI-compatible provider

Tau currently includes an OpenAI-compatible chat completions adapter.

Set:

```bash
export OPENAI_API_KEY="..."
```

Optionally set a custom compatible endpoint:

```bash
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

Optionally tune the HTTP timeout used by the default OpenAI-compatible provider:

```bash
export OPENAI_TIMEOUT_SECONDS="120"
```

The provider uses `/chat/completions` with streaming enabled.

## Durable Provider Config

Tau stores provider metadata in:

```text
~/.tau/providers.json
```

List configured providers:

```bash
tau providers
```

Create or update a provider:

```bash
tau --provider local \
  --base-url http://localhost:11434/v1 \
  --api-key-env LOCAL_API_KEY \
  --timeout-seconds 120 \
  --model qwen \
  setup
```

Provider entries can also include `timeout_seconds` in `~/.tau/providers.json`.
The value must be greater than zero.

Run Tau with a configured provider:

```bash
tau --provider local
tau "summarize this project" --provider local
```

Inside the TUI:

```text
/provider
/provider local
/model
/model qwen
/reload
```

`/reload` refreshes provider settings for future command use. Switching the
active runtime provider is still done explicitly with `/provider <name>`.

## Fake provider

Tau also includes `FakeProvider` for deterministic tests. It replays scripted provider events and never makes network requests.

It is used heavily by agent-loop, session, command, and TUI tests.
