from backend.models import Robot, RobotEvent
from backend.state import add_event, add_robot, fleet_state, reset_state


def test_state_accepts_robots_and_events() -> None:
    reset_state()
    add_robot(Robot(id="r1", name="Pepper"))
    add_event(
        RobotEvent(
            robot_id="r1",
            event_type="heartbeat",
            timestamp="2026-09-02T00:00:00Z",
        )
    )

    assert len(fleet_state["robots"]) == 1
    assert len(fleet_state["events"]) == 1
    reset_state()
