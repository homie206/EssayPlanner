from .llm_connector import create_agent
from .prompts import build_prompt_for_agent
from .tools import Tools
from .state_schema import State


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
    facilitator_critic_promt = build_prompt_for_agent("Facilitator", state["subject"], agent_turn=2)
    facilitator_agent_ideation = create_agent(facilitator_prompt)
    facilitator_agent_critic = create_agent(facilitator_critic_promt)

    # Idea Generator
    idea_gen_prompt = build_prompt_for_agent("IdeaGenerator", state["subject"])
    idea_generator_agent = create_agent(
        idea_gen_prompt,
        tools=[Tools.tavily_search_tool],
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
    
    #router
    router_prompt = build_prompt_for_agent("Router", state["subject"])
    router_agent = create_agent(router_prompt, model_name="gpt-5")
    
    # Facilitator Structuring
    facilitator_structuring_prompt = build_prompt_for_agent("FacilitatorStructuring", state["subject"])
    facilitator_agent_structuring = create_agent(facilitator_structuring_prompt)

    # Structuring Coach
    structuring_prompt = build_prompt_for_agent("StructuringCoach", state["subject"])
    structuring_coach_agent = create_agent(structuring_prompt)

    # Argument Flow Agent
    argument_flow_prompt = build_prompt_for_agent("ArgumentFlow", state["subject"])
    argument_flow_agent = create_agent(argument_flow_prompt)

    # Structuring Router Agent
    structuring_router_prompt = build_prompt_for_agent("StructuringRouter", state["subject"])
    structuring_router_agent = create_agent(structuring_router_prompt)

    # Structuring Idea Structurer Agent
    structuring_idea_structurer_prompt = build_prompt_for_agent("StructuringIdeaStructurer", state["subject"])
    structuring_idea_structurer_agent = create_agent(structuring_idea_structurer_prompt)

    return (
        facilitator_agent_ideation,
        idea_generator_agent,
        subject_specialist_agent,
        idea_structurer_agent,
        critic_agent,
        router_agent,
        facilitator_agent_critic,
        structuring_coach_agent,
        argument_flow_agent,
        facilitator_agent_structuring,
        structuring_router_agent,
        structuring_idea_structurer_agent,
    )
