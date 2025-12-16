"""
Main UI orchestrator for the Rich Console interface.

This module coordinates all UI components and manages the main event loop
"""

import uuid
from rich.console import Console

from bin.MultiAgentSystem.ochestrator import build_mas_graph, multiagent_chat_once
from bin.MultiAgentSystem.agents import create_all_agents
from bin.MultiAgentSystem.state_schema import State
from .conversation_manager import ConversationManager
from .input_handler import InputHandler
from .display_renderer import DisplayRenderer
from .agent_config import AGENT_CONFIG


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
        self.thread_id = str(uuid.uuid4())

        # Initialize components
        self.conversation_manager = ConversationManager(max_history=5)
        self.input_handler = InputHandler(self.console)
        self.display_renderer = DisplayRenderer(self.console)

        # Initialize state
        self.state: State = {
            "idea_board": "",
            "structures": [],
            "subject": subject,
            "user_message": "",
            "facilitator_reply": "",
            "idea_generator_reply": "",
            "subject_specialist_reply": "",
            "critic_reply": "",
            "iteration": 0,
            "thread_id": self.thread_id
        }

        # Create agents and MAS graph
        with self.display_renderer.show_agent_thinking("System", "cyan"):
            facilitator, idea_generator, subject_specialist, idea_structurer, critic = create_all_agents(self.state)
            self.mas = build_mas_graph(idea_generator, facilitator, idea_structurer, subject_specialist, critic)

    def run(self) -> None:
        """
        Run the main event loop.

        Displays welcome screen and enters conversation loop,
        processing user input and displaying responses until user quits.
        """
        # Display welcome screen
        self.display_renderer.render_welcome(self.subject)

        # Show initial prompt to guide the user
        self.console.print("[dim]What would you like help with? Share your thoughts or questions about the essay topic.[/dim]\n")

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
        Process a user message and display agent responses as they stream in.

        This method:
        1. Adds the user message to conversation history
        2. Displays the user message
        3. Streams responses from the multi-agent system
        4. Displays each agent's response as it completes (one by one)

        Args:
            user_message: The user's message text
        """
        # Add to conversation history
        self.conversation_manager.add_user_message(user_message)

        # Display user message
        self.console.print()
        self.display_renderer.render_user_message(user_message)

        # Update state with user message
        self.state["user_message"] = user_message

        # Stream agent responses as they complete
        try:
            self.console.print()
            self.console.rule("[bold cyan]Agent Responses[/bold cyan]")
            self.console.print()

            # Create the streaming generator
            response_stream = multiagent_chat_once(self.mas, self.state, self.thread_id)

            # Show thinking animation while waiting for first response
            with self.display_renderer.show_agent_thinking("Agents", "cyan"):
                # Get first response (this blocks until first agent completes)
                try:
                    first_item = next(response_stream)
                except StopIteration:
                    # No responses generated
                    return

            # Process first response
            agent_name, state_key, reply = first_item
            if agent_name in AGENT_CONFIG:
                config = AGENT_CONFIG[agent_name]
                render_method = getattr(self.display_renderer, config["render_method"])
                render_method(reply)
                self.console.print()
                self.state[state_key] = reply

            # Process remaining responses with thinking animation between each
            while True:
                # Show thinking animation while waiting for next agent
                with self.display_renderer.show_agent_thinking("Agents", "cyan"):
                    try:
                        agent_name, state_key, reply = next(response_stream)
                    except StopIteration:
                        # No more responses
                        break

                # Get agent configuration and render
                if agent_name in AGENT_CONFIG:
                    config = AGENT_CONFIG[agent_name]
                    render_method = getattr(self.display_renderer, config["render_method"])
                    render_method(reply)
                    self.console.print()
                    self.state[state_key] = reply

            # Add facilitator response to conversation history for display purposes
            if self.state.get("facilitator_reply"):
                self.conversation_manager.add_assistant_message(self.state["facilitator_reply"])

        except Exception as e:
            # Handle errors gracefully
            self.display_renderer.print_error(f"Failed to get response: {str(e)}")
            self.console.print("[dim]Please try again or type /quit to exit.[/dim]")
