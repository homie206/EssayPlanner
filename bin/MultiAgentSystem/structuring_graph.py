from __future__ import annotations
from langgraph.types import interrupt
from langgraph.graph import START, END, StateGraph
from .llm_connector import chat
from .state_schema import State


class StructuringSubgraph:

    def __init__(self, structuring_coach_agent, argument_flow_agent):
        self.structuring_coach_agent = structuring_coach_agent
        self.argument_flow_agent = argument_flow_agent

        self.graph = self._build().compile(checkpointer=True)


    # -------------------------
    # Nodes
    # -------------------------

    def _coach_node(self, state: State):

        reply = chat(
            self.structuring_coach_agent,
            "Idea board:\n" + state["idea_board"],
            thread_id=state["thread_id"],
        )

        return {"structuring_coach_reply": reply}


    def _user_node(self, state: State):

        user_reply = interrupt("How would you like to organise these ideas into an essay structure?")

        messages = state.get("turn_user_messages", [])
        messages.append(user_reply)

        return {"latest_user_message": user_reply, "turn_user_messages": messages}


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


    def _iteration_node(self, state: State):

        iteration = state["structuring_iteration"] + 1

        return {"structuring_iteration": iteration}


    def stop_condition(self, state: State):

        ans = interrupt(
            "Here is the current structure:\n"
            + "\n".join(state["structures"])
            + "\n\nAre you happy with this structure? (y/n)"
        )

        a = str(ans).strip().lower()

        yes = a in {"y", "yes", "yeah", "yep", "ok", "sure"}

        if yes:
            return {"structuring_done": True}


    # -------------------------
    # Graph Builder
    # -------------------------

    def _build(self):

        g = StateGraph(State)

        g.add_node("coach", self._coach_node)
        g.add_node("user", self._user_node)
        g.add_node("argument_flow", self._argument_flow_node)
        g.add_node("iterator", self._iteration_node)
        g.add_node("stop_condition", self.stop_condition)

        g.add_edge(START, "coach")
        g.add_edge("coach", "user")
        g.add_edge("user", "argument_flow")
        g.add_edge("argument_flow", "iterator")

        g.add_conditional_edges(
            "iterator",
            lambda s: "stop?" if s["structuring_iteration"] >= 3 else "continue",
            {
                "stop?": "stop_condition",
                "continue": "coach",
            },
        )

        g.add_conditional_edges(
            "stop_condition",
            lambda s: s["structuring_done"],
            {
                True: END,
                False: "coach",
            },
        )

        return g