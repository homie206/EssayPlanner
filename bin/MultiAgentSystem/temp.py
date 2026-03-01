
from .critic_graph import CriticSubgraph
from .agents import create_all_agents
from .state_schema import State

initial_state: State = {
    "idea_board": "",
    "structures": [],
    "subject": "Education",
    "turn_user_messages": [],
    "latest_user_message": "user_message",
    "facilitator_turn": 1,
    "facilitator_reply": "",
    "idea_generator_reply": "",
    "subject_specialist_reply": "",
    "critic_reply": "",
    "facilitation_done": False,
    "iteration": 1,
    "thread_id": "some_thread_id",
    "essay_topic": "Education",
    "route": "none",
    "criticisng_done": False
}
#create agents and the MAS graph
facilitator_agent_ideation,idea_generator_agent,subject_specialist_agent,idea_structurer_agent,critic_agent,router_agent,facilitator_agent_critic = create_all_agents(initial_state)
criticising = CriticSubgraph(facilitator_agent_critic,critic_agent,idea_structurer_agent)
print("Saved:", criticising.save_mermaid_png())   # writes ideation_subgraph.png