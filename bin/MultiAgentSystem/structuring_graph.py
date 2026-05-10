from __future__ import annotations
from langgraph.types import interrupt
from langgraph.graph import START, END, StateGraph
from .llm_connector import chat
from .state_schema import State
from pathlib import Path



class StructuringSubgraph:

    def __init__(self, facilitator_agent, structuring_coach_agent, argument_flow_agent, router_agent, structuring_idea_structurer_agent):
        self.facilitator_agent = facilitator_agent
        self.structuring_coach_agent = structuring_coach_agent
        self.argument_flow_agent = argument_flow_agent
        self.router_agent = router_agent
        self.idea_structurer_agent = structuring_idea_structurer_agent

        self.graph = self._build().compile(checkpointer=True)


    # -------------------------
    # Nodes
    # -------------------------

    def _facilitator_node(self, state: State):

        facilitator_input = (
            f"Idea board:\n{state.get('idea_board', '')}\n\n"
            f"Student's last message:\n{state.get('latest_user_message', '')}\n\n"
            f"Structuring coach's last suggestion:\n{state.get('structuring_coach_reply', '')}\n\n"
            f"Argument flow proposal:\n{state.get('argument_flow_reply', '')}"
        )

        reply = chat(
            self.facilitator_agent,
            facilitator_input,
            thread_id=state["thread_id"],
        )

        return {"facilitator_reply": reply}


    def _user_node(self, state: State):

        user_reply = interrupt("Your turn:")

        messages = state.get("turn_user_messages", [])
        messages.append(user_reply)

        return {"latest_user_message": user_reply, "turn_user_messages": messages}


    def _coach_node(self, state: State):

        coach_input = (
            f"Idea board:\n{state.get('idea_board', '')}\n\n"
            f"Student's thoughts:\n{state.get('latest_user_message', '')}"
        )

        reply = chat(
            self.structuring_coach_agent,
            coach_input,
            thread_id=state["thread_id"],
        )

        return {"structuring_coach_reply": reply}


    def _argument_flow_node(self, state: State):

        reply = chat(
            self.argument_flow_agent,
            "Idea board:\n"
            + state["idea_board"]
            + "\nStudent thoughts:\n"
            + "\n".join(state["turn_user_messages"]),
            thread_id=state["thread_id"],
        )

        return {"argument_flow_reply": reply}
    
    def _router_node(self, state: State):

        reply = chat(
            self.router_agent,
            "Student message:\n"
            + state["latest_user_message"]
            + "\n\nIdea board:\n"
            + state.get("idea_board", ""),
            thread_id=state["thread_id"],
        )

        route = str(reply).strip().lower()

        if route not in ("structuring", "flow"):
            route = "none"

        print(f"Router chose route: {route}")

        return {"route": route}

    def _idea_structurer_node(self, state: State):

        reply = chat(
            self.idea_structurer_agent,
            "Existing ideas: "
            + state["idea_board"]
            + "\nStudent messages:\n"
            + "\n".join(state.get("turn_user_messages", [])),
            thread_id=state["thread_id"],
        )

        return {"idea_board": reply}

    def _iteration_node(self, state: State):

        iteration = state["structuring_iteration"] + 1

        return {"structuring_iteration": iteration}
    
    def _final_output_node(self, state: State):

        idea_board = state.get("idea_board", "").strip()
        essay_topic = state.get("essay_topic", "").strip()
        message = (
            "Great — your essay plan is now complete.\n\n"
            "Your structured essay plan is ready to be downloaded:\n\n"
            "Use it to start writing your essay."
        )

        return {
            "final_message": message,
            "final_file_name": f"essay_plan_{essay_topic}.txt",
            "final_file_mime_type": "text",
            "final_document": idea_board,
        }


    def _ask_stop(self, state: State):
        idea_board = state.get("idea_board", "")
        stop_statement = "We've done a few rounds of structuring now. "
        if state["structuring_iteration"] > 5:
            stop_statement = "We've done several more rounds of structuring."

        ans = interrupt(
            stop_statement
            + 
            "Here is your idea board:\n\n"
            f"{idea_board}\n\n"
            "\n\n[YES_NO] Are you happy with your final idea board?"
        )

        a = str(ans).strip().lower()

        yes = a in {"y", "yes", "yeah", "yep", "sure", "ok", "okay", "go", "move on", "continue"}

        if yes:
            return {"structuring_done": True}
        
    def check_move_on(self, state: State):
        messages = state.get("turn_user_messages", [])
        stop_statement = "The brainstorming session will finish now."
        idea_board = state.get("idea_board", "")
        if not messages:
            return {"structuring_done": False}
    
        latest_message = str(messages[-1]).lower().strip()
    
        move_words = {"skip", "finish", "ready to write", "stop", "I think I am ready to start", "I had enough"}
        target_words = {"structuring phase", "structuring", "structure", "brainstorming", " the essay", "writing"}
    
        wants_move = any(word in latest_message for word in move_words)
        wants_target = any(word in latest_message for word in target_words)
    
        if not (wants_move and wants_target):
            return {"structuring_done": False}
        
        ans = interrupt(
            stop_statement
            + 
            "Here is your idea board:\n\n"
            f"{idea_board}\n\n"
            "\n\n[YES_NO] Are you happy with your final idea board?"
        )

        confirmed = str(ans).strip().lower() in {
            "y", "yes", "yeah", "yep", "sure", "ok", "okay", "go", "continue"
        }
    
        return {"structuring_done": confirmed}
    
    def _after_structurer(self, state: State):
        iteration = state.get("structuring_iteration", 0)

        # First: stop condition
        if iteration >= 4 and iteration % 4 == 0:
            return "stop"

        # Then: intro vs normal
        if iteration <= 1:
            return "intro"

        return "normal"
    
    def save_mermaid_png(self, output_file_path: str = "ideation_subgraph.png") -> str:
        """
        Render the graph as a PNG using Mermaid drawing and save it.
        Returns the saved path.
        """
        path = Path(output_file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # draw_mermaid_png returns bytes; passing output_file_path also saves the file.
        img_bytes = self.graph.get_graph().draw_mermaid_png(output_file_path=str(path))
        if img_bytes and not path.exists():
            # Fallback: write bytes ourselves if your version doesn't auto-save
            path.write_bytes(img_bytes)
        
        return str(path)

    # -------------------------
    # Graph Builder
    # -------------------------

    def _build(self):

        g = StateGraph(State)

        # Nodes
        g.add_node("facilitator", self._facilitator_node)
        g.add_node("user1", self._user_node)
        g.add_node("user2", self._user_node)
        g.add_node("router", self._router_node)
        g.add_node("coach", self._coach_node)
        g.add_node("argument_flow", self._argument_flow_node)
        g.add_node("idea_structurer", self._idea_structurer_node)
        g.add_node("iterator", self._iteration_node)
        g.add_node("ask_stop", self._ask_stop)
        g.add_node("final_output", self._final_output_node)
        g.add_node("move_on", self.check_move_on)
        g.add_node("move_on_2", self.check_move_on)

        g.add_edge(START, "facilitator")

        g.add_edge("facilitator", "user1")
        g.add_edge("user1", "move_on")
        
        #check for manual exit
        g.add_conditional_edges(
            "move_on",
            lambda s: s["structuring_done"],
            {
                True: "final_output",
                False: "iterator",   
            })

        g.add_conditional_edges(
            "iterator",
            self._after_structurer,
            {
                "intro": "facilitator",
                "normal": "router",
                "stop": "ask_stop",
            },
        )

        
        # Router decides agent
        g.add_conditional_edges(
            "router",
            lambda s: s["route"],
            {
                "structuring": "coach",
                "flow": "argument_flow",
                "none": "coach", # Default to coach if router doesn't choose a valid route
            },
        )
      
        g.add_edge("coach", "user2")
        g.add_edge("argument_flow", "user2")
        g.add_edge("user2", "move_on_2")
        
        #check for manual exit
        g.add_conditional_edges(
            "move_on_2",
            lambda s: s["structuring_done"],
            {
                True: "final_output",
                False: "idea_structurer",   
            })
        
        g.add_edge("idea_structurer", "facilitator")

        g.add_conditional_edges(
            "ask_stop",
            lambda s: s["structuring_done"],
            {
                True: "final_output",
                False: "facilitator",
            },
        )

        g.add_edge("final_output", END)

        return g
