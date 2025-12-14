from .llm_connector import create_agent, chat
from .prompts import build_prompt_for_agent
from .tools import Tools


prompt = build_prompt_for_agent("SubjectSpecialist", "mental health")
subject_specialist_agent = create_agent(prompt, tools=[Tools.retrieve_knowledge])


reply = chat(
            subject_specialist_agent,      
            "effects of soical media on mental health",
            thread_id="abc"
        )

print(reply)