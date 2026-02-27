from .personas import get_agent

def build_prompt_for_agent(
    agent_name: str,
    #session: Session,
    #state: PlanningState,
    #essay_question: str,
    #user_message: str,
    essay_subject: str,
    agent_turn: int = 1
) -> str:
    persona = get_agent(agent_name)
    base_prompt = persona.base_prompt if agent_turn == 1 else persona.base_prompt_2

    subject = essay_subject or "the subject area"
    level = "high-school"  # placeholder for now
    

    if "{subject}" in base_prompt or "{level}" in base_prompt:
        base_prompt = base_prompt.format(subject=subject, level=level)

    prompt = (
        f"{base_prompt}\n"
        #TODO
        #f"{ideas_summary}\n\n"
        f"Respond in a way that matches your role."
    )
    return prompt