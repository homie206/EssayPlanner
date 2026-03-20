
from .prompts import build_prompt_for_agent
from .tools import Tools
from .critic_graph import CriticSubgraph
from .agents import create_all_agents
from .state_schema import State
import uuid 
import sys, time
from langgraph.types import Command
from .llm_connector import chat



thread_id = str(uuid.uuid4())
subject = "Education"
state: State = {
    "idea_board" : """
Essay topic: Impact of AI on Education

Main ideas:
- AI can personalise learning by adjusting difficulty and giving explanations in different styles.
- Students can get instant feedback, which may improve understanding and motivation.
- AI can help teachers by reducing workload such as marking, lesson planning, and creating resources.
- AI can improve accessibility for students with disabilities and language barriers through translation, text-to-speech, speech-to-text, and simplified explanations.
- AI can act as a brainstorming partner in creative tasks and reduce blank page anxiety.
- AI may help schools with tracking progress and identifying students who need support.
""",
    "structures": [],
    "subject": subject,
    "turn_user_messages": [],
    "latest_user_message": "lets expand on the current ideas",
    "facilitator_turn": 1,
    "facilitator_reply": "",
    "idea_generator_reply": "",
    "subject_specialist_reply": "",
    "critic_reply": "",
    "facilitation_done": False,
    "iteration": 1,
    "thread_id": thread_id,
    "essay_topic": "use of AI in education",
    "route": "none",
    "done": False
}
#create agents and the MAS graph
facilitator_ideation, idea_generator, subject_specialist, idea_structurer, critic, router, facilitator_agent_critic, structuring_coach, argument_flow, facilitator_structuring = create_all_agents(state)

reply = chat(
            subject_specialist,
            state["latest_user_message"] + "\nEssay topic: " + state["essay_topic"] + "\nExisting ideas: " + state["idea_board"],
            thread_id=state["thread_id"],
        )
print(reply)