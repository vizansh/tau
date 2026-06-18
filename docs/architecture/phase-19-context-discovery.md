# Phase 19: Project Context Discovery and Reload

This phase adds Tau's project instruction discovery and reload command. It stays in
`tau_coding`, beside resources, commands, and session startup.

The implementation lives in:

```text
src/tau_coding/context.py
src/tau_coding/session.py
src/tau_coding/cli.py
src/tau_coding/commands.py
```

## What was added

Tau now discovers markdown instruction files automatically and inserts them into
the existing `ProjectContextFile` system-prompt section.

The current discovery order is:

```text
~/.tau/AGENTS.md
~/.agents/AGENTS.md
<project root>/AGENTS.md
<project root>/.../<cwd>/AGENTS.md
<cwd>/.tau/AGENTS.md
<cwd>/.agents/AGENTS.md
```

The project root is the nearest ancestor containing a common project marker such
as `.git`, `pyproject.toml`, `uv.lock`, `setup.py`, or `package.json`. If no
marker exists, Tau treats the session cwd as the project root.

## System Prompt Integration

Both normal `CodingSession` startup and non-interactive print mode pass
discovered context files into:

```python
BuildSystemPromptOptions(context_files=...)
```

That preserves the Phase 10 prompt boundary:

```text
tau_coding discovers local files
tau_coding.system_prompt formats them
tau_agent receives only a ready system string
```

`tau_agent` still has no dependency on local resource discovery, Tau home,
project paths, slash commands, Rich, or Textual.

## Slash Command

Tau now has:

```text
/context
/reload
```

`/context` lists the active project context files in the running session.

`/reload` refreshes Tau-owned resources for future turns:

- skills
- prompt templates
- project context files
- resource diagnostics
- provider settings used by `/login` and `/model`

When the session is using Tau's generated system prompt, reload also rebuilds
the harness system string so the next model request sees the updated resources
and context. The transcript and session tree are left untouched.

`/status` and `/resources` also include the current context-file count.

## Boundary

Reload is a `tau_coding` operation. It updates the coding-session environment
around the harness, then gives the harness a rebuilt system string for future
turns. `tau_agent` does not know where skills, prompts, context files, or
provider settings come from.

## Tests

The phase is covered by:

```text
tests/test_context.py
tests/test_coding_session.py
tests/test_cli.py
tests/test_commands.py
```

The tests verify:

- user, project, nested, `.tau`, and `.agents` context discovery
- discovered context included in session system prompts
- discovered context included in print-mode system prompts
- `/context`, `/status`, and `/resources` command output
- `/reload` command output
- reload updating resources and the next-turn system prompt
