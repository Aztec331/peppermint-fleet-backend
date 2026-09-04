import json
import time

from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "robots.json"


def load_robots() -> list[dict]:
    """Load the robot roster from robots.json and return it as a Python list."""
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def initialize_fleet_state(robots: list[dict]) -> dict:
    """Create the initial current state for every robot using its starting position."""
    fleet_state = {}

    for robot in robots:
        robot_id = robot["robot_id"]

        fleet_state[robot_id] = {
            "robot_id": robot_id,
            "robot_type": robot["robot_type"],
            "x": robot["start"]["x"],
            "y": robot["start"]["y"],
            "battery": None,
            "status": "idle",
            "last_event_time": None,
            "last_received_at": None,
        }

    return fleet_state


robots = load_robots()
fleet_state = initialize_fleet_state(robots)


def update_robot_state(fleet_state: dict, event: dict) -> None:
    """Update a robot's current state using a newly received event."""

    robot_id = event["robot_id"]

    if robot_id not in fleet_state:
        return

    if (
    fleet_state[robot_id]["last_event_time"] is not None
    and event["t"] < fleet_state[robot_id]["last_event_time"]
    ):
        return

    fleet_state[robot_id].update({
        "x": event["x"],
        "y": event["y"],
        "battery": event["battery"],
        "status": event["status"],
        "last_event_time": event["t"],
    })

    fleet_state[robot_id]["last_received_at"] = time.monotonic()
    