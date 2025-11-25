from .agents import get_agent

def build_prompt_for_agent(
    agent_name: str,
    #session: Session,
    #state: PlanningState,
    #essay_question: str,
    #user_message: str,
    essay_subject: str
) -> str:
    persona = get_agent(agent_name)
    base_prompt = persona.base_prompt

    subject = essay_subject or "the subject area"
    level = "university"  # placeholder for now

    if "{subject}" in base_prompt or "{level}" in base_prompt:
        base_prompt = base_prompt.format(subject=subject, level=level)
    
    #TODO: reintegrate these later
    #ideas_summary = "None yet."
    #if state.ideas:
    #    ideas_summary = "Ideas so far:\n" + "\n".join(f"- {i.text}" for i in state.ideas)

    prompt = (
        f"{base_prompt}\n"
        #TODO
        #f"{ideas_summary}\n\n"
        #f"The student just said: {user_message}\n\n"
        f"Respond in a way that matches your role."
    )
    return prompt