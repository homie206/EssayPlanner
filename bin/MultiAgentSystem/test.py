from .llm_connector import create_agent, chat
from .prompts import build_prompt_for_agent
from .tools import Tools
from .ochestrator import build_mas_graph,multiagent_chat_once
from .agents import create_all_agents
from .state_schema import State
import uuid 
import sys, time

def type_out(text: str, delay: float = 0.02):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)

def run_and_print(mas, initial_state: State, thread_id: str):
    big_sep = "=" * 80
    state = dict(initial_state)
    for agent_name, state_key, reply in multiagent_chat_once(mas, initial_state, thread_id):
        print("\n" + big_sep)
        print(f"[{agent_name}] : ", end="", flush=True)
        type_out(reply, delay=0.02)
        state[state_key] = reply
    return state



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
    "thread_id": thread_id
}
#create agents and the MAS graph
facilitator, idea_generator, subject_specialist, idea_structurer, critic = create_all_agents(initial_state)
mas = build_mas_graph(idea_generator, facilitator, idea_structurer, subject_specialist, critic)

while True:
    next_state = run_and_print(mas, initial_state, initial_state["thread_id"])
    #print("User message:", next_state["user_message"])
    #print_turn_summary(next_state)
    initial_state = next_state
    
    #user_message = input("Your turn (type 'exit' to quit): ")
    #if user_message.lower() == 'exit':
    #    break
    #initial_state["user_message"] = user_message