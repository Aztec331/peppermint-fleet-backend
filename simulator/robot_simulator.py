import json
import os
import time
from pathlib import Path

import httpx


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "events.jsonl"
BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://localhost:8000/api/robots/events",
)
ROBOT_ID = os.getenv("ROBOT_ID", "r1")


def load_robot_events(robot_id: str) -> list[dict]:
    """Load all recorded events belonging to the specified robot."""
    events = []

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        for line in file:
            event = json.loads(line)

            if event["robot_id"] == robot_id:
                events.append(event)

    return events


def replay_events(events: list[dict]) -> None:
    """Replay robot events in their recorded order and send them to the backend."""
    with httpx.Client() as client:
        for event in events:
            print(f"{ROBOT_ID} sending event: {event}")

            try:
                response = client.post(BACKEND_URL, json=event)
                response.raise_for_status()
            except httpx.HTTPError as error:
                print(f"{ROBOT_ID} failed to send event: {error}")

            time.sleep(1)


def main() -> None:
    """Load the robot's events and start replaying them."""
    events = load_robot_events(ROBOT_ID)

    print(f"{ROBOT_ID} loaded {len(events)} events.")

    replay_events(events)


if __name__ == "__main__":
    main()