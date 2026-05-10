from __future__ import annotations

import uuid
from typing import Any, Dict, Optional, List, Tuple

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .state_schema import State
from .agents import create_all_agents
from .ochestrator import PlanningModule


app = FastAPI()

# minimal CORS for a browser frontend (tighten later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSIONS: Dict[str, Dict[str, Any]] = {}  # thread_id -> {"mas": PlanningModule, "state": State}


class StartReq(BaseModel):
    subject: str = "Education"
    essay_topic: str


class MsgReq(BaseModel):
    message: str


def make_initial_state(thread_id: str, subject: str, essay_topic: str) -> State:
    return {
        "idea_board": """Impact of AI on Education
The use of AI has both positive and negative impacts on education.
Positive Impacts of AI on Education
Democratized Execution: AI acts as a "Technical Equalizer," enabling students with ideas but lacking certain skills (e.g., drawing) to produce creative works like films or comics, shifting value from manual labor to vision and curation.
Rapid Prototyping: Students can test many ideas quickly (e.g., 100 ideas in 10 minutes), reducing fear of failure and encouraging a culture of experimentation and "failing forward."
The "Creative Sparring" Partner: AI acts as a mirror, helping students learn to critique and refine their work rather than just accept it, sharpening their logic and ability to defend creative choices.
The "Socratic" Shift: AI facilitates learning through dialogue and interrogation rather than simple fact retrieval, helping students build deeper mental models beyond memorization.
Negative Impacts of AI on Education
The "Path of Least Resistance":
Creative Laziness: AI generating "good enough" drafts quickly may cause students to stop striving for excellence, bypassing the struggle where original insights are born.
Skill Atrophy: Dependence on AI for structure and phrasing can weaken students' abilities to organize thoughts and master grammar and logic.
Confidence & Imposter Syndrome:
The Perfection Gap: Comparing raw student work to polished AI output may lower students' confidence in their own voice.
Hollow Ownership: Lack of struggle in creating ideas can erode emotional connection and pride in their work.
Algorithmic Homogenization:
The "Average" Trap: AI's tendency to predict the most likely next element based on data may pull students toward average ideas, discouraging radical or unconventional creativity.
Loss of Critical Inquiry:
Acceptance Bias: Students may treat AI as infallible, leading to passive consumption rather than critical questioning necessary for deep learning.""",
        "structures": [],
        "subject": subject,
        "turn_user_messages": [],
        "latest_user_message": essay_topic,
        "facilitator_reply": "",
        "idea_generator_reply": "",
        "subject_specialist_reply": "",
        "critic_reply": "",
        "structuring_coach_reply": "",
        "argument_flow_reply": "",
        "facilitation_done": False,
        "ideation_iteration": 1,
        "critic_iteration": 1,
        "structuring_iteration": 1,
        "thread_id": thread_id,
        "essay_topic": essay_topic,
        "route": "none",
        "done": False,
        "structuring_done": False,
    }   


def run_once(thread_id: str, resume_text: Optional[str]) -> Dict[str, Any]:
    sess = SESSIONS.get(thread_id)
    if not sess:
        raise HTTPException(404, "Unknown thread_id")

    mas: PlanningModule = sess["mas"]
    state: State = sess["state"]

    events: List[Tuple[str, str, Any]] = []
    interrupt_prompt = None

    for node, key, value in mas.stream_updates(state, thread_id=thread_id, resume_text=resume_text):
        if node == "__interrupt__":
            interrupt_prompt = str(value)
            events.append((node, key, interrupt_prompt))
            break
        events.append((node, key, value))

    return {
        "thread_id": thread_id,
        "events": events,
        "needs_user_input": interrupt_prompt is not None,
        "interrupt_prompt": interrupt_prompt,
    }


@app.post("/start")
def start(req: StartReq):
    thread_id = str(uuid.uuid4())
    state = make_initial_state(thread_id, req.subject, req.essay_topic)

    facilitator_ideation, idea_generator, subject_specialist, idea_structurer, critic, router, facilitator_agent_critic, structuring_coach, argument_flow, facilitator_structuring, structuring_router, structuring_idea_structurer  = create_all_agents(state)
    mas = PlanningModule(
        idea_generator_agent=idea_generator,
        facilitator_agent_ideation=facilitator_ideation,
        idea_structurer_agent=idea_structurer,
        subject_specialist_agent=subject_specialist,
        critic_agent=critic,
        router_agent=router,
        facilitator_agent_critic=facilitator_agent_critic,
        structuring_coach_agent=structuring_coach,
        argument_flow_agent=argument_flow,
        facilitator_agent_structuring=facilitator_structuring,
        structuring_router_agent=structuring_router,
        structuring_idea_structurer_agent=structuring_idea_structurer,
    )

    SESSIONS[thread_id] = {"mas": mas, "state": state}
    return run_once(thread_id, resume_text=None)


@app.post("/message/{thread_id}")
def message(thread_id: str, req: MsgReq):
    return run_once(thread_id, resume_text=req.message)