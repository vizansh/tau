# Phase 18: Provider Configuration Foundation

This phase starts Tau's durable provider configuration work without adding an
extension system.

The implementation lives in:

```text
src/tau_coding/provider_config.py
src/tau_coding/cli.py
src/tau_coding/tui/app.py
src/tau_coding/commands.py
src/tau_coding/session.py
```

## What was added

Tau now has a provider settings model under `tau_coding`:

```python
ProviderSettings
OpenAICompatibleProviderConfig
ProviderSelection
```

Settings are stored at:

```text
~/.tau/providers.json
```

If that file does not exist, Tau uses an OpenAI-compatible default:

```text
provider: openai
model: gpt-4.1-mini
api key env var: OPENAI_API_KEY
base URL env var: OPENAI_BASE_URL
timeout env var: OPENAI_TIMEOUT_SECONDS
```

API keys are not stored in the config file. Provider entries name the
environment variable that should hold the key.

## Example config

```json
{
  "default_provider": "local",
  "providers": [
    {
      "name": "local",
      "type": "openai-compatible",
      "base_url": "http://localhost:11434/v1",
      "api_key_env": "LOCAL_API_KEY",
      "models": ["qwen", "llama"],
      "default_model": "qwen",
      "timeout_seconds": 120
    }
  ]
}
```

## Runtime resolution

Print mode and TUI startup now resolve provider/model selection from durable
settings:

```text
tau --provider local --model qwen
tau -p "review this" --provider local
```

When `--model` is omitted, Tau uses the configured provider's default model.
When `--provider` is omitted, Tau uses `default_provider`.

## CLI commands

Tau can list configured providers:

```text
tau providers
```

Tau can also create or update an OpenAI-compatible provider entry:

```text
tau --provider local \
  --base-url http://localhost:11434/v1 \
  --api-key-env LOCAL_API_KEY \
  --timeout-seconds 120 \
  --model qwen \
  setup
```

The setup options are top-level options before the `setup` command word. This
preserves the Pi-style `tau "prompt"` form while still adding a lightweight
setup flow. Setup writes provider metadata only; it warns if the named API key
environment variable is not currently set.

Provider HTTP timeouts are configurable through `timeout_seconds` in
`~/.tau/providers.json`. The default OpenAI-compatible provider can also read
`OPENAI_TIMEOUT_SECONDS`. The configured value is passed to the HTTPX streaming
client instead of keeping timeout behavior hardcoded in the provider adapter.

## Slash commands

Slash commands now expose the active provider/model configuration:

```text
/provider
/provider <name>
/model
/model <name>
```

`/model <name>` switches the active model for future turns in the running
process when the model is known for the active provider.

`/provider <name>` switches the active provider for future turns in the running
process and resets the active model to that provider's configured default. The
provider must already exist in `~/.tau/providers.json`, and its API key must be
available through the configured environment variable.

## Boundary

Provider settings belong to `tau_coding`, not `tau_agent`.

The reusable harness still receives only a ready `ModelProvider` and a model
name. It does not know about Tau home, JSON config files, environment variables,
or CLI/TUI setup behavior.

## Limitations

Phase 18 intentionally keeps setup minimal. Provider metadata is edited through
the CLI setup command, not an interactive TUI form, and API keys are read from
environment variables instead of a secure keyring.

## Tests

The phase is covered by:

```text
tests/test_provider_config.py
tests/test_cli.py
tests/test_commands.py
tests/test_tui_app.py
```

The tests verify:

- missing config falls back to OpenAI-compatible defaults
- provider settings round-trip through `~/.tau/providers.json`
- provider setup and listing CLI behavior
- provider HTTP timeout parsing and runtime config forwarding
- default provider/model selection
- configured API key environment variables
- CLI provider/model forwarding
- TUI startup selection
- `/provider` and `/model` command behavior
