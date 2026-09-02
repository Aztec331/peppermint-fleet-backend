from pydantic import BaseModel


class Robot(BaseModel):
    id: str
    name: str
    status: str = "idle"


class RobotEvent(BaseModel):
    robot_id: str
    event_type: str
    timestamp: str
    payload: dict[str, object] = {}