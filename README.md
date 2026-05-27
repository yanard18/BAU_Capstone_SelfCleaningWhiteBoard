# Robot Lawnmower — Development Notes

## System Design Plan: Robot Movement

### Hardware Recommendation

Drop Arduino, use **ESP32 alone**. Arduino needs a separate WiFi/BT shield. ESP32 has WiFi built-in, can do PWM for motors, costs the same, and is programmable via Arduino IDE or MicroPython. Less wiring, fewer points of failure.

```
Raspberry Pi (camera + CV + navigation)
    │
    │  WiFi (UDP)
    ▼
ESP32 (motor controller)
    │         │
Motor A    Motor B
(via L298N or similar driver board)
```

---

### Step 1 — Navigation Logic (`navigation.py` on RPi)

The pipeline already gives you everything needed:
- **Position**: `center (x, y)` from ArUco
- **Heading**: the `mid_top` vector already computed in `draw_robot_overlays` — extract angle from it
- **Target**: `path[0]` (next waypoint)

The controller loop is simple:

```
angle_to_target = atan2(target.y - center.y, target.x - center.x)
heading_error   = angle_to_target - robot_heading

if |heading_error| > ANGLE_THRESHOLD  →  ROTATE_CW or ROTATE_CCW
elif distance_to_target > DIST_THRESHOLD  →  FORWARD
else  →  pop path[0], advance to next target
```

**Option A — Bang-bang controller** (simplest, implemented first): fixed speed, just direction.  
**Option B — P-controller**: rotation speed proportional to heading error — smoother but needs tuning.

---

### Step 2 — Communication (`robot_comm.py` on RPi)

| Method | Pros | Cons |
|---|---|---|
| **UDP socket** ← recommended | Simplest, lowest latency, no broker needed | Fire-and-forget, no ACK |
| WebSocket | Bidirectional, ESP32 can send back status | More setup |
| MQTT | Standard IoT pattern, easy to monitor | Needs a broker (Mosquitto) |
| Bluetooth | No router needed | Slower setup, pairing friction |

UDP is the right call here. Movement commands are best-effort — if one packet drops, the next frame sends a fresh command anyway.

**Protocol** — simple string commands, one per frame:
```
"STOP" | "FORWARD" | "BACKWARD" | "ROTATE_CW" | "ROTATE_CCW"
```

---

### Step 3 — Code Structure

Three new files, minimal changes to existing ones:

```
navigation.py   — pure function: (center, corners, path) → command string
robot_comm.py   — UDP socket wrapper: send(command) to ESP32
esp32/main.py   — MicroPython on ESP32: UDP server → motor PWM
```

`run_pipeline` exposes `robot_pos`, `corners`, and `path` in its return dict. The stream loop in `app.py` calls `get_command(...)` and `robot_comm.send(command)` each frame.

---

### Step 4 — ESP32 Side

**Option A — MicroPython** (recommended — you already know Python, flashing MicroPython onto an ESP32 takes 5 minutes):
```python
# esp32/main.py — runs on ESP32
import socket, network
# connect to WiFi, open UDP socket, listen for commands, drive motors via PWM
```

**Option B — Arduino C++**: more boilerplate but more community examples for motor control.

---

### Step 5 — Integration Point

The navigation loop runs **per-frame** inside `_generate_stream()` in `app.py` — it already loops over every frame and calls `run_pipeline`. Add:

```python
command, reached = get_command(result['robot_pos'], result['corners'], path_state)
if reached and path_state:
    path_state.pop(0)
robot_comm.send(command)
```

`path_state` is a module-level list tracking remaining waypoints — refills from the pipeline when empty.

---

### Step 6 — Testing Without Hardware

Before connecting the ESP32:

1. **Nav status overlay** — draw current command, heading error, and distance to target directly on the output frame. Visually verify the command makes sense given the robot's position.
2. **UDP echo server** (`echo_server.py`) — listens on port 5005 and prints every received packet. Verifies `robot_comm.py` sends correctly and deduplication works.
3. **Movement simulator** — modify the mock source to shift the robot's position each frame based on the last command. Closes the loop in software without hardware.

---

### Implementation Order

1. `navigation.py` — pure logic, testable without hardware
2. `robot_comm.py` — UDP sender, testable with `echo_server.py` on a laptop
3. Wire both into `_generate_stream` in `app.py`
4. Nav status overlay + echo server for validation
5. `esp32/main.py` — MicroPython UDP server → motor PWM
