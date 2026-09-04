# System Design

## 1. What happens if we ask you to add a new feature to this later? Does your current design accommodate that, or does it need a rework? Walk through a specific feature and where it would plug in.

The current design can accommodate additional fleet features without requiring a major rework because the system separates robot event ingestion, state management, and consumer interfaces. For example, if we were asked to add low-battery alerts, the existing robot events already contain the battery percentage. The event would continue to enter through POST /api/robots/events in backend/main.py, and update_robot_state() in backend/state.py would update the robot's current state as it does today. A low-battery check could then be added after the state update to evaluate whether the robot has crossed a configured battery threshold.

The resulting alert could be exposed through a new REST endpoint or delivered through the existing WebSocket ConnectionManager in backend/main.py. This means the existing robot simulators, event schema, and current-state model would not need to be reworked for this feature. If a future feature required historical information rather than only the current state, I would add persistent storage alongside the current-state layer rather than replacing the existing ingestion flow.


## 2. What happens if the number of robots grows a lot, say from eight to five hundred? What is the first thing that breaks, and why that specifically?

The first thing I would expect to become a bottleneck is the WebSocket broadcast of the entire fleet state on every robot event. Currently, receive_robot_event() in backend/main.py updates fleet_state and then calls manager.broadcast(fleet_state), which sends the complete state of all robots to every connected WebSocket client. With eight robots this is simple and inexpensive, but with 500 robots, every single event would cause a much larger payload to be sent to every connected client, even though only one robot may have changed. As the event rate and number of connected clients increase, this creates unnecessary network traffic and backend work.

I would address this by changing the WebSocket protocol to send only the changed robot or a state delta instead of the entire fleet snapshot for every event. The REST endpoint could continue returning the complete current fleet state when requested. If the system grew further, I would then consider scaling the backend state and WebSocket layer across multiple processes or instances, but the unnecessary full-fleet WebSocket broadcast is the first specific issue I would address at 500 robots.


## 3. What happens if bandwidth is limited and robots and the backend can only exchange a small amount of data per second? What would you change about what you send, how often, or how much detail it carries?

If bandwidth between the robots and backend were limited, I would reduce the amount and frequency of data sent by the simulators in simulator/robot_simulator.py. Currently, each recorded event from events.jsonl is sent to POST /api/robots/events, including the robot's position, battery, status, and event timestamp. Instead of sending every event, the simulator could send updates at a fixed interval or only when important state changes occur, such as a significant position change, battery change, or status transition. The event payload could also be reduced to only the fields required to maintain fleet_state in backend/state.py.

On the backend side, receive_robot_event() in backend/main.py would continue updating the current state through update_robot_state(). I would keep the full current state internally, but make the robot-to-backend payload smaller and less frequent so the constrained link carries only useful changes. This would trade some real-time precision for lower bandwidth usage while preserving the same ingestion and state-management structure.


## 4. What happens if a robot goes down mid task and stops responding? What should the rest of the system do about it, and how would it even find out?

The backend should not treat the last known robot state as indefinitely current. In the current implementation, `update_robot_state()` in `backend/state.py` records `last_received_at` whenever an event is accepted. The background `check_robot_status()` task in `backend/main.py` checks this value once per second. If a robot has previously sent an event and no new event is received for more than the configured 10-second timeout, its status is changed to `offline` and the fleet state is broadcast to WebSocket clients.

This allows both REST and WebSocket consumers to see that the robot is no longer reporting instead of assuming that its last state is still current. The current implementation detects a lack of communication rather than proving that the physical robot itself has failed. In a production system, I would add an explicit heartbeat or health signal and distinguish states such as never connected, stale, disconnected, and offline.


## 5. What happens if the connection between a robot and the backend is slow or unreliable, and updates arrive late, out of order, or not at all for a while? What does the rest of the system see during that time, and how does it recover once the connection is healthy again?

If the connection is unreliable, simulator/robot_simulator.py retries failed HTTP requests using bounded exponential backoff, so temporary failures do not immediately cause an event to be lost. If events arrive late or out of order, update_robot_state() in backend/state.py compares the incoming event's t value with the robot's last_event_time and ignores older events. While no new event is received, the REST endpoint get_fleet_state() and WebSocket clients continue to see the robot's last accepted state. If the gap exceeds the 10-second OFFLINE_TIMEOUT, check_robot_status() in backend/main.py marks the robot as "offline" and broadcasts that updated state.

Once communication becomes healthy again, a successfully received event is processed normally by receive_robot_event() and update_robot_state(), updating the robot's current position, battery, status, and event timestamp. The retry mechanism handles temporary delivery failures, while the timestamp check prevents delayed older events from overwriting newer state. WebSocket clients then receive the updated fleet state through manager.broadcast(fleet_state), and the REST endpoint reflects the recovered robot state.
