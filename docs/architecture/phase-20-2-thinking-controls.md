# Phase 20.2: Thinking Mode Controls

Phase 20.2 makes thinking mode an explicit Tau coding-session setting and adds
a TUI control for changing it.

## What Was Added

`tau_coding.thinking` defines Tau's supported thinking modes:

```text
off
minimal
low
medium
high
xhigh
```

The default is `medium`, matching Pi's default reasoning-depth preference. Tau
validates the visible controls against provider/model capabilities and passes
OpenAI-compatible `reasoning_effort` when a configured provider declares support.
Unsupported models show thinking controls as unavailable instead of presenting a
mode that Tau cannot safely send.

## Session Persistence

New sessions append an initial `thinking_level_change` entry after the initial
model entry. Explicit changes append another `thinking_level_change` entry and a
leaf pointer, so resume reconstructs the active thinking mode from the session
tree.

`CodingSession` exposes:

```python
session.thinking_level
session.available_thinking_levels
await session.set_thinking_level("high")
await session.cycle_thinking_level()
```

This keeps thinking state in `tau_coding`, while `tau_agent.session` remains the
portable replay layer that knows how to reconstruct `ThinkingLevelChangeEntry`
values.

## Commands And TUI

The Textual TUI binds thinking cycling to `Shift-Tab` by default. The key is
configurable in `~/.tau/tui.json`:

```json
{
  "keybindings": {
    "thinking_cycle": "f3"
  }
}
```

The sidebar and compact session line read `session.available_thinking_levels`
first. When the active provider or model has no thinking capability metadata,
the TUI shows the control as unavailable. If the user tries to cycle or set a
thinking mode anyway, the session raises a user-facing reason.

Tau does not register a standalone `/thinking` command in the default command
registry. The command surface stays aligned with Pi/Codex, where model choice
and reasoning controls belong with model selection and session status. `/session`
reports `Thinking mode: unavailable` plus the reason when the active
provider/model cannot change thinking mode.

## Provider Capabilities

Provider settings may declare thinking support with:

```json
{
  "thinking_levels": ["off", "low", "medium", "high"],
  "thinking_models": ["gpt-5.5"],
  "thinking_default": "medium",
  "thinking_parameter": "reasoning_effort"
}
```

`thinking_models` is optional. If it is omitted, the declared levels apply to
all models for that provider. Tau's built-in direct OpenAI provider declares
known GPT-5 reasoning models and sends `reasoning_effort` through the
OpenAI-compatible chat-completions adapter. OpenRouter and Hugging Face remain
disabled unless an OpenAI-compatible provider config explicitly opts in.
Anthropic and Codex-subscription thinking controls are rejected until their
adapters implement a provider-specific mapping.

Tau records an explicit reason when controls are unavailable:

- Providers with no `thinking_levels` report that the provider does not declare
  thinking capability metadata.
- Providers with `thinking_models` report that the active model is not listed
  when the model is outside that capability set.
- OpenAI Codex subscription models report that the adapter can stream reasoning
  output, but Tau does not yet have a supported Codex transport mapping for
  changing reasoning effort.
- Anthropic models report that Anthropic's thinking controls are
  model-specific, and Tau has not mapped them yet.

This keeps the durable provider metadata in `tau_coding`, the provider-specific
runtime knob in `tau_ai`, and the display choice in CLI/TUI code.

## Provider Comparison

OpenAI's public API exposes `reasoning_effort` for chat completions and
`reasoning.effort` for Responses API reasoning models. Supported values are
model-dependent; current docs list `none`, `minimal`, `low`, `medium`, `high`,
and `xhigh`, with defaults and support varying by model. Tau's direct OpenAI
entry maps Tau's normalized levels to `reasoning_effort` only for configured
reasoning-capable models.

Codex clients expose `model_reasoning_effort` for supported models, but the
documented configuration is Responses-API-specific and model-dependent. Tau's
subscription adapter talks to the ChatGPT Codex subscription transport and
currently only includes streamed reasoning content; it does not send a
reasoning-effort request parameter. That is why `openai-codex:gpt-5.5` shows
thinking controls as unavailable today.

Anthropic has used both explicit extended-thinking token budgets and newer
adaptive/effort controls, with support changing by model family. Tau can stream
Anthropic thinking deltas, but it does not yet expose a normalized control
because a single fixed level list would hide important model-specific behavior.

Models or providers without declared capability metadata are treated as having
no configurable thinking mode. Their existing session thinking setting is kept
while controls are hidden, so switching back to a capable model can reuse that
setting when it is valid. If a capable target model does not support the current
level, Tau coerces to that model/provider default.

## Boundary

Thinking controls remain outside Textual-specific rendering. Provider adapters
translate supported reasoning streams into provider-neutral thinking events,
`tau_agent` forwards those events without recording them as durable assistant
messages, and the Textual TUI decides whether to show or hide them. The built-in
TUI hides thinking tokens by default and exposes `Ctrl+T` as a frontend toggle.

## Tests

The phase is covered by:

```text
tests/test_thinking.py
tests/test_commands.py
tests/test_coding_session.py
tests/test_agent_loop.py
tests/test_tau_ai.py
tests/test_tui_adapter.py
tests/test_tui_config.py
tests/test_tui_app.py
```
