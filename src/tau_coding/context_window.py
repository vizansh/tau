"""Approximate context-size estimation for Tau coding sessions."""

from dataclasses import dataclass

from tau_agent.messages import AgentMessage
from tau_agent.tools import AgentTool

CHARS_PER_TOKEN = 4
MESSAGE_OVERHEAD_TOKENS = 4
TOOL_OVERHEAD_TOKENS = 16
SUMMARY_MESSAGE_CHAR_LIMIT = 500


@dataclass(frozen=True, slots=True)
class ContextUsageEstimate:
    """Deterministic context-size accounting for one provider request."""

    total_tokens: int
    system_tokens: int
    message_tokens: int
    tool_tokens: int
    message_count: int
    tool_count: int


def estimate_text_tokens(text: str) -> int:
    """Return a deterministic rough token estimate for text."""
    if not text:
        return 0
    return max(1, (len(text) + CHARS_PER_TOKEN - 1) // CHARS_PER_TOKEN)


def estimate_message_tokens(message: AgentMessage) -> int:
    """Return a rough token estimate for one provider-neutral message."""
    match message.role:
        case "user":
            return MESSAGE_OVERHEAD_TOKENS + estimate_text_tokens(message.content)
        case "assistant":
            tool_call_tokens = sum(
                estimate_text_tokens(call.name) + estimate_text_tokens(str(call.arguments))
                for call in message.tool_calls
            )
            return (
                MESSAGE_OVERHEAD_TOKENS
                + estimate_text_tokens(message.content)
                + tool_call_tokens
            )
        case "tool":
            return (
                MESSAGE_OVERHEAD_TOKENS
                + estimate_text_tokens(message.name)
                + estimate_text_tokens(message.content)
            )


def estimate_tool_tokens(tool: AgentTool) -> int:
    """Return a rough token estimate for one tool definition."""
    return (
        TOOL_OVERHEAD_TOKENS
        + estimate_text_tokens(tool.name)
        + estimate_text_tokens(tool.description)
        + estimate_text_tokens(str(tool.input_schema))
    )


def estimate_context_tokens(
    *,
    system: str,
    messages: tuple[AgentMessage, ...],
    tools: tuple[AgentTool, ...],
) -> int:
    """Return a rough estimate of the active provider context size."""
    return estimate_context_usage(system=system, messages=messages, tools=tools).total_tokens


def estimate_context_usage(
    *,
    system: str,
    messages: tuple[AgentMessage, ...],
    tools: tuple[AgentTool, ...],
) -> ContextUsageEstimate:
    """Return deterministic context accounting for the active provider request."""
    system_tokens = estimate_text_tokens(system)
    message_tokens = sum(estimate_message_tokens(message) for message in messages)
    tool_tokens = sum(estimate_tool_tokens(tool) for tool in tools)
    return ContextUsageEstimate(
        total_tokens=system_tokens + message_tokens + tool_tokens,
        system_tokens=system_tokens,
        message_tokens=message_tokens,
        tool_tokens=tool_tokens,
        message_count=len(messages),
        tool_count=len(tools),
    )


def summarize_messages_for_compaction(messages: tuple[AgentMessage, ...]) -> str:
    """Build a deterministic compact summary from provider-neutral messages."""
    if not messages:
        return "No prior messages."
    lines = [f"Automatically compacted {len(messages)} prior message(s)."]
    for index, message in enumerate(messages, start=1):
        lines.append(f"{index}. {message.role}: {_message_text(message)}")
    return "\n".join(lines)


def _message_text(message: AgentMessage) -> str:
    match message.role:
        case "user":
            return _truncate_summary_text(message.content)
        case "assistant":
            suffix = ""
            if message.tool_calls:
                names = ", ".join(call.name for call in message.tool_calls)
                suffix = f" [tool calls: {names}]"
            return _truncate_summary_text(f"{message.content}{suffix}")
        case "tool":
            prefix = f"{message.name} {'ok' if message.ok else 'failed'}: "
            return _truncate_summary_text(f"{prefix}{message.content}")


def _truncate_summary_text(text: str) -> str:
    collapsed = " ".join(text.split())
    if len(collapsed) <= SUMMARY_MESSAGE_CHAR_LIMIT:
        return collapsed
    return collapsed[: SUMMARY_MESSAGE_CHAR_LIMIT - 3].rstrip() + "..."
