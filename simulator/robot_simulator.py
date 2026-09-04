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

def send_event_with_retry(client: httpx.Client, event: dict) -> bool:
    """Send one robot event with limited retries and exponential backoff."""
    max_retries = 3
    delay = 1

    for attempt in range(max_retries + 1):
        try:
            response = client.post(BACKEND_URL, json=event)
            response.raise_for_status()
            return True
        except httpx.HTTPError as error:
            if attempt == max_retries:
                print(
                    f"{ROBOT_ID} failed after {max_retries} retries: {error}"
                )
                return False

            print(
                f"{ROBOT_ID} failed attempt {attempt + 1}: {error}. "
                f"Retrying in {delay}s..."
            )
            time.sleep(delay)
            delay *= 2

def replay_events(events: list[dict]) -> None:
    """Replay robot events in their recorded order and send them to the backend."""
    with httpx.Client() as client:
        for event in events:
            print(f"{ROBOT_ID} sending event: {event}")

            send_event_with_retry(client, event)

            time.sleep(1)


def main() -> None:
    """Load the robot's events and start replaying them."""
    events = load_robot_events(ROBOT_ID)

    print(f"{ROBOT_ID} loaded {len(events)} events.")

    replay_events(events)


if __name__ == "__main__":
    main()