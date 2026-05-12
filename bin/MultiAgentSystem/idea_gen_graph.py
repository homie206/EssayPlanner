from __future__ import annotations
from langgraph.types import interrupt
from langgraph.graph import START, END, StateGraph
from .llm_connector import chat
from .state_schema import State
from pathlib import Path
from langchain_core.runnables.graph import MermaidDrawMethod

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
    def _facilitator_node(self, state: State):
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
        return {"facilitator_reply": reply}
    
    def _user_turn_node_1(self, state: State):
        user_reply = interrupt("Your turn:")
        messages = state.get("turn_user_messages", [])

        #append only first message as all the other replies in this node 
        #arent content related
        if state["ideation_iteration"] == 1:
          messages.append(user_reply)
        
        print(messages)
        return {"latest_user_message": user_reply, "turn_user_messages": messages}
    
    def _user_turn_node_2(self, state: State):
        user_reply = interrupt("Your turn:")
        messages = state.get("turn_user_messages", [])
        messages.append(user_reply)
        return {"latest_user_message": user_reply, "turn_user_messages": messages}
    
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
    
        return {"idea_generator_reply": reply}

    def _idea_expansion_node(self, state: State) -> dict:
        reply = chat(
            self.subject_specialist_agent,
            state["latest_user_message"] + "\nEssay topic: " + state["essay_topic"] + "\nExisting ideas: " + state["idea_board"],
            thread_id=state["thread_id"],
        )
        return {"subject_specialist_reply": reply}
    
    def _cleanup_messages(self, state: State):
        # Clear the turn_user_messages list after each turn to avoid it growing indefinitely
        return {"turn_user_messages": []}
    
    def _structure_node(self, state: State):
        reply = chat(
            self.idea_structurer_agent,      
            "Existing ideas: " + state["idea_board"] +  "\nStudent's  messages: " + "\n".join(state["turn_user_messages"]),
            thread_id=state["thread_id"],
        )
        #print("Structurer reply:", reply)
        return {"idea_board": reply}
    
    def _iterater(self, state: State):
        iteration = state["ideation_iteration"] + 1
        print(f"--- Starting iteration {iteration} ---")
        return {"ideation_iteration": iteration}
    
    def check_move_on(self, state: State):
        messages = state.get("turn_user_messages", [])
        if not messages:
            return {"facilitation_done": False}
    
        latest_message = str(messages[-1]).lower().strip()
    
        move_words = {"move on", "go", "skip", "proceed", "continue", "move"}
        target_words = {"critic phase", "criticising", "criticise", "next phase", "next"}
    
        wants_move = any(word in latest_message for word in move_words)
        wants_target = any(word in latest_message for word in target_words)
    
        if not (wants_move and wants_target):
            return {"facilitation_done": False}
    
        ans = interrupt("[YES_NO] Are you sure you want to move on to the critic phase?")
        confirmed = str(ans).strip().lower() in {
            "y", "yes", "yeah", "yep", "sure", "ok", "okay", "go", "continue"
        }
    
        return {"facilitation_done": confirmed}

    def stop_condition(self, state: State) -> bool:
        stop_statement = "We've done a few rounds of ideation. "
        if state["ideation_iteration"] > 5 :
            stop_statement = "We've done several more rounds of ideation."
        ans = interrupt(
         stop_statement + "\n\n[YES_NO] Here is the idea board so far:\n\n" + state["idea_board"] + "\n\nAre you happy to move on to the critic phase?")
        a = str(ans).strip().lower()

        yes = a in {"y", "yes", "yeah", "yep", "sure", "ok", "okay", "go", "move on", "continue"}
        #no = a in {"n", "no", "nope", "not yet", "later", "keep going", "continue ideation"}
    
        if yes:
            return {"facilitation_done": True}
    
    def save_mermaid_png(self, output_file_path: str = "ideation_subgraph.png") -> str:
        """
        Render the graph as a PNG using Mermaid drawing and save it.
        Returns the saved path.
        """
        path = Path(output_file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # draw_mermaid_png returns bytes; passing output_file_path also saves the file.
        img_bytes = self.graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.PYPPETEER, output_file_path=str(path))
        if img_bytes and not path.exists():
            # Fallback: write bytes ourselves if your version doesn't auto-save
            path.write_bytes(img_bytes)

        return str(path)
    
    # ---- graph build ----
    def _build(self) -> StateGraph:
        g = StateGraph(State)

        #nodes
        g.add_node("user_reply_1", self._user_turn_node_1)
        g.add_node("user_reply_2", self._user_turn_node_2)
        g.add_node("iterater", self._iterater)
        g.add_node("facilitator", self._facilitator_node)
        g.add_node("router", self._routing_node)
        g.add_node("idea_generation", self._idea_generation_node)
        g.add_node("idea_expansion", self._idea_expansion_node)
        g.add_node("structure_1", self._structure_node)
        g.add_node("structure_2", self._structure_node)
        g.add_node("cleanup_1", self._cleanup_messages)
        g.add_node("cleanup_2", self._cleanup_messages)
        g.add_node("stop_condition", self.stop_condition)
        g.add_node("move_on", self.check_move_on)
        g.add_node("move_on_2", self.check_move_on)
        
        #edges
        g.add_edge(START, "facilitator")
        g.add_edge("facilitator", "user_reply_1")
        g.add_edge("user_reply_1", "move_on")

        #check for manual stop condition
        g.add_conditional_edges(
            "move_on",
            lambda s: s["facilitation_done"],
            {
                True: END,
                False: "iterater",   
            })
        
        g.add_conditional_edges(
            "iterater",
            lambda s: "intro_node" if s["ideation_iteration"] in [1, 2] else "normal_node",
            {
                "intro_node": "structure_1",  
                "normal_node": "router"
            },
        )
        g.add_edge("structure_1", "cleanup_1")
        g.add_edge("cleanup_1", "facilitator")
        g.add_conditional_edges(
            "router",
            lambda s: s["route"],
            {
                "idea_generation": "idea_generation",
                "idea_expansion": "idea_expansion",
                "none": "structure_2",
            },
        )
        g.add_edge("idea_generation", "user_reply_2")
        g.add_edge("idea_expansion", "user_reply_2")
        g.add_edge("user_reply_2", "move_on_2")

        #check for manual stop condition
        g.add_conditional_edges(
            "move_on_2",
            lambda s: s["facilitation_done"],
            {
                True: END,
                False: "structure_2",   
            })
        
        g.add_edge("structure_2", "cleanup_2")
        g.add_conditional_edges(
            "cleanup_2",
            lambda s: "stop?" if (s["ideation_iteration"] >= 4 and s["ideation_iteration"] % 4 == 0) else "continue",
            {
                "stop?": "stop_condition",
                "continue": "facilitator",
            },
        )
        g.add_conditional_edges(
            "stop_condition",
            lambda s: s["facilitation_done"],
            {
                True: END,
                False: "facilitator",   
            })
        return g
    