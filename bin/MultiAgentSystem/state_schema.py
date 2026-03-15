from typing_extensions import Literal, TypedDict
from typing import List

Route = Literal["idea_generation", "idea_expansion", "none"]
class State(TypedDict):
    idea_board: str
    structures: List[str]
    subject: str
    turn_user_messages: List[str]
    latest_user_message: str 
    facilitator_reply : str
    idea_generator_reply: str
    subject_specialist_reply: str
    critic_reply: str
    structuring_coach_reply: str
    argument_flow_reply: str
    facilitation_done: bool
    ideation_iteration : int
    critic_iteration : int
    structuring_iteration : int
    thread_id: str
    essay_topic: str
    route: Route
    criticising_done : bool
    structuring_done : bool
