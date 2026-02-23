from langgraph.graph import START, StateGraph
from langgraph.types import interrupt
from .llm_connector import chat
from .state_schema import State


class StructuringSubgraph:
    def __init__(
        self,
        facilitator_agent,
        structure_coach_agent,
        internal_structurer_agent,
        argument_flow_agent,
    ):
        self.facilitator_agent = facilitator_agent
        self.structure_coach_agent = structure_coach_agent
        self.internal_structurer_agent = internal_structurer_agent
        self.argument_flow_agent = argument_flow_agent

        self.graph = self._build().compile(checkpointer=True)


    def structure_coach_node(self, state: State):
        reply = chat(
            self.structure_coach_agent,
            "IDEA BOARD:\n"
            + state["idea_board"]
            + "\n\nStudent message:\n"
            + state["latest_user_message"],
            thread_id=state["thread_id"],
        )

        user_reply = interrupt("Structure Coach: " + reply)

        msgs = state.get("turn_user_messages", [])
        msgs.append(user_reply)

        return {
            "latest_user_message": user_reply,
            "turn_user_messages": msgs,
        }

    def internal_structurer_node(self, state: State):
        reply = chat(
            self.internal_structurer_agent,
            "IDEA BOARD:\n"
            + state["idea_board"]
            + "\n\nSTRUCTURAL DECISIONS FROM STUDENT:\n"
            + "\n".join(state["turn_user_messages"]),
            thread_id=state["thread_id"],
        )

        return {"structures": reply}

    def argument_flow_node(self, state: State):
        reply = chat(
            self.argument_flow_agent,
            "CURRENT STRUCTURE:\n"
            + str(state["structures"])
            + "\n\nIDEA BOARD:\n"
            + state["idea_board"],
            thread_id=state["thread_id"],
        )

        return {"structures": reply}

    def cleanup_node(self, state: State):
        return {"turn_user_messages": []}


    def _build(self) -> StateGraph:
        g = StateGraph(State)

        g.add_node("structure_coach", self.structure_coach_node)
        g.add_node("internal_structurer", self.internal_structurer_node)
        g.add_node("argument_flow", self.argument_flow_node)
        g.add_node("cleanup", self.cleanup_node)

        g.add_edge(START, "structure_coach")
        g.add_edge("structure_coach", "internal_structurer")
        g.add_edge("internal_structurer", "argument_flow")
        g.add_edge("argument_flow", "cleanup")
        g.add_edge("cleanup", "structure_coach")

        return g