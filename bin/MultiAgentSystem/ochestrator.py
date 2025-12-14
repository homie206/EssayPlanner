from .state_schema import State
from .llm_connector import chat
from.brainstorm_graph import build_discussion_subgraph
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver



#def iterate_state(state: State) -> State:
#     return {
#        "iteration": state["iteration"] + 1,
#    } 

def build_mas_graph(idea_generator_agent, facilitator_agent, idea_structurer_agent, subject_specialist_agent) -> StateGraph[State]:
    graph_builder = StateGraph(State)
    brainstorm_graph = build_discussion_subgraph(idea_generator_agent, idea_structurer_agent, subject_specialist_agent)
    def facilitator_node(state: State):
        reply = chat(
            facilitator_agent,      
            state["user_message"],
            thread_id=state["thread_id"]
        )
        if state["facilitator_turn"] == 1:
          state["facilitator_turn"] = 2
          return {"facilitator_reply_1": reply}
        else:
          state["facilitator_turn"] = 1
          return {"facilitator_reply_2": reply}
              
    graph_builder.add_node("brainstorm", brainstorm_graph)
    graph_builder.add_node("facilitator", facilitator_node)
    #graph_builder.add_node("iterate", iterate_state)
    graph_builder.add_edge(START, "facilitator")
    graph_builder.add_edge("facilitator", "brainstorm")
    #graph_builder.add_edge("brainstorm", "facilitator")
    #graph_builder.add_edge("facilitator", "iterate")
    #graph_builder.add_edge("iterate", END)
    graph_builder.add_edge("brainstorm", END)

    checkpointer = InMemorySaver()
    mas = graph_builder.compile(checkpointer=checkpointer)
    return mas

def multiagent_chat_once(mas, initial_state: State, thread_id: str) -> str:
    final_state = mas.invoke(initial_state, config={"configurable": {"thread_id": thread_id}},)
    return final_state