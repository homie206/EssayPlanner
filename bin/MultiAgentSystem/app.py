from .ochestrator import build_mas_graph,multiagent_chat_once
from .agents import create_all_agents
from .state_schema import State
import uuid 

if __name__ == "__main__":
    # Example usage
    # change the subject and user message as needed

    thread_id = str(uuid.uuid4())
    subject = "The impact of social media on mental health"
    user_message = input("What would you like to write an essay about? ")
    initial_state: State = {
        "idea_board": "",
        "structures": [],
        "subject": subject,
        "user_message": user_message,
        "facilitator_turn": 1,
        "facilitator_reply_1": "",
        "facilitator_reply_2": "",
        "idea_generator_reply": "",
        "iteration": 0,
        "thread_id": thread_id
    }

    #create agents and the MAS graph
    facilitator, idea_generator, subject_specialist, idea_structurer = create_all_agents(initial_state)
    mas = build_mas_graph(idea_generator, facilitator, idea_structurer, subject_specialist)
    
    while True:
        next_state = multiagent_chat_once(mas, initial_state, initial_state["thread_id"])
        print("Facilitator says:", next_state["facilitator_reply_1"])
        print("Idea Generator says:", next_state["idea_generator_reply"])
        print("Facilitator says:", next_state["facilitator_reply_2"])
        print("Subject Specialist says:", next_state["subject_specialist_reply"])
        print("idea board so far:", next_state["idea_board"])
        user_message = input("Your turn (type 'exit' to quit): ")
        if user_message.lower() == 'exit':
            break
        initial_state["user_message"] = user_message