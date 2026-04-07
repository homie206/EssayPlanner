from .state_schema import State
from .llm_connector import chat
from .idea_gen_graph import IdeationSubgraph
from .critic_graph import CriticSubgraph
from .structuring_graph import StructuringSubgraph
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
    def __init__(self,idea_generator_agent,facilitator_agent_ideation,idea_structurer_agent,subject_specialist_agent,
                 critic_agent, router_agent, facilitator_agent_critic, structuring_coach_agent, argument_flow_agent,
                 facilitator_agent_structuring, structuring_router_agent, structuring_idea_structurer_agent):

        # Agents
        self.idea_generator_agent = idea_generator_agent
        self.facilitator_agent_ideation = facilitator_agent_ideation
        self.idea_structurer_agent = idea_structurer_agent
        self.subject_specialist_agent = subject_specialist_agent
        self.critic_agent = critic_agent
        self.router_agent = router_agent
        self.facilitator_agent_critic = facilitator_agent_critic
        self.structuring_coach_agent = structuring_coach_agent
        self.structuring_router_agent = structuring_router_agent
        self.argument_flow_agent = argument_flow_agent
        self.structuring_idea_structurer_agent = structuring_idea_structurer_agent
        self.facilitator_agent_structuring = facilitator_agent_structuring

        # Ideation Subgraph
        self.ideation = IdeationSubgraph(
            self.facilitator_agent_ideation,
            self.router_agent,
            self.idea_generator_agent,
            self.subject_specialist_agent,
            self.idea_structurer_agent
        )
        
        # Critic Subgraph
        self.critic = CriticSubgraph(
            self.facilitator_agent_critic,
            critic_agent,
            idea_structurer_agent
        )

        # Structuring Subgraph
        self.structuring = StructuringSubgraph(
            self.facilitator_agent_structuring,
            self.structuring_coach_agent,
            self.argument_flow_agent, 
            self.structuring_router_agent,
            self.structuring_idea_structurer_agent,
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

        # ideation subgraph
        gb.add_node("ideation", self.ideation.graph)

        # critic subgraph
        gb.add_node("critic", self.critic.graph)

        # structuring subgraph
        gb.add_node("structuring", self.structuring.graph)

        gb.add_edge(START, "ideation")
        gb.add_edge("ideation", "critic")
        gb.add_edge("critic", "structuring")
        gb.add_edge("structuring", END)

        return gb
    
    # -----------------------------
    # Streaming runner with interrupt handling
    # -----------------------------
    #def stream_updates(
    #    self,
    #    initial_state: State,
    #    thread_id: str,
    #):
    #    """
    #    Yields (node_name, state_key, value) updates.
#
    #    Handles interrupts by prompting on CLI and resuming with Command(resume=...).
    #    """
#
    #    fields = {
    #"facilitator": "facilitator_reply",
    #"router": "route",
    #"idea_generation": "idea_generator_reply",
    #"idea_expansion": "subject_specialist_reply",
    #}
    #    initial_input =initial_state
#
    #    while True:
    #        for _, chunk in self.graph.stream(
    #            initial_input,
    #            config={"configurable": {"thread_id": thread_id}},
    #            subgraphs=True,
    #            stream_mode="updates",
    #        ):
    #            # Handle turn boundary
    #            if "__interrupt__" in chunk:
    #                prompt = chunk["__interrupt__"][0].value
    #                print (str(prompt))
    #                user_response = input().strip()
    #                # Resume from interrupt
    #                initial_input = Command(resume=user_response)
    #                break
    #             
    #            ## Emit useful node updates
    #            for node, state_key in fields.items():
    #                if node in chunk:
    #                    node_update = chunk[node]
    #                    if isinstance(node_update, dict) and state_key in node_update:
    #                        yield (node, state_key, node_update[state_key])
    
    def stream_updates(self, initial_state: State, thread_id: str, resume_text: str | None = None):
     """
     Run until the next interrupt (or END).
     Yields updates, and on interrupt yields ("__interrupt__", "interrupt_prompt", <prompt>) then returns.
     """
     initial_input = Command(resume=resume_text) if resume_text is not None else initial_state
 
     for _, chunk in self.graph.stream(
         initial_input,
         config={"configurable": {"thread_id": thread_id}},
         subgraphs=True,
         stream_mode="updates",
     ):
         # interrupt boundary
         if "__interrupt__" in chunk:
             prompt = chunk["__interrupt__"][0].value
             yield ("__interrupt__", "interrupt_prompt", str(prompt))
             return
 
         # flatten updates (handles subgraph outputs)
         for node_name, node_update in chunk.items():
             if node_name == "__interrupt__":
                 continue
 
             # if parent node (e.g., "ideation") wraps subnodes
             if node_name == "ideation" and isinstance(node_update, dict):
                 for subnode, subupdate in node_update.items():
                     if isinstance(subupdate, dict):
                         for k, v in subupdate.items():
                             yield (subnode, k, v)
                 continue
 
             if isinstance(node_update, dict):
                 for k, v in node_update.items():
                     yield (node_name, k, v)
    def show_graph(self):
     # Mermaid diagram
     mermaid = self.graph.get_graph().draw_mermaid()
     with open("planning_graph.md", "w") as f:
         f.write(mermaid)
