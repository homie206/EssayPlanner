from .state_schema import State
from .llm_connector import chat
from .idea_gen import IdeationSubgraph
from langgraph.types import Command, interrupt
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver


#def iterate_state(state: State) -> State:
#     return {
#        "iteration": state["iteration"] + 1,
#    } 

def facilitator_node(facilitator_agent, state: State):
        facilitator_input = (
    f"Student message:\n{state['user_message']}\n\n"
    f"Idea board:\n{state.get('idea_board', '')}\n\n"
    f"Outline:\n{state.get('structures', '')}\n\n"
    f"Subject expert notes:\n{state.get('subject_specialist_reply', '')}\n\n"
    f"Critic feedback:\n{state.get('critic_reply', '')}"
)
        reply = chat(
            facilitator_agent,      
            facilitator_input,
            thread_id=state["thread_id"]
        )
        user_reply = interrupt(reply)
        print("User reply:", user_reply)
        return {"facilitator_reply": reply, "user_message": user_reply}
              

def build_mas_graph(idea_generator_agent, facilitator_agent, idea_structurer_agent, subject_specialist_agent, critic_agent, router_agent) -> StateGraph[State]:
    graph_builder = StateGraph(State)
    ideation = IdeationSubgraph(router_agent, idea_generator_agent, subject_specialist_agent)
    
    graph_builder.add_node("facilitator", facilitator_node)
    #graph_builder.add_node("iterate", iterate_state)
    graph_builder.add_edge(START, "facilitator")
    
    #graph_builder.add_edge("brainstorm", "facilitator")
    #graph_builder.add_edge("facilitator", "iterate")
    #graph_builder.add_edge("iterate", END)
    graph_builder.add_edge("brainstorm", END)

    checkpointer = InMemorySaver()
    mas = graph_builder.compile(checkpointer=checkpointer)
    return mas

def multiagent_chat_once(mas, initial_state: State, thread_id: str):
    # final_state = mas.invoke(initial_state, config={"configurable": {"thread_id": thread_id}},)
    #return final_state
    fields = {
        "idea_generator": "idea_generator_reply",
        "subject_specialist": "subject_specialist_reply",
        "critic": "critic_reply",
        "idea_structurer": "idea_board",
        "facilitator": "facilitator_reply",
    }
    initial_input = initial_state 
    
    while True:   
     for _, chunk in mas.stream(
         initial_input,
         config={"configurable": {"thread_id": thread_id}},
         subgraphs=True,
         stream_mode="updates",
     ):
         if "__interrupt__" in chunk:
                 prompt = chunk["__interrupt__"][0].value
             # show prompt + capture student reply from terminal
                 print("\n" + str(prompt))
                 user_response = input("User: ").strip()
 
                 # resume graph
                 initial_input = Command(resume=user_response)
                 
                 break 
 
         # data is like {"critic": {"critic_reply": "..."}} etc.
         for node, state_key in fields.items():
             if node in chunk:
                 node_update = chunk[node]
                 if isinstance(node_update, dict) and state_key in node_update:
                     yield (node, state_key, node_update[state_key])