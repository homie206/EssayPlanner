from __future__ import annotations
from langgraph.types import interrupt
from langgraph.graph import START, END, StateGraph
from .llm_connector import chat
from .state_schema import State


class IdeationSubgraph:
    """
    Holds a compiled ideation subgraph and the agents it needs.
    """
    def __init__(self, router_agent, idea_generator_agent, subject_specialist_agent):
        self.router_agent = router_agent
        self.idea_generator_agent = idea_generator_agent
        self.subject_specialist_agent = subject_specialist_agent

        self.graph = self._build().compile() 
        
    # ---- nodes ----
    def _routing_node(self, state: State) -> dict:
        reply = chat(
            self.router_agent,
            "Student message:\n"
            + state["user_message"]
            + "\n\nIdea board:\n"
            + state.get("idea_board", ""),
            thread_id=state["thread_id"],
        )

        route = str(reply).strip().strip('"')
        if route not in ("idea_generation", "idea_expansion"):
            route = "None" #Skipping ideation if router gives invalid output.

        return {"route": route}

    def _idea_generation_node(self, state: State) -> dict:
        reply = chat(
            self.idea_generator_agent,
            state["user_message"] + "\nExisting ideas: " + state.get("idea_board", ""),
            thread_id=state["thread_id"],
        )
        # End-of-turn: stop here and wait for resume
        user_reply = interrupt(reply)
        return {"idea_generator_reply": reply, "user_message": user_reply}

    def _idea_expansion_node(self, state: State) -> dict:
        reply = chat(
            self.subject_specialist_agent,
            state["user_message"] + "\nExisting ideas: " + state.get("idea_board", ""),
            thread_id=state["thread_id"],
        )
        # End-of-turn: stop here and wait for resume
        user_reply = interrupt(reply)
        return {"subject_specialist_reply": reply, "user_message": user_reply}

    # ---- graph build ----
    def _build(self) -> StateGraph:
        g = StateGraph(State)

        g.add_node("router", self._routing_node)
        g.add_node("idea_generation", self._idea_generation_node)
        g.add_node("idea_expansion", self._idea_expansion_node)

        g.add_edge(START, "router")

        g.add_conditional_edges(
            "router",
            lambda s: s["route"],
            {
                "idea_generation": "idea_generation",
                "idea_expansion": "idea_expansion",
                "None": END,
            },
        )

        g.add_edge("idea_generation", END)
        g.add_edge("idea_expansion", END)

        return g