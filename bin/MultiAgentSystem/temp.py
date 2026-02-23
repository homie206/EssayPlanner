from .idea_gen import IdeationSubgraph
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
    "route": "none"
}
#create agents and the MAS graph
facilitator, idea_generator, subject_specialist, idea_structurer, critic, router = create_all_agents(initial_state)
ideation = IdeationSubgraph(
            facilitator,
            router,
            idea_generator,
            subject_specialist,
            idea_structurer
        )
print("Saved:", ideation.save_mermaid_png())   # writes ideation_subgraph.png