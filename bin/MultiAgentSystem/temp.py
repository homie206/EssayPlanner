from .idea_gen_graph import IdeationSubgraph
from .agents import create_all_agents
initial_state = {
        "idea_board": "",
        "structures": [],
        "subject": "subject",
        "turn_user_messages": [],
        "latest_user_message": "essay_topic",
        "facilitator_reply": "",
        "idea_generator_reply": "",
        "subject_specialist_reply": "",
        "critic_reply": "",
        "structuring_coach_reply": "",
        "argument_flow_reply": "",
        "facilitation_done": False,
        "ideation_iteration": 1,
        "critic_iteration": 1,
        "structuring_iteration": 1,
        "thread_id": "thread_id",
        "essay_topic": "essay_topic",
        "route": "none",
        "done": False,
        "structuring_done": False,
    }   
facilitator_ideation, idea_generator, subject_specialist, idea_structurer, critic, router, facilitator_agent_critic, structuring_coach, argument_flow, facilitator_structuring = create_all_agents(initial_state)
graph = IdeationSubgraph(facilitator_ideation,
            router,
            idea_generator,
            subject_specialist,
            idea_structurer)

output_path = graph.save_mermaid_png("my_graph.png")