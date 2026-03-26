from __future__ import annotations
from langgraph.types import interrupt
from langgraph.graph import START, END, StateGraph
from .llm_connector import chat
from .state_schema import State
from pathlib import Path


class CriticSubgraph:
    """
    Holds a compiled ideation subgraph and the agents it needs.
    """
    def __init__(self, facilitator_agent, critic_agent, idea_structurer_agent):
        self.facilitator_agent = facilitator_agent
        self.critic_agent = critic_agent
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
        messages.append(user_reply)
        return {"latest_user_message": user_reply, "turn_user_messages": messages}
    
    def _user_turn_node_2(self, state: State):
        user_reply = interrupt("Your turn:")
        messages = state.get("turn_user_messages", [])
        messages.append(user_reply)
        return {"latest_user_message": user_reply, "turn_user_messages": messages}
        
    def _critic_node(self, state: State):
        critic_input = (
    f"Student message:\n{state['latest_user_message']}\n\n"
    f"Idea board:\n{state.get('idea_board', '')}\n\n"
    f"Outline:\n{state.get('structures', '')}\n\n"
    f"Subject expert reply:\n{state.get('subject_specialist_reply', '')}\n\n"
    f"Idea generator reply:\n{state.get('idea_generator_reply', '')}"
    )
        reply = chat(
            self.critic_agent,      
            critic_input,
            thread_id=state["thread_id"]
        )
        return {"critic_reply": reply}
    
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
        iteration = state["critic_iteration"] + 1
        print(f"--- Starting iteration {iteration} ---")
        return {"critic_iteration": iteration}
    
    def stop_condition(self, state: State) -> bool:
        stop_statement = "We've done a few rounds of criticing. "
        if state["critic_iteration"] > 5 :
            stop_statement = "We've done several more rounds of citicising."
        ans = interrupt(
         stop_statement + "\n\n[YES_NO] Here is the idea board so far:\n\n" + state["idea_board"] + "\n\nAre you happy to move on to the structuring phase?")
        a = str(ans).strip().lower()

        yes = a in {"y", "yes", "yeah", "yep", "sure", "ok", "okay", "go", "move on", "continue"}
        #no = a in {"n", "no", "nope", "not yet", "later", "keep going", "continue ideation"}
    
        if yes:
            return {"criticising_done": True}
        
        return {"criticising_done": False}
    
    def check_move_on(self, state: State):
        messages = state.get("turn_user_messages", [])
        if not messages:
            return {"criticising_done": False}
    
        latest_message = str(messages[-1]).lower().strip()
    
        move_words = {"move on", "go", "skip", "proceed", "continue"}
        target_words = {"structuring phase", "structuring", "structure"}
    
        wants_move = any(word in latest_message for word in move_words)
        wants_target = any(word in latest_message for word in target_words)
    
        if not (wants_move and wants_target):
            return {"criticising_done": False}
    
        ans = interrupt("[YES_NO] Are you sure you want to move on to the structuring phase?")
        confirmed = str(ans).strip().lower() in {
            "y", "yes", "yeah", "yep", "sure", "ok", "okay", "go", "continue"
        }
    
        return {"criticising_done": confirmed}

    
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
            path.write_bytes(img_bytes)

        return str(path)
    
    # ---- graph build ----
    def _build(self) -> StateGraph:
        g = StateGraph(State)

        # ---- nodes ----
        g.add_node("iterator", self._iterater)
        g.add_node("facilitator", self._facilitator_node)
        g.add_node("user_reply_1", self._user_turn_node_1)
        g.add_node("user_reply_2", self._user_turn_node_2)
        g.add_node("critic", self._critic_node)
        g.add_node("structure", self._structure_node)
        g.add_node("cleanup", self._cleanup_messages)
        g.add_node("stop_condition", self.stop_condition)
        g.add_node("move_on", self.check_move_on)

        # ---- edges ----
        g.add_edge(START, "facilitator")
        g.add_conditional_edges(
          START,
          lambda s: "first_turn" if s["critic_iteration"] == 1 else "other_turn",
          {
              "first_turn": "cleanup",
              "other_turn": "facilitator",
          }
        )
        g.add_edge("facilitator", "user_reply_1")
        g.add_edge("user_reply_1", "move_on")
        g.add_conditional_edges(
            "move_on",
            lambda s: s["criticising_done"],
            {
                True: END,
                False: "critic",   
            })
        g.add_edge("critic", "user_reply_2")
        g.add_edge("user_reply_2", "structure")
        g.add_edge("structure", "cleanup")
        g.add_edge("cleanup", "iterator")
        g.add_conditional_edges(
            "iterator",
            lambda s: "stop?" if (s["critic_iteration"] >= 4 and s["critic_iteration"] % 4 == 0) else "continue",
            {
                "stop?": "stop_condition",
                "continue": "facilitator",
            },
        )
        g.add_conditional_edges(
            "stop_condition",
            lambda s: s["criticising_done"],
            {
                True: END,
                False: "facilitator",   
            })
        return g
    