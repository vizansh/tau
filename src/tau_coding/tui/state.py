"""Display state for Tau's Textual TUI."""

from dataclasses import dataclass, field
from typing import Literal

ChatItemRole = Literal["user", "assistant", "tool", "error", "status"]


@dataclass(slots=True)
class ChatItem:
    """One rendered item in the TUI transcript."""

    role: ChatItemRole
    text: str


@dataclass(slots=True)
class TuiState:
    """Mutable display state for the interactive TUI."""

    items: list[ChatItem] = field(default_factory=list)
    assistant_buffer: str = ""
    running: bool = False
    error: str | None = None

    def add_item(self, role: ChatItemRole, text: str) -> None:
        """Append a transcript item."""
        self.items.append(ChatItem(role=role, text=text))
