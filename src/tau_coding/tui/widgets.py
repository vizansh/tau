"""Small Textual widgets for Tau's interactive TUI."""

from rich.text import Text
from textual.widgets import RichLog

from tau_coding.tui.state import ChatItem, TuiState

_ROLE_LABELS = {
    "user": "you",
    "assistant": "assistant",
    "tool": "tool",
    "error": "error",
    "status": "status",
}

_ROLE_STYLES = {
    "user": "bold cyan",
    "assistant": "bold green",
    "tool": "yellow",
    "error": "bold red",
    "status": "dim",
}


class TranscriptView(RichLog):
    """Scrollable transcript view backed by ``TuiState``."""

    def update_from_state(self, state: TuiState) -> None:
        """Redraw the transcript from display state."""
        self.clear()
        for item in state.items:
            self.write(render_chat_item(item))
        if state.assistant_buffer:
            self.write(render_chat_item(ChatItem(role="assistant", text=state.assistant_buffer)))


def render_chat_item(item: ChatItem) -> Text:
    """Render a chat item as Rich text."""
    label = _ROLE_LABELS[item.role]
    style = _ROLE_STYLES[item.role]
    text = Text()
    text.append(f"{label}: ", style=style)
    text.append(item.text)
    return text
