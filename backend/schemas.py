from pydantic import BaseModel


class RobotEvent(BaseModel):
    """Represent a single robot event received by the backend."""

    t: int
    robot_id: str
    x: float
    y: float
    status: str
    battery: float