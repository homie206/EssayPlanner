from .llm_connector import create_agent, chat
from .prompts import build_prompt_for_agent
from .tools import Tools
from .ochestrator import PlanningModule
from .agents import create_all_agents
from .state_schema import State
import uuid 
import sys, time



thread_id = str(uuid.uuid4())
subject = "Education"
user_message = input("What would you like to write an essay about? ")
initial_state: State = {
    "idea_board": "",
    "structures": [],
    "subject": subject,
    "user_message": user_message,
    "facilitator_turn": 1,
    "facilitator_reply": "",
    "idea_generator_reply": "",
    "subject_specialist_reply": "",
    "critic_reply": "",
    "facilitation_done": False,
    "iteration": 0,
    "thread_id": thread_id,
    "essay_topic": user_message,
    "route": "none"
}
#create agents and the MAS graph
facilitator, idea_generator, subject_specialist, idea_structurer, critic, router = create_all_agents(initial_state)
planning_module = PlanningModule(idea_generator, facilitator, idea_structurer, subject_specialist, critic, router)

while True:
    for node, key, value in planning_module.stream_updates(initial_state, thread_id):
        print(f"\n[{node}] {key}:\n{value}\n")

    #print("User message:", next_state["user_message"])
    #print_turn_summary(next_state)
    #initial_state = next_state
    
    #user_message = input("Your turn (type 'exit' to quit): ")
    #if user_message.lower() == 'exit':
    #    break
    #initial_state["user_message"] = user_message