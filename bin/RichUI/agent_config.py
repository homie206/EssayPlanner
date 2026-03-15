"""
Agent configuration mapping for rendering.

Maps agent names (from multiagent_chat_once generator) to:
- Display labels
- Colors for Rich console
- State keys for responses

TODO: This should eventually move to bin/MultiAgentSystem/ when we refactor
      the core system, since this metadata will be useful for web UI and
      other interfaces (not just Rich UI).
"""

AGENT_CONFIG = {
    "idea_generator": {
        "label": "Idea Generator",
        "color": "bright_cyan",
        "emoji": "💡",
        "st_color": "#00bcd4",           # cyan
        "bg_color": "rgba(0,188,212,0.15)",
        "state_key": "idea_generator_reply",
        "render_method": "render_idea_generator",
    },
    "subject_specialist": {
        "label": "Subject Specialist",
        "color": "magenta",
        "emoji": "📚",
        "st_color": "#9c27b0",           # purple
        "bg_color": "rgba(156,39,176,0.15)",
        "state_key": "subject_specialist_reply",
        "render_method": "render_subject_specialist",
    },
    "critic": {
        "label": "Critic",
        "color": "red",
        "emoji": "⚠️",
        "st_color": "#f44336",           # red
        "bg_color": "rgba(244,67,54,0.15)",
        "state_key": "critic_reply",
        "render_method": "render_critic",
    },
    "idea_structurer": {
        "label": "Idea Structurer",
        "color": "yellow",
        "emoji": "📋",
        "st_color": "#f9a825",           # amber
        "bg_color": "rgba(249,168,37,0.15)",
        "state_key": "idea_board",
        "render_method": "render_idea_structurer",
    },
    "facilitator": {
        "label": "Facilitator",
        "color": "blue",
        "emoji": "💬",
        "st_color": "#3f51b5",           # indigo — clearly distinct from cyan
        "bg_color": "rgba(63,81,181,0.15)",
        "state_key": "facilitator_reply",
        "render_method": "render_facilitator",
    },
    "structuring_coach": {
        "label": "Structuring Coach",
        "color": "green",
        "emoji": "🗂️",
        "st_color": "#4caf50",           # green
        "bg_color": "rgba(76,175,80,0.15)",
        "state_key": "structuring_coach_reply",
        "render_method": "render_structuring_coach",
    },
    "argument_flow": {
        "label": "Argument Flow",
        "color": "yellow",
        "emoji": "🔗",
        "st_color": "#ff5722",           # deep orange
        "bg_color": "rgba(255,87,34,0.15)",
        "state_key": "argument_flow_reply",
        "render_method": "render_argument_flow",
    },
}


def get_agent_config(agent_name: str) -> dict:
    """
    Get configuration for an agent by name.

    Args:
        agent_name: Name of the agent (e.g., "idea_generator")

    Returns:
        dict with label, color, state_key, render_method

    Raises:
        KeyError if agent_name not found
    """
    return AGENT_CONFIG[agent_name]
