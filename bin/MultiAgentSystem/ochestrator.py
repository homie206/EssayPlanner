from typing import List
from .llm_connector import  chat
from .prompts import build_prompt_for_agent
from typing_extensions import TypedDict
from langgraph.graph import START, END, StateGraph

class State(TypedDict):
    ideas: List[str]
    structures: List[str]
    subject: str
    user_message: str # latest student message
    facilitator_reply : str

def run_facilitator(state: State) -> str:
    prompt = build_prompt_for_agent("Facilitator", state["subject"])
    reply_text = chat(prompt, state["user_message"])
    return {
        "facilitator_reply": reply_text,
    }

def build_mas_graph() -> StateGraph[State]:
    graph_builder = StateGraph(State)
    graph_builder.add_node("facilitator", run_facilitator)

    graph_builder.add_edge(START, "facilitator")
    graph_builder.add_edge("facilitator", END)
    mas = graph_builder.compile()
    return mas

def multiagent_chat_once(subject: str, user_message: str) -> str:
    mas = build_mas_graph()
    initial_state: State = {
        "ideas": [],
        "structures": [],
        "subject": subject,
        "user_message": user_message,
        "facilitator_reply": "",
    }
    final_state = mas.invoke(initial_state)
    return final_state["facilitator_reply"]