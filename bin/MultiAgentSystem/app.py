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
        "idea_board": "",
        "structures": [],
        "subject": subject,
        "turn_user_messages": [],
        "latest_user_message": essay_topic,
        "facilitator_reply": "",
        "idea_generator_reply": "",
        "subject_specialist_reply": "",
        "critic_reply": "",
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

    facilitator_ideation, idea_generator, subject_specialist, idea_structurer, critic, router, facilitator_agent_critic, structuring_coach, argument_flow = create_all_agents(state)
    mas = PlanningModule(
        idea_generator_agent=idea_generator,
        facilitator_agent_ideation=facilitator_ideation,
        idea_structurer_agent=idea_structurer,
        subject_specialist_agent=subject_specialist,
        critic_agent=critic,
        router_agent=router,
        facilitator_agent_critic=facilitator_agent_critic,
        structuring_coach_agent=structuring_coach,
        argument_flow_agent=argument_flow
    )

    SESSIONS[thread_id] = {"mas": mas, "state": state}
    return run_once(thread_id, resume_text=None)


@app.post("/message/{thread_id}")
def message(thread_id: str, req: MsgReq):
    return run_once(thread_id, resume_text=req.message)