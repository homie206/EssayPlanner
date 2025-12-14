from .state_schema import State
from .llm_connector import chat
from.brainstorm_graph import build_discussion_subgraph
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver

#def iterate_state(state: State) -> State:
#     return {
#        "iteration": state["iteration"] + 1,
#    } 

def build_mas_graph(idea_generator_agent, facilitator_agent, idea_structurer_agent, subject_specialist_agent, critic_agent) -> StateGraph[State]:
    graph_builder = StateGraph(State)
    brainstorm_graph = build_discussion_subgraph(idea_generator_agent, idea_structurer_agent, subject_specialist_agent, critic_agent)
    def facilitator_node(state: State):
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
        return {"facilitator_reply": reply}
              
    graph_builder.add_node("brainstorm", brainstorm_graph)
    graph_builder.add_node("facilitator", facilitator_node)
    #graph_builder.add_node("iterate", iterate_state)
    graph_builder.add_edge(START, "brainstorm")
    graph_builder.add_edge("brainstorm", "facilitator")
    #graph_builder.add_edge("brainstorm", "facilitator")
    #graph_builder.add_edge("facilitator", "iterate")
    #graph_builder.add_edge("iterate", END)
    graph_builder.add_edge("facilitator", END)

    checkpointer = InMemorySaver()
    mas = graph_builder.compile(checkpointer=checkpointer)
    return mas

def multiagent_chat_once(mas, initial_state: State, thread_id: str) -> str:
    final_state = mas.invoke(initial_state, config={"configurable": {"thread_id": thread_id}},)
    return final_state