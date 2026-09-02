from .models import Robot, RobotEvent


fleet_state: dict[str, list[Robot | RobotEvent]] = {
    "robots": [],
    "events": [],
}


def add_robot(robot: Robot) -> None:
    fleet_state["robots"].append(robot)


def add_event(event: RobotEvent) -> None:
    fleet_state["events"].append(event)


def reset_state() -> None:
    fleet_state["robots"].clear()
    fleet_state["events"].clear()
