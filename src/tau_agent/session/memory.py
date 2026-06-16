"""In-memory session state reconstruction."""

from dataclasses import dataclass

from tau_agent.messages import AgentMessage
from tau_agent.session.entries import (
    CustomEntry,
    SessionEntry,
    SessionInfoEntry,
)
from tau_agent.session.tree import path_to_entry


@dataclass(frozen=True, slots=True)
class SessionState:
    """Current session state derived from append-only entries."""

    messages: tuple[AgentMessage, ...]
    model: str | None
    thinking_level: str | None
    label: str | None
    active_leaf_id: str | None
    session_info: SessionInfoEntry | None
    custom_entries: tuple[CustomEntry, ...]
    entries: tuple[SessionEntry, ...]

    @classmethod
    def from_entries(
        cls,
        entries: list[SessionEntry],
        *,
        leaf_id: str | None = None,
    ) -> SessionState:
        """Replay entries into state.

        When `leaf_id` is provided, only the root-to-leaf path is replayed. Without
        it, entries are replayed linearly in storage order.
        """
        replay_entries = path_to_entry(entries, leaf_id) if leaf_id is not None else entries

        messages: list[AgentMessage] = []
        model: str | None = None
        thinking_level: str | None = None
        label: str | None = None
        active_leaf_id: str | None = leaf_id
        session_info: SessionInfoEntry | None = None
        custom_entries: list[CustomEntry] = []

        for entry in replay_entries:
            match entry.type:
                case "message":
                    messages.append(entry.message)
                case "model_change":
                    model = entry.model
                case "thinking_level_change":
                    thinking_level = entry.thinking_level
                case "label":
                    label = entry.label
                case "leaf":
                    active_leaf_id = entry.entry_id
                case "session_info":
                    session_info = entry
                case "custom":
                    custom_entries.append(entry)
                case "compaction" | "branch_summary":
                    pass

        return cls(
            messages=tuple(messages),
            model=model,
            thinking_level=thinking_level,
            label=label,
            active_leaf_id=active_leaf_id,
            session_info=session_info,
            custom_entries=tuple(custom_entries),
            entries=tuple(replay_entries),
        )
