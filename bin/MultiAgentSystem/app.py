from .ochestrator import build_mas_graph,multiagent_chat_once
from .agents import create_all_agents
from .state_schema import State
import uuid 
import sys, time

def print_turn_summary(next_state: dict):
    sep = "-" * 80
    big_sep = "=" * 80

    print("\n" + big_sep)
    print(" MULTI-AGENT TURN SUMMARY ".center(80, "="))
    print(big_sep + "\n")

    # Idea Generator
    print("IDEA GENERATOR".center(80, "-"))
    print(next_state["idea_generator_reply"], "\n")

    # Subject Specialist
    print("SUBJECT SPECIALIST".center(80, "-"))
    print(next_state["subject_specialist_reply"], "\n")

    # Critic
    print("CRITIC".center(80, "-"))
    print(next_state["critic_reply"], "\n")

    # Idea Board
    print("IDEA BOARD SO FAR".center(80, "-"))
    print(next_state["idea_board"], "\n")

    # Facilitator
    print("FACILITATOR".center(80, "-"))
    print(next_state["facilitator_reply"], "\n")

    print(big_sep + "\n")

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

if __name__ == "__main__":
    # Example usage
    # change the subject and user message as needed

    thread_id = str(uuid.uuid4())
    subject = "Climate Change"
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
        "iteration": 1,
        "thread_id": thread_id
    }

    #create agents and the MAS graph
    facilitator, idea_generator, subject_specialist, idea_structurer, critic = create_all_agents(initial_state)
    mas = build_mas_graph(idea_generator, facilitator, idea_structurer, subject_specialist, critic)
    
    while True:
        next_state = run_and_print(mas, initial_state, initial_state["thread_id"])
        #print_turn_summary(next_state)
        initial_state = next_state
        user_message = input("Your turn (type 'exit' to quit): ")
        if user_message.lower() == 'exit':
            break
        initial_state["user_message"] = user_message