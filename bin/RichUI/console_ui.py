"""
Main UI orchestrator for the Rich Console interface.

This module coordinates all UI components and manages the main event loop
"""

from rich.console import Console

from bin.MultiAgentSystem.ochestrator import multiagent_chat_once
from .conversation_manager import ConversationManager
from .input_handler import InputHandler
from .display_renderer import DisplayRenderer


class RichConsoleUI:
    """Main UI orchestrator for Rich-based console interface."""

    def __init__(self, subject: str):
        """
        Initialize the Rich Console UI.

        Args:
            subject: The essay subject/topic
        """
        self.console = Console()
        self.subject = subject

        # Initialize components
        self.conversation_manager = ConversationManager(max_history=5)
        self.input_handler = InputHandler(self.console)
        self.display_renderer = DisplayRenderer(self.console)

    def run(self) -> None:
        """
        Run the main event loop.

        Displays welcome screen and enters conversation loop,
        processing user input and displaying responses until user quits.
        """
        # Display welcome screen
        self.display_renderer.render_welcome(self.subject)

        # Main conversation loop
        while True:
            # Get user input
            user_input = self.input_handler.get_user_input()

            # Handle quit
            if user_input is None:
                self.console.print("\n[bold cyan]Goodbye![/bold cyan]\n")
                break

            # Handle empty input (re-prompt)
            if user_input == "":
                continue

            # Handle help command
            if user_input == InputHandler.HELP_COMMAND:
                self.display_renderer.render_help_text()
                continue

            # Handle clear command
            if user_input == InputHandler.CLEAR_COMMAND:
                self.conversation_manager.clear_history()
                self.display_renderer.clear_screen()
                self.display_renderer.render_welcome(self.subject)
                self.console.print("[dim]Conversation history cleared.[/dim]\n")
                continue

            # Process user message
            self._process_user_input(user_input)

    def _process_user_input(self, user_message: str) -> None:
        """
        Process a user message and display the response.

        This method:
        1. Adds the user message to conversation history
        2. Displays the user message
        3. Calls the backend (with spinner)
        4. Adds and displays the response

        Args:
            user_message: The user's message text
        """
        # Add to conversation history
        self.conversation_manager.add_user_message(user_message)

        # Display user message
        self.console.print()
        self.display_renderer.render_user_message(user_message)

        # Call backend with spinner
        try:
            with self.display_renderer.show_spinner_while_processing():
                response = multiagent_chat_once(self.subject, user_message)

            # Add response to conversation history
            self.conversation_manager.add_assistant_message(response)

            # Display response
            self.console.print()
            self.display_renderer.render_assistant_message(response)

        except Exception as e:
            # Handle errors gracefully
            self.display_renderer.print_error(f"Failed to get response: {str(e)}")
            self.console.print("[dim]Please try again or type /quit to exit.[/dim]")
