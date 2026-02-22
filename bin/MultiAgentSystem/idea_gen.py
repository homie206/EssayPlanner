from __future__ import annotations
from langgraph.types import interrupt
from langgraph.graph import START, END, StateGraph
from .llm_connector import chat
from .state_schema import State


class IdeationSubgraph:
    """
    Holds a compiled ideation subgraph and the agents it needs.
    """
    def __init__(self, facilitator_agent, router_agent, idea_generator_agent, subject_specialist_agent, idea_structurer_agent):
        self.facilitator_agent = facilitator_agent
        self.router_agent = router_agent
        self.idea_generator_agent = idea_generator_agent
        self.subject_specialist_agent = subject_specialist_agent
        self.idea_structurer_agent = idea_structurer_agent
        self.graph = self._build().compile(checkpointer=True) 
        
    # ---- nodes ----
    def facilitator_node(self, state: State):
        facilitator_input = (
    f"Student message:\n{state['latest_user_message']}\n\n"
    f"Idea board:\n{state.get('idea_board', '')}\n\n"
    f"Outline:\n{state.get('structures', '')}\n\n"
    f"Subject expert reply:\n{state.get('subject_specialist_reply', '')}\n\n"
    f"Idea generator reply:\n{state.get('idea_generator_reply', '')}"
    )
        reply = chat(
            self.facilitator_agent,      
            facilitator_input,
            thread_id=state["thread_id"]
        )
        # End-of-turn: stop here and wait for resume
        user_reply = interrupt("Facilitator: " + reply)

        messages = state.get("turn_user_messages", [])
        messages.append(user_reply)

        # When resumed, interrupt(...) returns the user's response
        return {"facilitator_reply": reply, "latest_user_message": user_reply, "turn_user_messages": messages}
    def _routing_node(self, state: State) -> dict:
        reply = chat(
            self.router_agent,
            "Student message:\n"
            + state["latest_user_message"]
            + "\n\nIdea board:\n"
            + state.get("idea_board", ""),
            thread_id=state["thread_id"],
        )

        route = str(reply).strip().strip('"')
        if route not in ("idea_generation", "idea_expansion"):
            route = "none" #Skipping ideation if router gives invalid output.
        
        print(f"Router chose route: {route}")

        return {"route": route}

    def _idea_generation_node(self, state: State) -> dict:
        reply = chat(
            self.idea_generator_agent,
            state["latest_user_message"] + "\nEssay topic: " + state["essay_topic"] + "\nExisting ideas: " + state["idea_board"],
            thread_id=state["thread_id"],
        )
        # End-of-turn: stop here and wait for resume
        user_reply = interrupt("Idea generator: " + reply)
        messages = state.get("turn_user_messages", [])
        messages.append(user_reply)
        return {"idea_generator_reply": reply, "latest_user_message": user_reply, "turn_user_messages": messages}

    def _idea_expansion_node(self, state: State) -> dict:
        reply = chat(
            self.subject_specialist_agent,
            state["latest_user_message"] + "\nEssay topic: " + state["essay_topic"] + "\nExisting ideas: " + state["idea_board"],
            thread_id=state["thread_id"],
        )
        # End-of-turn: stop here and wait for resume
        user_reply = interrupt("Subject specialist: " + reply)
        
        # Append the user's response to the list of messages in this turn
        messages = state.get("turn_user_messages", [])
        messages.append(user_reply)

        return {"subject_specialist_reply": reply, "latest_user_message": user_reply, "turn_user_messages": messages}
    
    def cleanup_messages(self, state: State):
        # Clear the turn_user_messages list after each turn to avoid it growing indefinitely
        return {"turn_user_messages": []}
    
    def _structure_node(self, state: State):
        print(state["idea_generator_reply"])
        reply = chat(
            self.idea_structurer_agent,      
            "Existing ideas: " + state["idea_board"] +  "\nStudent's  messages: " + "\n".join(state["turn_user_messages"]),
            thread_id=state["thread_id"],
        )
        print("Structurer reply:", reply)
        return {"idea_board": reply}
    
    def iterater(self, state: State):
        iteration = state["iteration"] + 1
        print(f"--- Starting iteration {iteration} ---")
        return {"iteration": iteration}
    
    # ---- graph build ----
    def _build(self) -> StateGraph:
        g = StateGraph(State)
        g.add_node("iterater", self.iterater)
        g.add_node("facilitator", self.facilitator_node)
        g.add_node("router", self._routing_node)
        g.add_node("idea_generation", self._idea_generation_node)
        g.add_node("idea_expansion", self._idea_expansion_node)
        g.add_node("structure", self._structure_node)
        g.add_node("cleanup", self.cleanup_messages)
        
        g.add_edge(START, "facilitator")
        g.add_edge("facilitator", "iterater")
        g.add_conditional_edges(
            "iterater",
            lambda s: "intro_node" if s["iteration"] in [1, 2] else "normal_node",
            {
                "intro_node": "facilitator",  # Loop back to facilitator for the first turn to get the initial student ideas before further ideation
                "normal_node": "router", # After the first turn, route to either idea generation or expansion based on the router's decision
            },
        )
        g.add_conditional_edges(
            "router",
            lambda s: s["route"],
            {
                "idea_generation": "idea_generation",
                "idea_expansion": "idea_expansion",
                "none": "structure",
            },
        )
       # g.add_edge("idea_generation", "cleanup")
       # g.add_edge("idea_expansion", "cleanup")
        g.add_edge("idea_generation", "structure")
        g.add_edge("idea_expansion", "structure")
        g.add_edge("structure", "cleanup")
        g.add_edge("cleanup", "facilitator")


        return g
    