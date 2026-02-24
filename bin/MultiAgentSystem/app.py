from __future__ import annotations

import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .agents import create_all_agents
from .ochestrator import PlanningModule
from .state_schema import State  

app = FastAPI(title="Essay MAS API")


# ---------
# In-memory session store
# ---------
@dataclass
class Session:
    thread_id: str
    planning_module: PlanningModule
    state: Dict[str, Any]


SESSIONS: Dict[str, Session] = {}

# ---------
# Request/Response models
# ---------
class CreateSessionRequest(BaseModel):
    essay_topic: str
    subject: str = "Education"


class MessageRequest(BaseModel):
    message: str


class RunResponse(BaseModel):
    thread_id: str
    updates: List[Dict[str, str]]
    needs_user_input: bool
    interrupt_prompt: Optional[str] = None


# ---------
# Helpers
# ---------
def _make_initial_state(thread_id: str, subject: str, essay_topic: str) -> Dict[str, Any]:
    return {
        "idea_board": "",
        "structures": [],
        "subject": subject,
        "turn_user_messages": [],
        "latest_user_message": essay_topic,   # first message = essay topic
        "facilitator_turn": 1,
        "facilitator_reply": "",
        "idea_generator_reply": "",
        "subject_specialist_reply": "",
        "critic_reply": "",
        "facilitation_done": False,
        "iteration": 1,
        "thread_id": thread_id,
        "essay_topic": essay_topic,
        "route": "none",
    }


def _run_until_interrupt(session: Session, resume_text: Optional[str] = None) -> RunResponse:
    updates: List[Dict[str, str]] = []
    interrupt_prompt: Optional[str] = None
    needs_user_input = False

    # Run the graph and collect updates
    for node, key, value in session.planning_module.stream_updates(
        session.state,
        thread_id=session.thread_id,
        resume_text=resume_text,
    ):
        if node == "__interrupt__":
            needs_user_input = True
            interrupt_prompt = value or None
            break

        updates.append({"node": node, "key": key, "value": value})

        # Keep server-side state roughly in sync.
        # This is a simple approach: if your node writes "idea_board", update it, etc.
        # (Your checkpointer/thread_id is still the real source of truth.)
        session.state[key] = value

    return RunResponse(
        thread_id=session.thread_id,
        updates=updates,
        needs_user_input=needs_user_input,
        interrupt_prompt=interrupt_prompt,
    )


# ---------
# API
# ---------
@app.post("/sessions", response_model=RunResponse)
def create_session(req: CreateSessionRequest):
    thread_id = str(uuid.uuid4())
    initial_state = _make_initial_state(thread_id, req.subject, req.essay_topic)

    # Create agents + graph
    facilitator, idea_generator, subject_specialist, idea_structurer, critic, router = create_all_agents(initial_state)
    planning_module = PlanningModule(idea_generator, facilitator, idea_structurer, subject_specialist, critic, router)

    session = Session(thread_id=thread_id, planning_module=planning_module, state=initial_state)
    SESSIONS[thread_id] = session

    # Run once: produces facilitator output, etc., then stops at interrupt waiting for next user input
    return _run_until_interrupt(session, resume_text=None)


@app.post("/sessions/{thread_id}/message", response_model=RunResponse)
def send_message(thread_id: str, req: MessageRequest):
    session = SESSIONS.get(thread_id)
    if not session:
        raise HTTPException(status_code=404, detail="Unknown thread_id")

    # Resume the graph with the user's message
    return _run_until_interrupt(session, resume_text=req.message)


@app.get("/sessions/{thread_id}")
def get_session_state(thread_id: str):
    session = SESSIONS.get(thread_id)
    if not session:
        raise HTTPException(status_code=404, detail="Unknown thread_id")
    return {"thread_id": thread_id, "state": session.state}