#!/usr/bin/env python3
"""
Rich Console UI for AI4ED Multi-Agent Essay Planning System.

This is the entry point for the Rich-based terminal interface.
It provides a modern, interactive console experience with panels,
spinners, and conversation history.

Usage:
    python -m bin.RichUI.app
    python -m bin.RichUI.app --subject "Your essay topic"
"""

import argparse
import sys
from rich.console import Console

from .console_ui import RichConsoleUI


def main():
    """Main entry point for the Rich Console UI."""
    parser = argparse.ArgumentParser(
        description="AI4ED Essay Planning Assistant (Rich UI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m bin.RichUI.app
  python -m bin.RichUI.app --subject "Social media and mental health"

Commands available during conversation:
  /help  - Show help information
  /clear - Clear conversation history
  /quit  - Exit the application
        """
    )

    parser.add_argument(
        "--subject",
        type=str,
        default=None,
        help="Essay subject (you will be prompted if not provided)"
    )

    args = parser.parse_args()

    try:
        console = Console()

        # Get subject from args or prompt user
        if args.subject:
            subject = args.subject
        else:
            subject = console.input("[bold cyan]Essay subject:[/bold cyan] ").strip()

            # Validate subject is not empty
            if not subject:
                console.print("[bold red]Error:[/bold red] Subject cannot be empty")
                sys.exit(1)

        # Initialize and run UI
        ui = RichConsoleUI(subject=subject)
        ui.run()

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        console = Console()
        console.print("\n\n[bold cyan]Goodbye![/bold cyan]\n")
        sys.exit(0)

    except Exception as e:
        # Handle unexpected errors
        console = Console()
        console.print(f"\n[bold red]Error:[/bold red] {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
