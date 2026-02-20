from .state_schema import State
from .llm_connector import chat
from .idea_gen import IdeationSubgraph
from langgraph.types import Command, interrupt
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver


class PlanningModule:
    """
    Multi-agent system wrapper:
      - builds the parent LangGraph
      - owns the ideation subgraph
      - exposes a streaming loop similar to your multiagent_chat_once()
    """
    def __init__(self,idea_generator_agent,facilitator_agent,idea_structurer_agent,subject_specialist_agent,
                 critic_agent, router_agent):
        
        # Agents
        self.idea_generator_agent = idea_generator_agent
        self.facilitator_agent = facilitator_agent
        self.idea_structurer_agent = idea_structurer_agent
        self.subject_specialist_agent = subject_specialist_agent
        self.critic_agent = critic_agent
        self.router_agent = router_agent

        # Ideation Subgraph
        self.ideation = IdeationSubgraph(
            router_agent,
            idea_generator_agent,
            subject_specialist_agent,
        )

        # Planning module graph (compiled)
        self._checkpointer = InMemorySaver()
        self.graph = self._build_graph().compile(checkpointer=self._checkpointer)


    # -----------------------------
    # Node functions
    # -----------------------------
    def facilitator_node(self, state: State):
        facilitator_input = (
    f"Student message:\n{state['user_message']}\n\n"
    f"Idea board:\n{state.get('idea_board', '')}\n\n"
    f"Outline:\n{state.get('structures', '')}\n\n"
    f"Subject expert notes:\n{state.get('subject_specialist_reply', '')}\n\n"
    f"Critic feedback:\n{state.get('critic_reply', '')}"
    )
        reply = chat(
            self.facilitator_agent,      
            facilitator_input,
            thread_id=state["thread_id"]
        )
        # End-of-turn: stop here and wait for resume
        user_reply = interrupt(reply)

        # When resumed, interrupt(...) returns the user's response
        return {"facilitator_reply": reply, "user_message": user_reply}
    

    # -----------------------------
    # Graph builder
    # -----------------------------
    def _build_graph(self) -> StateGraph:
        gb = StateGraph(State)

        gb.add_node("facilitator", self.facilitator_node)

        # ideation subgraph
        gb.add_node("brainstorm", self.ideation.graph)

        gb.add_edge(START, "facilitator")

        # After facilitator gets a student reply, run ideation, then come back and prompt again
        gb.add_edge("facilitator", "brainstorm")
        gb.add_edge("brainstorm", "facilitator")

        return gb
    
    # -----------------------------
    # Streaming runner (your multiagent_chat_once, but as a method)
    # -----------------------------
    def stream_updates(
        self,
        initial_state: State,
        thread_id: str,
    ):
        """
        Yields (node_name, state_key, value) updates.

        Handles interrupts by prompting on CLI and resuming with Command(resume=...).
        """

        fields = {
    "facilitator": "facilitator_reply",
    "router": "route",
    "idea_generation": "idea_generator_reply",
    "idea_expansion": "subject_specialist_reply",
    }
        initial_input =initial_state

        while True:
            for _, chunk in self.graph.stream(
                initial_input,
                config={"configurable": {"thread_id": thread_id}},
                subgraphs=True,
                stream_mode="updates",
            ):
                # Handle turn boundary
                if "__interrupt__" in chunk:
                    prompt = chunk["__interrupt__"][0].value
                    print("\n" + str(prompt))
                    user_response = input("User: ").strip()

                    # Resume from interrupt
                    initial_input = Command(resume=user_response)
                    break

                # Emit useful node updates
                for node, state_key in fields.items():
                    if node in chunk:
                        node_update = chunk[node]
                        if isinstance(node_update, dict) and state_key in node_update:
                            yield (node, state_key, node_update[state_key])