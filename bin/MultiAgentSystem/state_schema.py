from typing_extensions import TypedDict
from typing import List

class State(TypedDict):
    idea_board: str
    structures: List[str]
    subject: str
    user_message: str # latest student message
    facilitator_turn : int
    facilitator_reply_1 : str
    facilitator_reply_2 : str
    idea_generator_reply: str
    subject_specialist_reply: str
    iteration : int
    thread_id: str