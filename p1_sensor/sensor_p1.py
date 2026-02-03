import time, json, random
from datetime import datetime
import paho.mqtt.client as mqtt

BROKER_HOST = "broker.emqx.io"
BROKER_PORT = 1883

SPOTS = [f"A{i:02d}" for i in range(1, 21)]

THRESHOLD_CM = 50.0
READ_INTERVAL_S = 1.0
DEBOUNCE_N = 4

DIST_FREE = (150, 280)
DIST_PARK = (10, 35)
NOISE_CM = 2.0

ENTRY_TOPIC = "smart_parking_2026/parking/entry_sensor/status"
EXIT_TOPIC  = "smart_parking_2026/parking/exit_sensor/status"

ENTRY_EXIT_OCCUPIED_SECONDS = (1.5, 3.0)   # how long sensor stays OCCUPIED when triggered
ENTRY_EXIT_FREE_SECONDS = (4.0, 12.0)      # time between triggers (demo)

def now():
    return datetime.now().isoformat(timespec="seconds")

class Spot:
    def __init__(self, spot_id: str):
        self.spot_id = spot_id
        self.has_car = False
        self.activity = random.uniform(0.6, 1.6)
        self.next_switch = time.time() + self._free_duration()
        self.stable_status = "FREE"
        self.occ_count = 0
        self.free_count = 0

    def _park_duration(self):
        base = random.uniform(45, 180)
        return base / self.activity

    def _free_duration(self):
        base = random.uniform(30, 150)
        return base / self.activity

    def _update_world(self):
        t = time.time()
        if t >= self.next_switch:
            self.has_car = not self.has_car
            self.next_switch = t + (self._park_duration() if self.has_car else self._free_duration())

    def read_distance(self) -> float:
        self._update_world()
        base = random.uniform(*(DIST_PARK if self.has_car else DIST_FREE))
        noise = random.uniform(-NOISE_CM, NOISE_CM)
        return max(0.0, base + noise)

    def update_debounced_status(self, distance_cm: float) -> str:
        detected_occ = distance_cm < THRESHOLD_CM

        if detected_occ:
            self.occ_count += 1
            self.free_count = 0
        else:
            self.free_count += 1
            self.occ_count = 0

        if self.stable_status != "OCCUPIED" and self.occ_count >= DEBOUNCE_N:
            self.stable_status = "OCCUPIED"
            self.occ_count = 0
            self.free_count = 0

        elif self.stable_status != "FREE" and self.free_count >= DEBOUNCE_N:
            self.stable_status = "FREE"
            self.occ_count = 0
            self.free_count = 0

        return self.stable_status

class GateSensor:
    def __init__(self, name: str, topic: str):
        self.name = name
        self.topic = topic
        self.state = "FREE"
        self.next_toggle = time.time() + random.uniform(*ENTRY_EXIT_FREE_SECONDS)

    def step(self):
        t = time.time()
        if t >= self.next_toggle:
            if self.state == "FREE":
                self.state = "OCCUPIED"
                self.next_toggle = t + random.uniform(*ENTRY_EXIT_OCCUPIED_SECONDS)
            else:
                self.state = "FREE"
                self.next_toggle = t + random.uniform(*ENTRY_EXIT_FREE_SECONDS)

        return self.state

def main():
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="SmartPark2026_P1"
    )
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    client.loop_start()

    spots = [Spot(s) for s in SPOTS]
    last_published_spots = {s: None for s in SPOTS}

    entry_sensor = GateSensor("ENTRY", ENTRY_TOPIC)
    exit_sensor = GateSensor("EXIT", EXIT_TOPIC)
    last_entry_state = None
    last_exit_state = None

    try:
        while True:
            # ---- Parking spots ----
            for sp in spots:
                d = sp.read_distance()
                status = sp.update_debounced_status(d)

                if status != last_published_spots[sp.spot_id]:
                    last_published_spots[sp.spot_id] = status
                    topic = f"smart_parking_2026/parking/spots/{sp.spot_id}/status"
                    payload = {
                        "id": sp.spot_id,
                        "status": status,
                        "distance_cm": round(d, 1),
                        "threshold_cm": THRESHOLD_CM,
                        "debounce_n": DEBOUNCE_N,
                        "ts": now()
                    }
                    client.publish(topic, json.dumps(payload), qos=1, retain=True)
                    print(f"{payload['ts']} | {sp.spot_id} => {status} (distance={payload['distance_cm']}cm)")

            # ---- Entry sensor ----
            entry_state = entry_sensor.step()
            if entry_state != last_entry_state:
                last_entry_state = entry_state
                payload = {"status": entry_state, "ts": now()}
                client.publish(ENTRY_TOPIC, json.dumps(payload), qos=1, retain=True)
                print(f"{payload['ts']} | ENTRY_SENSOR => {entry_state}")

            # ---- Exit sensor ----
            exit_state = exit_sensor.step()
            if exit_state != last_exit_state:
                last_exit_state = exit_state
                payload = {"status": exit_state, "ts": now()}
                client.publish(EXIT_TOPIC, json.dumps(payload), qos=1, retain=True)
                print(f"{payload['ts']} | EXIT_SENSOR => {exit_state}")

            time.sleep(READ_INTERVAL_S)

    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
