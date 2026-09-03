from fastapi import FastAPI

from backend.schemas import RobotEvent
from backend.state import fleet_state, update_robot_state


app = FastAPI()


@app.get("/")
def root():
    """Return a simple message confirming that the backend is running."""
    return {"message": "Peppermint Fleet Backend is running"}


@app.post("/api/robots/events")
def receive_robot_event(event: RobotEvent):
    """Receive a robot event and update the robot's current fleet state."""
    update_robot_state(fleet_state, event.model_dump())

    return {
    "message": "Event received",
    }

@app.get("/api/robots")
def get_fleet_state() -> dict:
    """Return the current state of all robots in the fleet."""
    return fleet_state