from backend.state import initialize_fleet_state, update_robot_state


def test_update_robot_state_accepts_newer_event() -> None:
    fleet_state = initialize_fleet_state([
        {
            "robot_id": "r1",
            "robot_type": "picker",
            "start": {"x": 0, "y": 0},
        }
    ])

    event = {
        "t": 10,
        "robot_id": "r1",
        "x": 100,
        "y": 200,
        "status": "active",
        "battery": 90,
    }

    update_robot_state(fleet_state, event)

    assert fleet_state["r1"]["x"] == 100
    assert fleet_state["r1"]["y"] == 200
    assert fleet_state["r1"]["battery"] == 90
    assert fleet_state["r1"]["last_event_time"] == 10


def test_update_robot_state_ignores_older_event() -> None:
    fleet_state = initialize_fleet_state([
        {
            "robot_id": "r1",
            "robot_type": "picker",
            "start": {"x": 0, "y": 0},
        }
    ])

    newer_event = {
        "t": 10,
        "robot_id": "r1",
        "x": 100,
        "y": 200,
        "status": "active",
        "battery": 90,
    }

    older_event = {
        "t": 5,
        "robot_id": "r1",
        "x": 50,
        "y": 60,
        "status": "idle",
        "battery": 50,
    }

    update_robot_state(fleet_state, newer_event)
    update_robot_state(fleet_state, older_event)

    assert fleet_state["r1"]["x"] == 100
    assert fleet_state["r1"]["y"] == 200
    assert fleet_state["r1"]["battery"] == 90
    assert fleet_state["r1"]["last_event_time"] == 10