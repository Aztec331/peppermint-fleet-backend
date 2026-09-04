from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_root() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Peppermint Fleet Backend is running"
    }


def test_get_fleet_state() -> None:
    response = client.get("/api/robots")

    assert response.status_code == 200
    assert "r1" in response.json()
    assert "r8" in response.json()


def test_receive_robot_event() -> None:
    event = {
        "t": 100,
        "robot_id": "r1",
        "x": 123,
        "y": 456,
        "status": "active",
        "battery": 80,
    }

    response = client.post("/api/robots/events", json=event)

    assert response.status_code == 200
    assert response.json() == {"message": "Event received"}

    state = client.get("/api/robots").json()

    assert state["r1"]["x"] == 123
    assert state["r1"]["y"] == 456
    assert state["r1"]["battery"] == 80
    assert state["r1"]["status"] == "active"