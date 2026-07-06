# EssayPlanner: A Multi-Agent Assistant for Student Academic Writing Planning

## A Multi-Agent Assistant for Student-Centred Academic Writing Planning

EssayPlanner is a multi-agent system that supports students in the pre-writing and planning stages of academic essays. Through collaborative interaction with multiple AI agents, students can brainstorm ideas, explore diverse perspectives, and structure their arguments before they start writing.

### Project Overview

EssayPlanner provides interconnected modules to support student-centred academic writing planning:

1. **Planning Module** - Pre-writing discussions with multiple AI agents (facilitator, challenger, supporter) to help students brainstorm ideas and explore diverse perspectives
2. **Structuring Module** - Guidance on organising ideas into a coherent essay structure and argument flow
3. **Assessment Module** - Automated band-like scoring aligned with writing rubrics (IELTS, TOEFL)
4. **Feedback Module** - Surface-level corrections and deeper guidance on coherence, organization, and argument quality

### Key Features

- Multi-agent collaboration with different AI personas representing various perspectives
- Critic agents for evaluation and feedback
- Flexible, expandable design for future enhancements
- Flexible implementation allowing easy model switching

### Getting Started

#### Prerequisites

- Python 3.12 or higher
- [UV package manager](https://docs.astral.sh/uv/)
- OpenAI API key

#### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd AI4ED-turing-project
```

2. Install dependencies using UV:
```bash
uv sync
```

3. Activate the Environment:
```bash
source .venv/bin/activate
```

4. Set up environment variables:
Create a `.env` file in the project root (get from folder in google drive):
```bash
OPENAI_API_KEY=your_api_key_here
```


#### Running the Application

You can choose between two user interfaces:

**Option 1: Rich Console UI (Recommended)**

Modern, interactive terminal interface with colored panels, spinners, and conversation history:

```bash
# Interactive mode (will prompt for subject)
uv run python -m bin.RichUI.app

# With subject specified
uv run python -m bin.RichUI.app --subject "Social media and mental health"
```

Features:
- Live conversation display with color-coded Rich panels
- Typing indicators/spinners during LLM processing
- Conversation history scrollback (last 5 turns)
- Multi-line input support (use `>>>` to finish)
- Commands: `/help`, `/clear`, `/quit`

See `bin/RichUI/README.md` for detailed usage guide.

**Option 2: Basic CLI**

Simple command-line interface (original):

```bash
uv run python -m bin.MultiAgentSystem.app
```

This runs a demo conversation where a facilitator agent helps a student brainstorm an essay about social media's impact on mental health.

**Option 4 : (MOST RECENT) SERVER AND FRONTEND**

first from project root folder run:

```bash
uvicorn bin.MultiAgentSystem.app:app --reload --host 127.0.0.1 --port 8000
```

now inorder to run the front end naviagate to the bin/MultiAgentSystem Folder
```bash
cd bin/MultiAgentSystem
```

After run the front end using :
```bash
streamlit run front_end.py
```


Now you should be able to see the chat interface loaded up if you follow the URL into your browser.

**Option 5: Docker (recommended for deployment)**

Requires [Docker](https://docs.docker.com/get-docker/) and Docker Compose.

1. Copy the example env file and fill in your API keys:
```bash
cp .env.example .env
```

2. Build and start both services:
```bash
docker compose up --build
```

The backend will be available at `http://localhost:8000` and the frontend at `http://localhost:8501`.

To stop:
```bash
docker compose down
```

#### Project Structure

```
.
├── bin/
│   ├── MultiAgentSystem/          # Core multi-agent system (backend)
│   │   ├── agents.py              # Agent persona definitions
│   │   ├── llm_connector.py       # OpenAI/LangChain integration
│   │   ├── ochestrator.py         # LangGraph multi-agent orchestration
│   │   ├── prompts.py             # Prompt building utilities
│   │   └── app.py                 # Basic CLI application
│   └── RichUI/                    # Rich Console UI (frontend)
│       ├── console_ui.py          # Main UI orchestrator
│       ├── conversation_manager.py # Message history tracking
│       ├── input_handler.py       # Multi-line input handling
│       ├── display_renderer.py    # Rich panels and formatting
│       ├── app.py                 # Rich UI entry point
│       └── README.md              # Rich UI documentation
├── main.py                        # Project entry point
├── pyproject.toml                 # Project dependencies and metadata
└── readme.md                      # This file
```

### Ethics

This project follows the University's Ethics Review Procedure with appropriate consent forms and data protection measures.
