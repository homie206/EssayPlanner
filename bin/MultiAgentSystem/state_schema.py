from typing_extensions import TypedDict
from typing import List

class State(TypedDict):
    idea_board: str
    structures: List[str]
    subject: str
    user_message: str 
    facilitator_reply : str
    idea_generator_reply: str
    subject_specialist_reply: str
    critic_reply: str
    facilitation_done: bool
    iteration : int
    thread_id: str