from .state_schema import State
from .llm_connector import chat
from .idea_gen import IdeationSubgraph
from langgraph.types import Command, interrupt
from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from .structuring_phase import StructuringSubgraph

class PlanningModule:
    """
    Multi-agent system wrapper:
      - builds the parent LangGraph
      - owns the ideation subgraph
      - exposes a streaming loop similar to your multiagent_chat_once()
    """
    def __init__(self,idea_generator_agent,facilitator_agent,idea_structurer_agent,subject_specialist_agent,
                 critic_agent, router_agent, structure_coach_agent, argument_flow_agent):
        
        # Agents
        self.idea_generator_agent = idea_generator_agent
        self.facilitator_agent = facilitator_agent
        self.idea_structurer_agent = idea_structurer_agent
        self.subject_specialist_agent = subject_specialist_agent
        self.critic_agent = critic_agent
        self.router_agent = router_agent

        # Ideation Subgraph
        self.ideation = IdeationSubgraph(
            facilitator_agent,
            router_agent,
            idea_generator_agent,
            subject_specialist_agent,
            idea_structurer_agent
        )

        # Structuring Subgraph
        self.structuring = StructuringSubgraph(
            facilitator_agent,
            structure_coach_agent,
            idea_structurer_agent,
            argument_flow_agent,
        )

        # Planning module graph (compiled)
        self._checkpointer = InMemorySaver()
        self.graph = self._build_graph().compile(checkpointer=self._checkpointer)



    # -----------------------------
    # Node functions
    # -----------------------------
    

    # -----------------------------
    # Graph builder
    # -----------------------------
    def _build_graph(self) -> StateGraph:
        gb = StateGraph(State)

        gb.add_node("ideation", self.ideation.graph)
        gb.add_node("structuring", self.structuring.graph)

        gb.add_edge(START, "ideation")
        gb.add_edge("ideation", "structuring")
        gb.add_edge("structuring", END)

        return gb
    
    # -----------------------------
    # Streaming runner with interrupt handling
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
                    yield ("__interrupt__", "prompt", str(prompt))
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
    
    def show_graph(self):
     # Mermaid diagram
     mermaid = self.graph.get_graph().draw_mermaid()
     with open("planning_graph.md", "w") as f:
         f.write(mermaid)


# =========================
# UI ENTRY POINT
# =========================

def build_mas_graph(subject: str):
    """
    Required by RichUI.
    Builds and returns the compiled MAS graph.
    """
    from .agents import create_all_agents
    from .state_schema import State

    state = State(subject=subject)

    (
        facilitator,
        idea_generator,
        subject_specialist,
        idea_structurer,
        critic,
        router,
        structure_coach,
        argument_flow,
    ) = create_all_agents(state)

    planning = PlanningModule(
        idea_generator,
        facilitator,
        idea_structurer,
        subject_specialist,
        critic,
        router,
        structure_coach,
        argument_flow,
    )

    return planning.graph

# =========================
# UI COMPATIBILITY WRAPPER
# =========================

def multiagent_chat_once(
    mas_graph,
    state,
    thread_id: str,
):
    """
    Adapter for RichUI.

    Takes:
      - compiled MAS graph
      - shared UI state dict
      - thread_id

    Yields:
      (agent_name, state_key, reply)
    """

    from langgraph.types import Command

    # Stream updates from the graph
    stream = mas_graph.stream(
        state,
        config={"configurable": {"thread_id": thread_id}},
        subgraphs=True,
        stream_mode="updates",
    )

    for _, chunk in stream:
        # Handle interrupts (pause for user input)
        if "__interrupt__" in chunk:
            prompt = chunk["__interrupt__"][0].value
            user_input = yield ("facilitator", "facilitator_reply", str(prompt))
            state = Command(resume=user_input)
            continue

        # Emit agent outputs in a UI-friendly way
        for node, update in chunk.items():
            if not isinstance(update, dict):
                continue

            for key, value in update.items():
                yield (node, key, value)