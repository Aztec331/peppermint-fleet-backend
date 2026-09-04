import asyncio
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from backend.schemas import RobotEvent
from backend.state import fleet_state, update_robot_state


class ConnectionManager:
    """Manage connected WebSocket clients and broadcast fleet updates."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a WebSocket connection and add it to the active clients."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a disconnected WebSocket client."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: dict) -> None:
        """Send data to every currently connected WebSocket client."""
        for websocket in self.active_connections.copy():
            try:
                await websocket.send_json(data)
            except Exception:
                self.disconnect(websocket)


manager = ConnectionManager()

OFFLINE_TIMEOUT = 10
CHECK_INTERVAL = 1


async def check_robot_status():
    """Mark robots offline when no event is received within the timeout."""
    while True:
        current_time = time.monotonic()

        for robot in fleet_state.values():
            last_received_at = robot["last_received_at"]

            if (
                last_received_at is not None
                and current_time - last_received_at > OFFLINE_TIMEOUT
                and robot["status"] != "offline"
            ):
                robot["status"] = "offline"
                await manager.broadcast(fleet_state)

        await asyncio.sleep(CHECK_INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start and stop the background robot status checker."""
    task = asyncio.create_task(check_robot_status())

    yield

    task.cancel()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    """Return a simple message confirming that the backend is running."""
    return {"message": "Peppermint Fleet Backend is running"}


@app.post("/api/robots/events")
async def receive_robot_event(event: RobotEvent):
    """Receive a robot event, update fleet state, and broadcast the update."""
    update_robot_state(fleet_state, event.model_dump())
    await manager.broadcast(fleet_state)

    return {
        "message": "Event received",
    }


@app.get("/api/robots")
def get_fleet_state() -> dict:
    """Return the current state of all robots in the fleet."""
    return fleet_state


@app.websocket("/api/robots/ws")
async def robot_websocket(websocket: WebSocket):
    """Accept a WebSocket client and keep the connection open for updates."""
    # manager is ConnectionManager object
    await manager.connect(websocket)

    try:
        await websocket.send_json(fleet_state)

        while True:
            message = await websocket.receive()

            if message["type"] == "websocket.disconnect":
                break

    except WebSocketDisconnect:
        pass

    finally:
        manager.disconnect(websocket)