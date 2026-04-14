
from .prompts import build_prompt_for_agent
from .tools import Tools
from .idea_gen_graph import IdeationSubgraph
from .agents import create_all_agents
from .state_schema import State
import uuid 
import sys, time
from langgraph.types import Command
from .llm_connector import chat



thread_id = str(uuid.uuid4())
subject = "Education"
initial_state: State = {
    "idea_board" : """
Essay topic: Impact of AI on Education

Main angle / tentative argument:
AI has a positive impact on education because it makes learning more personalised, accessible, and efficient, but it also creates risks like overreliance, cheating, and inequality. Therefore, AI should be used to support teachers and students, not replace human teaching.

Main ideas:
- AI can personalise learning by adjusting difficulty and giving explanations in different styles.
- Students can get instant feedback, which may improve understanding and motivation.
- AI can help teachers by reducing workload such as marking, lesson planning, and creating resources.
- AI can improve accessibility for students with disabilities and language barriers through translation, text-to-speech, speech-to-text, and simplified explanations.
- AI can act as a brainstorming partner in creative tasks and reduce blank page anxiety.
- AI may help schools with tracking progress and identifying students who need support.

Negative points / concerns:
- Students may become overdependent on AI and stop thinking for themselves.
- AI can make cheating and plagiarism easier.
- AI-generated work may become generic and reduce originality.
- Some students and schools may have better access to AI tools than others, which could increase inequality.
- AI systems may give biased or inaccurate information.
- There are privacy concerns if student data is collected and stored.

Examples / scenarios:
- A student struggling with maths uses AI tutoring to get step-by-step explanations at home.
- A teacher uses AI to generate differentiated worksheets for mixed-ability students.
- An ESL student uses AI translation and simplified explanations to understand lessons better.
- A student uses AI to write an essay and gets good marks, but later performs poorly in an exam because they did not actually learn the skill.

Possible structure:
1. Introduction – AI is rapidly changing education.
2. Benefits of AI for students and teachers.
3. AI and accessibility / personalised learning.
4. Risks such as cheating, dependence, and inequality.
5. Conclusion – AI should be used in moderation.

Things I am not fully sure about yet:
- Whether the essay should focus more on students or on the education system as a whole.
- Whether creativity should be a main paragraph or just a smaller supporting point.
- Whether AI overall is more positive than negative.
- I need stronger real-world examples and maybe evidence.
""",
    "structures": [],
    "subject": subject,
    "turn_user_messages": [],
    "latest_user_message": "",
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
facilitator_ideation, idea_generator, subject_specialist, idea_structurer, critic, router, facilitator_agent_critic, structuring_coach, argument_flow, facilitator_structuring, structuring_router, structuring_idea_structurer  = create_all_agents(initial_state)
subgraph = IdeationSubgraph(
    facilitator_agent=facilitator_ideation,
    router_agent=router,
    idea_generator_agent=idea_generator,
    subject_specialist_agent=subject_specialist,
    idea_structurer_agent=idea_structurer,
)

png_path = subgraph.save_mermaid_png("graphs/ideation_subgraph.png")
print("Saved graph to:", png_path)
