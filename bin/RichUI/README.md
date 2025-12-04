# Rich Console UI

A modern, interactive terminal interface for the AI4ED Essay Planning Assistant using the [Rich](https://rich.readthedocs.io/) library.

## Features

- **Live conversation display** with color-coded Rich panels
- **Typing indicators/spinners** during LLM processing
- **Conversation history scrollback** (last 5 turns)
- **Multi-line input support** via delimiter (`>>>`)
- **Special commands** (`/help`, `/clear`, `/quit`)
- **Completely separated** from core multiagent system

## Architecture

The Rich UI is completely isolated from the backend multiagent system in `bin/MultiAgentSystem/`. This separation ensures:

- No interference with core team development
- Backend remains stateless
- UI can be swapped or updated independently
- Easy to switch between basic CLI and Rich UI

### Components

```
bin/RichUI/
├── __init__.py              # Module exports
├── app.py                   # Entry point with argument parsing
├── console_ui.py            # Main UI orchestrator
├── conversation_manager.py  # Message history tracking (UI-only)
├── input_handler.py         # Multi-line input with delimiter
└── display_renderer.py      # Rich panels, spinners, formatting
```

### Data Flow

```
User Input → InputHandler → RichConsoleUI
                                ↓
                    ConversationManager (UI state)
                                ↓
                    DisplayRenderer (show message)
                                ↓
            multiagent_chat_once() [STATELESS BACKEND]
                                ↓
                    ConversationManager (store response)
                                ↓
                    DisplayRenderer (show response + history)
```

## Usage

### Run the Rich UI

```bash
# Interactive mode (will prompt for subject)
uv run python -m bin.RichUI.app

# With subject specified
uv run python -m bin.RichUI.app --subject "Social media and mental health"

# Show help
uv run python -m bin.RichUI.app --help
```

### Basic CLI (Alternative)

The original basic CLI is still available:

```bash
uv run python -m bin.MultiAgentSystem.app
```

## User Guide

### Single-line Messages

Type your message and press Enter:

```
You: What should I write about?

[Facilitator responds]
```

### Multi-line Messages

1. Type your first line and press Enter
2. Continue typing additional lines (press Enter after each)
3. Type `>>>` on a new line and press Enter to send

Example:

```
You: I want to write about
... the impact of social media
... on teenagers' mental health
... >>>

[Message sent to Facilitator]
```

### Commands

- `/help` - Show help information and commands
- `/clear` - Clear conversation history (UI-only, backend remains stateless)
- `/quit` or `/exit` - Exit the application
- Empty input - Re-prompts for input

### Visual Feedback

- **User messages**: Green panels with "You" title
- **Assistant messages**: Blue panels with "Facilitator" title
- **History**: Dimmed panels for previous turns
- **Spinner**: "Facilitator is thinking..." during LLM processing
- **Scrollback**: Last 5 turns displayed after each response

## Design Decisions

### Stateless Backend

The backend `multiagent_chat_once(subject, user_message)` function remains completely stateless. Each call is independent, with NO conversation history passed to the backend.

**Why?**
- Core team can modify orchestrator without breaking UI
- Future features (conversation memory, RAG) can be added to backend independently
- Clear separation of concerns

### UI-Side Conversation History

The `ConversationManager` tracks messages purely for display purposes. It maintains a rolling window of the last 5 turns (10 messages) to show scrollback.

### Delimiter-Based Multi-line Input

Uses `>>>` as a delimiter to end multi-line input, rather than external editors or complex keyboard shortcuts.

**Why?**
- No external dependencies beyond Rich
- Simple to explain and use
- Familiar to Python users (similar to REPL)
- Works in any terminal

### Rolling Window of 5 Turns

Displays the last 5 conversation turns to keep the terminal readable while providing sufficient context.

## Dependencies

Only one new dependency:

```toml
rich==14.2.0  # Terminal formatting, panels, spinners
```

Installed automatically with:

```bash
uv add rich
```

## Development

### File Modifications

**Created** (new files):
- `bin/RichUI/` (entire directory)

**Modified**:
- `pyproject.toml` (added Rich dependency)

**Not Modified** (backend remains unchanged):
- `bin/MultiAgentSystem/` (all files)

### Testing

1. **Import test**:
```bash
uv run python -c "from bin.RichUI import RichConsoleUI; print('OK')"
```

2. **Help test**:
```bash
uv run python -m bin.RichUI.app --help
```

3. **Interactive test**:
```bash
uv run python -m bin.RichUI.app --subject "Test topic"
# Try single-line input
# Try multi-line input with >>>
# Try /help command
# Try /clear command
# Try /quit command
```

### Edge Cases to Test

- Empty input (should re-prompt)
- Very long messages (100+ lines)
- Special characters in messages
- LLM errors/timeouts (graceful error handling)
- Ctrl+C interruption (clean exit)
- Multi-line with empty lines

## Future Enhancements

- [ ] Configurable history size: `--history=10`
- [ ] Session export to markdown
- [ ] Session save/load
- [ ] Elapsed time display during LLM calls
- [ ] Multiple agent styling (when Challenger/Supporter added)
- [ ] Streaming responses (if backend supports it)
- [ ] Markdown rendering in assistant responses

## Troubleshooting

### Rich Not Displaying Correctly

Rich requires a terminal that supports ANSI escape codes. Most modern terminals work fine:
- Linux: bash, zsh (built-in)
- macOS: Terminal.app, iTerm2
- Windows: Windows Terminal, PowerShell 7+

If Rich doesn't work, fall back to the basic CLI:
```bash
uv run python -m bin.MultiAgentSystem.app
```

### Import Errors

Ensure you're running from the project root:
```bash
cd /home/ray/AI4ED/AI4ED-turing-project
uv run python -m bin.RichUI.app
```

### LLM Errors

If the backend fails, the UI displays an error message and allows you to retry or quit. Check:
- `.env` file contains valid `OPENAI_API_KEY`
- Internet connection is available
- OpenAI API is accessible

## Contributing

When adding features to the Rich UI:

1. **Do NOT modify** files in `bin/MultiAgentSystem/`
2. Keep UI logic in RichUI module
3. Maintain stateless backend contract
4. Update this README with new features
5. Test all commands and edge cases

## License

Same as parent project (AI4ED Turing Project).
