from .llm_connector import create_agent, chat
from .prompts import build_prompt_for_agent
from .tools import Tools


prompt = build_prompt_for_agent("Critic", "Education", agent_turn=1)
agent = create_agent(prompt)

user_input = ("ESSAY QUESTION:\n"
    "Should AI be used in education?\n"
    "\n"
    "CURRENT IDEA BOARD (student developed ideas):\n"
    "\n"
    "Idea 1: AI helps teachers with marking.\n"
    "Student explanation: AI can automatically check grammar and structure in written work, "
    "which reduces repetitive marking and saves teacher time.\n"
    "\n"
    "Idea 2: Students may rely too much on AI.\n"
    "Student explanation: Students could use AI tools to plan or write work instead of thinking "
    "independently, which may weaken problem-solving skills.\n"
    "\n"
    "Idea 3: AI enables personalised learning.\n"
    "Student explanation: AI systems can adapt tasks to student level, allowing weaker students "
    "to get support and stronger students to progress faster.\n"
    "\n"
    )

reply = chat(
        agent,      
        "user message : " + user_input,
        thread_id="abc"
    )

while True:
 user_input = input("User: ") 
 reply = chat(
            agent,      
            "user message : " + user_input,
            thread_id="abc"
        )

 print(reply)