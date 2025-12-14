from .llm_connector import chat
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from .state_schema import State

def build_discussion_subgraph(idea_generator_agent, idea_structurer_agent, subject_specialist_agent, critic_agent) -> StateGraph[State]:
    graph_builder = StateGraph(State)
    def strucuture_node(state: State):
        print(state["idea_generator_reply"])
        reply = chat(
            idea_structurer_agent,      
            "Existing ideas: " + state["idea_board"] +  "\nNew ideas: " + state["idea_generator_reply"],
            thread_id=state["thread_id"],
        )
        
        return {"idea_board": reply}
    
    def idea_node(state: State):
        reply = chat(
            idea_generator_agent,      
            state["user_message"] + "\n" + "Critic feedback: " + state["critic_reply"],
            thread_id=state["thread_id"],
        )
        return {"idea_generator_reply": reply}
    
    def sub_specialist_node(state: State):
        reply = chat(
            subject_specialist_agent,      
            state["user_message"] + "\n" + "The ideas that are generated: " + state["idea_generator_reply"] + "\n" + "Critic feedback: " + state["critic_reply"],
            thread_id=state["thread_id"],
        )
        return {"subject_specialist_reply": reply}
    
    def critic_node(state: State):
        reply = chat(
            critic_agent,      
            "Ideas" + state["idea_board"] + "\n" + "Subject Specialist Ideas: " + state["subject_specialist_reply"],
            thread_id=state["thread_id"],
        )
        return {"critic_reply": reply}
    
    graph_builder.add_node("idea_generator", idea_node)
    graph_builder.add_node("idea_structurer", strucuture_node)
    graph_builder.add_node("subject_specialist", sub_specialist_node)
    graph_builder.add_node("critic", critic_node)
    graph_builder.add_edge(START, "idea_generator")
    graph_builder.add_edge("idea_generator", "subject_specialist")
    graph_builder.add_edge("subject_specialist", "critic")
    graph_builder.add_edge("critic", "idea_structurer")
    graph_builder.add_edge("idea_structurer", END)
    subgraph = graph_builder.compile(checkpointer=True)
    return subgraph