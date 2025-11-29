# AI4Ed Turing Project

## Multi-Agent Systems for Multi-Party Human-AI Interaction

A research project investigating how multi-agent systems can enhance essay writing through collaborative AI interactions.

### Team Members
- Alan O'Connell
- Don Rasula Dhakshaka Atapattu
- Raymon JS Narwal

**Supervisor:** Zheng Yuan

### Project Overview

This project develops a prototype system with three interconnected modules to support student essay writing:

1. **Planning Module** - Pre-writing discussions with multiple AI agents (facilitator, challenger, supporter) to help students brainstorm ideas and explore diverse perspectives
2. **Assessment Module** - Automated band-like scoring aligned with writing rubrics (IELTS, TOEFL)
3. **Feedback Module** - Surface-level corrections and deeper guidance on coherence, organization, and argument quality

### Key Features

- Multi-agent collaboration with different AI personas representing various cultural and linguistic backgrounds
- Critic agents for evaluation and feedback
- Integration with existing assessment and feedback systems
- Flexible, expandable design for future enhancements

### Technical Approach

- Prioritizing local LLM models (privacy concerns, especially for minors)
- Flexible implementation allowing easy model switching
- Limited OpenAI credits ($2000) available for testing

### Project Timeline

**Semester 1 (Weeks 1-12)**
- Week 1-3: Team forming and project setup
- Week 4-10: Research and development
- Week 11: Interim presentation
- Week 12: Interim report

**Semester 2 (Weeks 1-12)**
- Week 1-10: Continued development
- Week 11: Final presentation
- Week 12: Final report

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

3. Set up environment variables:
Create a `.env` file in the project root (get from folder in google drive):
```bash
OPENAI_API_KEY=your_api_key_here
```

#### Running the Application

To run the basic multi-agent system example:

```bash
uv run python -m bin.MultiAgentSystem.app
```

This will run a demo conversation where a facilitator agent helps a student brainstorm an essay about social media's impact on mental health.

#### Project Structure

```
.
├── bin/
│   └── MultiAgentSystem/
│       ├── agents.py          # Agent persona definitions
│       ├── llm_connector.py   # OpenAI/LangChain integration
│       ├── ochestrator.py     # LangGraph multi-agent orchestration
│       ├── prompts.py         # Prompt building utilities
│       └── app.py             # Example application
├── main.py                    # Project entry point
├── pyproject.toml             # Project dependencies and metadata
└── readme.md                  # This file
```

### Resources

- **Module:** COM4520 Turing Research Project
- **Academic Year:** 2025/2026
- **University:** University of Sheffield, Computer Science Department

### Ethics

This project will follow the University of Sheffield's Ethics Review Procedure with appropriate consent forms and data protection measures.

---

*This is an early-stage research project. Documentation and features will be updated as development progresses.*
