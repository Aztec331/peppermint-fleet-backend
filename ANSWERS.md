# Answers

## 1. What holds the fleet's current state in your backend, and why that shape, given it has to serve both the WebSocket stream and the polling endpoint consistently?

The backend keeps the fleet's current state in an in-memory Python dictionary called `fleet_state` in `backend/state.py`, keyed by `robot_id`. Each entry contains the robot's identity and type, current position, battery, status, the timestamp of the latest accepted event, and the time the backend last received an event. The initial state is created from `data/robots.json` by `initialize_fleet_state()`, while `update_robot_state()` applies incoming events to the corresponding robot.

I chose this shape because the main requirement is to maintain the latest state of each robot rather than a persistent event history. More importantly, it gives both consumer interfaces one source of truth. `GET /api/robots` returns `fleet_state`, while the WebSocket implementation in `backend/main.py` sends the same state through `ConnectionManager`. This avoids maintaining separate REST and WebSocket state that could become inconsistent. `update_robot_state()` also compares the incoming event timestamp with `last_event_time` so an older event cannot overwrite a newer accepted state.


## 2. Name one real tradeoff you made: the mechanism you chose for robots to reach your backend, its delivery guarantees, and how you reconcile that mechanism's semantics with your WebSocket fanout. Argue for the decision, including its cost.

I chose HTTP callbacks for robot-to-backend communication. Each independent robot simulator reads its events from `data/events.jsonl` and sends them to `POST /api/robots/events`. I chose HTTP because it keeps the producer-consumer boundary simple, is easy to inspect and debug during local development, and does not require an additional broker service for this small fleet. The simulator also retries failed HTTP requests with bounded exponential backoff, giving temporary connection failures a chance to recover. On the backend, `update_robot_state()` uses the event timestamp to prevent a late older event from replacing newer state.

The tradeoff is that HTTP callbacks with application-level retries do not provide the durable buffering and delivery guarantees of a message broker or persistent queue. If the backend remains unavailable beyond the retry window, an event can still be lost. Once an event is accepted by the backend, the backend updates the shared `fleet_state`, and `ConnectionManager` handles WebSocket fanout to connected consumers. This keeps robot ingestion independent from consumer connections. The cost of this simpler design is that durable event delivery, persistent recovery, and distributed fanout would need additional infrastructure if this were scaled into a production system.


## 3. What did you leave out, and what would you build next given more time?

I intentionally kept the implementation focused on the required current-state backend. I left out persistent fleet history, authentication and authorization, a message broker, distributed/shared state, and the optional history endpoint. I also kept WebSocket fanout simple by broadcasting the current fleet snapshot instead of implementing a delta-based update protocol. These choices kept the implementation small enough to understand, test, and run completely through Docker Compose within the assignment's scope.

Given more time, I would first add persistent event history and shared state so the backend could survive restarts and eventually scale horizontally. I would then add stronger event identifiers or sequence numbers for idempotency and ordering, explicit robot heartbeats for health detection, and delta-based WebSocket updates so consumers receive only the state that changed. Authentication, authorization, and operational monitoring would follow for a production deployment.