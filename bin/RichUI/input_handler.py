"""
User input handling with multi-line support.

This module manages user input using prompt_toolkit, which supports
advanced features like Alt+Enter for multi-line input.
"""

from typing import Optional
from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.filters import Condition


class InputHandler:
    """Handles user input with multi-line support via Alt+Enter."""

    # Special commands
    QUIT_COMMANDS = ['/quit', '/exit', '/q']
    HELP_COMMAND = '/help'
    CLEAR_COMMAND = '/clear'

    def __init__(self, console=None):
        """
        Initialize the input handler.

        Args:
            console: Rich Console instance (kept for compatibility, not used)
        """
        self.console = console
        self.is_multiline = False

    def get_user_input(self) -> Optional[str]:
        """
        Get user input with multi-line support.

        - Press Enter to send message
        - Press Alt+Enter (or Esc+Enter) to add a new line
        - Commands: /quit, /exit, /help, /clear

        Returns:
            The user's message, a command string, or None if user wants to quit.
            Commands: '/help', '/clear', None (for quit)
        """
        try:
            # Create custom key bindings
            bindings = KeyBindings()

            # Track if we're in multiline mode
            self.is_multiline = False

            @bindings.add(Keys.Enter)
            def _(event):
                """Enter key submits the input."""
                event.current_buffer.validate_and_handle()

            @bindings.add(Keys.Escape, Keys.Enter)
            def _(event):
                """Esc+Enter inserts a newline (enables multiline mode)."""
                self.is_multiline = True
                event.current_buffer.insert_text('\n')

            # Also support Alt+Enter on some terminals
            @bindings.add('escape', 'enter')
            def _(event):
                """Alt+Enter inserts a newline (enables multiline mode)."""
                self.is_multiline = True
                event.current_buffer.insert_text('\n')

            # Dynamic prompt continuation based on multiline state
            def get_continuation(width, line_number, is_soft_wrap):
                if self.is_multiline:
                    return HTML('<ansigreen>... </ansigreen><ansiyellow>[Alt+Enter: newline, Enter: send]</ansiyellow> ')
                return HTML('<ansigreen>... </ansigreen>')

            # Use prompt_toolkit with custom key bindings
            user_input = prompt(
                HTML('\n<ansigreen><b>You:</b></ansigreen> '),
                multiline=True,
                prompt_continuation=get_continuation,
                key_bindings=bindings
            ).strip()

        except (EOFError, KeyboardInterrupt):
            return None

        # Check for quit commands
        if user_input.lower() in self.QUIT_COMMANDS:
            return None

        # Check for help command
        if user_input.lower() == self.HELP_COMMAND:
            return self.HELP_COMMAND

        # Check for clear command
        if user_input.lower() == self.CLEAR_COMMAND:
            return self.CLEAR_COMMAND

        # Handle empty input - re-prompt
        if not user_input:
            return ""  # Signal to re-prompt

        return user_input

    def _is_command(self, text: str) -> bool:
        """
        Check if the input is a special command.

        Args:
            text: The input text to check

        Returns:
            True if the text is a command, False otherwise
        """
        text_lower = text.lower()
        return (
            text_lower in self.QUIT_COMMANDS or
            text_lower == self.HELP_COMMAND or
            text_lower == self.CLEAR_COMMAND
        )
