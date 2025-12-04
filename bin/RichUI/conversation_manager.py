"""
Conversation history management for Rich Console UI.

This module tracks conversation messages for display purposes only.
The backend orchestrator remains stateless - each call to multiagent_chat_once()
is independent. This module maintains a rolling window of recent messages
to provide conversation scrollback in the UI.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Literal


@dataclass
class Message:
    """Single conversation message."""

    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime


class ConversationManager:
    """
    Manages conversation history for display purposes only.

    NOTE: This is UI-only state. The backend orchestrator does NOT receive
    or maintain conversation history. Each backend call is stateless.

    The manager maintains a rolling window of the last N turns (where 1 turn =
    user message + assistant response = 2 messages).
    """

    def __init__(self, max_history: int = 5):
        """
        Initialize conversation manager.

        Args:
            max_history: Maximum number of turns to keep (default: 5 turns = 10 messages)
        """
        self.messages: List[Message] = []
        self.max_history = max_history

    def add_user_message(self, content: str) -> None:
        """
        Add a user message to the conversation history.

        Args:
            content: The user's message text
        """
        msg = Message(
            role="user",
            content=content,
            timestamp=datetime.now()
        )
        self.messages.append(msg)
        self._trim_history()

    def add_assistant_message(self, content: str) -> None:
        """
        Add an assistant response to the conversation history.

        Args:
            content: The assistant's response text
        """
        msg = Message(
            role="assistant",
            content=content,
            timestamp=datetime.now()
        )
        self.messages.append(msg)
        self._trim_history()

    def add_system_message(self, content: str) -> None:
        """
        Add a system message to the conversation history.

        Args:
            content: The system message text
        """
        msg = Message(
            role="system",
            content=content,
            timestamp=datetime.now()
        )
        self.messages.append(msg)
        self._trim_history()

    def get_display_messages(self) -> List[Message]:
        """
        Get messages for display.

        Returns the last N turns worth of messages (max_history turns * 2 messages/turn).

        Returns:
            List of recent messages for display
        """
        max_messages = self.max_history * 2
        return self.messages[-max_messages:]

    def _trim_history(self) -> None:
        """
        Keep only the last N complete turns.

        Trims the message list to maintain only the most recent
        max_history turns (where 1 turn = 2 messages: user + assistant).
        """
        max_messages = self.max_history * 2
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]

    def clear_history(self) -> None:
        """Clear all conversation history."""
        self.messages.clear()

    def get_message_count(self) -> int:
        """Get the total number of messages in history."""
        return len(self.messages)
