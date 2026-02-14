from .llm_connector import create_agent
from .prompts import build_prompt_for_agent
from .tools import Tools
from .ochestrator import State  # adjust if State is elsewhere


def create_all_agents(state: State):
    """Create all agents for the MAS and return them in a fixed order.

    Order:
      1) facilitator
      2) idea_generator
      3) subject_specialist
      4) idea_structurer
      5) critic
    """

    # Facilitator
    facilitator_prompt = build_prompt_for_agent("Facilitator", state["subject"])
    facilitator_agent = create_agent(facilitator_prompt)

    # Idea Generator
    idea_gen_prompt = build_prompt_for_agent("IdeaGenerator", state["subject"])
    idea_generator_agent = create_agent(
        idea_gen_prompt,
        tools=[Tools.google_search],
    )

    # Subject Specialist
    subject_prompt = build_prompt_for_agent("SubjectSpecialist", state["subject"])
    subject_specialist_agent = create_agent(
        subject_prompt,
        tools=[Tools.knowledge_retreiver],
    )

    # Idea Structurer
    structurer_prompt = build_prompt_for_agent("Idea_Structurer", state["subject"])
    idea_structurer_agent = create_agent(structurer_prompt)

    #critic
    critic_prompt = build_prompt_for_agent("Critic", state["subject"])
    critic_agent = create_agent(critic_prompt, model_name="gpt-5")

    return (
        facilitator_agent,
        idea_generator_agent,
        subject_specialist_agent,
        idea_structurer_agent,
        critic_agent
    )
