import json
import math
import os
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt


HOST = os.getenv("MQTT_HOST", "localhost")
PORT = int(os.getenv("MQTT_PORT", "1883"))
INTERVAL = float(os.getenv("SIMULATOR_INTERVAL", "2"))
MACHINES = ("MOTOR-01", "BOMBA-02", "VENTILADOR-03")


def build_telemetry(machine_id: str, tick: int) -> dict:
    phase = MACHINES.index(machine_id) * 1.7
    incident = random.random() < 0.06
    temperature = 62 + 5 * math.sin(tick / 18 + phase) + random.gauss(0, 1.2)
    vibration = 2.2 + 0.7 * math.sin(tick / 10 + phase) + abs(random.gauss(0, 0.25))
    current = 10.5 + 1.1 * math.sin(tick / 12 + phase) + random.gauss(0, 0.35)
    rpm = 1760 + 55 * math.sin(tick / 15 + phase) + random.gauss(0, 15)

    if incident:
        temperature += random.uniform(16, 34)
        vibration += random.uniform(2.8, 6.5)
        current += random.uniform(4, 10)
        rpm -= random.uniform(250, 700)

    return {
        "machine_id": machine_id,
        "temperature_c": round(temperature, 2),
        "vibration_mm_s": round(max(0, vibration), 2),
        "current_a": round(max(0, current), 2),
        "rpm": round(max(0, rpm), 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="factory-simulator")
    while True:
        try:
            client.connect(HOST, PORT, keepalive=60)
            break
        except OSError:
            print("Aguardando broker MQTT...", flush=True)
            time.sleep(2)

    tick = 0
    try:
        while True:
            for machine_id in MACHINES:
                payload = build_telemetry(machine_id, tick)
                topic = f"factory/machines/{machine_id}/telemetry"
                client.publish(topic, json.dumps(payload), qos=1)
                print(f"{topic}: {payload}", flush=True)
            tick += 1
            time.sleep(INTERVAL)
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
