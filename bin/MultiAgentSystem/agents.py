from typing import Literal, List, Dict
from dataclasses import dataclass

Stage = Literal["brainstorming", "structuring", "refining"]

@dataclass
class AgentPersona:
    name: str
    visible_to_student: bool
    stages: List[Stage]   # where this agent is active
    base_prompt: str      # role description template

AGENT_PERSONAS: Dict[str, AgentPersona] = {
    "Facilitator": AgentPersona(
        name="Facilitator",
        visible_to_student=True,
        stages=["brainstorming", "structuring", "refining"],
        base_prompt=(
            "You are a Facilitator helping a student plan their essay writing.\n"
            "Guide them with open questions, reflections, and short suggestions.\n"
            "Do NOT write the essay for them. Keep answers concise."
        ),
    )}


def get_agent(name: str) -> AgentPersona:
    return AGENT_PERSONAS[name]
