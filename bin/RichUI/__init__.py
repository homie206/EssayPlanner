"""
Rich Console UI for AI4ED Multi-Agent Essay Planning System.

This module provides a beautiful terminal interface using the Rich library,
completely separated from the core multi-agent orchestration logic.

The UI maintains conversation history for display purposes only, while the
backend orchestrator remains stateless. Each call to the backend is independent,
allowing the core team to develop the multi-agent system without interference.

Components:
-----------
- RichConsoleUI: Main UI orchestrator
- ConversationManager: Manages message history for display
- Message: Data model for conversation messages
- InputHandler: Handles user input with multi-line support
- DisplayRenderer: Renders Rich panels, spinners, and formatting

Usage:
------
    from bin.RichUI import RichConsoleUI

    ui = RichConsoleUI(subject="Social media impact")
    ui.run()

Or run directly as a module:
    python -m bin.RichUI.app
    python -m bin.RichUI.app --subject "Essay topic"
"""

from .console_ui import RichConsoleUI
from .conversation_manager import ConversationManager, Message
from .input_handler import InputHandler
from .display_renderer import DisplayRenderer

__all__ = [
    "RichConsoleUI",
    "ConversationManager",
    "Message",
    "InputHandler",
    "DisplayRenderer",
]

__version__ = "1.0.0"
