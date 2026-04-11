from __future__ import annotations
from langgraph.types import interrupt
from langgraph.graph import START, END, StateGraph
from .llm_connector import chat
from .state_schema import State


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
            "Here is your structured essay plan is ready to be downloaded:\n\n"
            "You can now use this to start writing your essay."
        )

        return {
            "final_message": message,
            "final_file_name": f"essay_plan_{essay_topic}.txt",
            "final_file_mime_type": "text",
            "final_document": idea_board,
        }


    def _ask_stop(self, state: State):
        stop_statement = "We've done a few rounds of structuring now. "
        if state["structuring_iteration"] > 5:
            stop_statement = "We've done several more rounds of structuring."

        interrupt(
            stop_statement
            + "\n\n[YES_NO] Are you happy with your final idea board?"
        )

        return {}
    
    def _decide_stop(self, state: State):

        last = state.get("latest_user_message", "").strip().lower()
        yes = last in {"y", "yes", "yeah", "yep", "sure", "ok", "okay", "go", "move on"}

        return {"structuring_done": yes}
    
    def _after_structurer(self, state: State):
        iteration = state.get("structuring_iteration", 0)

        # First: stop condition
        if iteration >= 5:
            return "stop"

        # Then: intro vs normal
        if iteration <= 1:
            return "intro"

        return "normal"


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
        g.add_node("decide_stop", self._decide_stop)
        g.add_node("final_output", self._final_output_node)

        g.add_edge(START, "facilitator")

        g.add_edge("facilitator", "user1")
        g.add_edge("user1", "iterator")
        g.add_edge("iterator", "idea_structurer")

        g.add_conditional_edges(
            "idea_structurer",
            self._after_structurer,
            {
                "intro": "facilitator",
                "normal": "router",
                "stop": "ask_stop",
            },
        )

        g.add_edge("ask_stop", "user1")
        g.add_edge("user1", "decide_stop")

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

        g.add_edge("user2", "facilitator")

        g.add_conditional_edges(
            "decide_stop",
            lambda s: s["structuring_done"],
            {
                True: "final_output",
                False: "facilitator",
            },
        )

        g.add_edge("final_output", END)

        return g
