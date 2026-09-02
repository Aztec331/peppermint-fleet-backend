import json
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
        }

    return fleet_state


robots = load_robots()
fleet_state = initialize_fleet_state(robots)

print(fleet_state)