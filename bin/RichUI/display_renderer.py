"""
Rich-based visual rendering for the console UI.

This module handles all Rich-specific rendering including panels, spinners,
color formatting, and visual layout of the conversation interface.
"""

from contextlib import contextmanager
from typing import List
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from .conversation_manager import Message


class DisplayRenderer:
    """Renders UI elements using the Rich library."""

    # Style configuration
    USER_STYLE = "bold green"
    ASSISTANT_STYLE = "bold blue"
    SYSTEM_STYLE = "bold yellow"
    HISTORY_STYLE = "dim"

    def __init__(self, console: Console):
        """
        Initialize the display renderer.

        Args:
            console: Rich Console instance for output
        """
        self.console = console

    def render_welcome(self, subject: str) -> None:
        """
        Display welcome screen with essay subject.

        Args:
            subject: The essay topic/subject
        """
        welcome_text = f"""[bold cyan]AI4ED Essay Planning Assistant[/bold cyan]

Subject: [bold]{subject}[/bold]

The Facilitator will help you brainstorm ideas and structure your essay.

[dim]Input:[/dim]
• Press [bold]Enter[/bold] to send your message
• Press [bold]Alt+Enter[/bold] (or [bold]Esc+Enter[/bold]) for multi-line input

[dim]Commands:[/dim]
• [bold]/help[/bold] - Show help
• [bold]/clear[/bold] - Clear conversation history
• [bold]/quit[/bold] or [bold]/exit[/bold] - Exit

"""

        self.console.print(Panel(
            welcome_text,
            title="[bold]Welcome[/bold]",
            border_style="cyan",
            padding=(1, 2)
        ))

    def render_user_message(self, message: str, dimmed: bool = False) -> None:
        """
        Display a user message in a green panel.

        Args:
            message: The user's message text
            dimmed: Whether to display with dimmed styling (for history)
        """
        border_style = "dim green" if dimmed else "green"
        title_style = "[dim green]You[/dim green]" if dimmed else "[green]You[/green]"

        self.console.print(Panel(
            message,
            title=title_style,
            title_align="left",
            border_style=border_style,
            padding=(0, 1),
            expand=False
        ))

    def render_assistant_message(self, message: str, dimmed: bool = False) -> None:
        """
        Display an assistant message in a blue panel.

        Args:
            message: The assistant's response text
            dimmed: Whether to display with dimmed styling (for history)
        """
        border_style = "dim blue" if dimmed else "blue"
        title_style = "[dim blue]Facilitator[/dim blue]" if dimmed else "[blue]Facilitator[/blue]"

        self.console.print(Panel(
            message,
            title=title_style,
            title_align="left",
            border_style=border_style,
            padding=(0, 1),
            expand=False
        ))

    def render_system_message(self, message: str) -> None:
        """
        Display a system message in a yellow panel.

        Args:
            message: The system message text
        """
        self.console.print(Panel(
            message,
            title="[yellow]System[/yellow]",
            title_align="left",
            border_style="yellow",
            padding=(0, 1),
            expand=False
        ))

    @contextmanager
    def show_spinner_while_processing(self):
        """
        Context manager to show a spinner during LLM processing.

        Usage:
            with renderer.show_spinner_while_processing():
                response = llm_call()
        """
        with self.console.status(
            "[bold blue]Facilitator is thinking...",
            spinner="dots"
        ):
            yield

    def render_conversation_history(self, messages: List[Message]) -> None:
        """
        Display conversation scrollback with dimmed styling.

        Shows previous turns (excluding the most recent) to provide context
        while keeping focus on the current conversation.

        Args:
            messages: List of messages to display (should exclude current turn)
        """
        if not messages:
            return

        self.console.print()
        self.console.rule("[dim]Recent Conversation[/dim]")
        self.console.print()

        for msg in messages:
            if msg.role == "user":
                self.render_user_message(msg.content, dimmed=True)
            elif msg.role == "assistant":
                self.render_assistant_message(msg.content, dimmed=True)
            elif msg.role == "system":
                self.console.print(f"[dim yellow]{msg.content}[/dim yellow]")

        self.console.print()
        self.console.rule("[dim]End of History[/dim]")
        self.console.print()

    def render_help_text(self) -> None:
        """Display help information about commands and usage."""
        help_text = """[bold cyan]AI4ED Essay Planning Assistant - Help[/bold cyan]

[bold]Basic Usage:[/bold]
1. Type your message and press [bold]Enter[/bold] to send
2. The Facilitator will respond to help you plan your essay

[bold]Multi-line Input:[/bold]
• Press [bold]Alt+Enter[/bold] (or [bold]Esc+Enter[/bold]) to create a new line
• Continue typing additional lines
• Press [bold]Enter[/bold] to send your complete message

Example:
  You: I want to write about [Press Alt+Enter]
  ... social media effects [Press Alt+Enter]
  ... on teenagers [Press Enter to send]

[bold]Commands:[/bold]
• [bold]/help[/bold] - Show this help message
• [bold]/clear[/bold] - Clear conversation history
• [bold]/quit[/bold] or [bold]/exit[/bold] - Exit the application

[bold]Tips:[/bold]
• The Facilitator remembers your essay subject throughout the conversation
• Ask open-ended questions to get the most helpful guidance
• Use multi-line input for longer, more detailed messages
"""

        self.console.print(Panel(
            help_text,
            title="[bold]Help[/bold]",
            border_style="cyan",
            padding=(1, 2)
        ))

    def clear_screen(self) -> None:
        """Clear the console screen."""
        self.console.clear()

    def print_info(self, message: str) -> None:
        """
        Print an informational message.

        Args:
            message: The message to display
        """
        self.console.print(f"[dim]{message}[/dim]")

    def print_error(self, message: str) -> None:
        """
        Print an error message.

        Args:
            message: The error message to display
        """
        self.console.print(f"[bold red]Error:[/bold red] {message}")
