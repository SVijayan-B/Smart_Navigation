import json
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

from ml.predictor import predict_traffic
from traffic.traffic_store import update_route, update_vehicle_position


ALPHA = 0.6
BETA = 0.4
VMAX = 80.0
EPSILON = 0.1


def _to_float(payload: dict, key: str, default: float = 0.0) -> float:
    try:
        return float(payload.get(key, default))
    except (TypeError, ValueError):
        return default


def _physics_score(payload: dict) -> float:
    speed = max(0.0, _to_float(payload, "speed"))
    front_distance = max(0.0, _to_float(payload, "front_distance", _to_float(payload, "distance_front")))

    density_proxy = 1.0 / (front_distance + EPSILON)
    pressure = (density_proxy * ALPHA) + (1.0 - min(speed / VMAX, 1.0)) * BETA
    pressure_max = ALPHA * (1.0 / EPSILON) + BETA
    normalized_pressure = min(max(pressure / pressure_max, 0.0), 1.0)
    return 1.0 - normalized_pressure


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
        client.subscribe("traffic/sensors")
    else:
        print(f"MQTT connection failed with code {rc}")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        route_id = str(payload["route_id"])

        ml_score = predict_traffic(payload)
        physics_score = _physics_score(payload)
        fused_score = (0.7 * ml_score) + (0.3 * physics_score)
        smoothed = update_route(route_id, fused_score, ts=datetime.now(timezone.utc))
        update_vehicle_position(payload)

        print(
            f"Traffic updated -> route: {route_id} | ml={ml_score:.3f} "
            f"| phy={physics_score:.3f} | ema={smoothed:.3f}"
        )
    except Exception as exc:
        print(f"Error processing message: {exc}")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883)
print("Waiting for sensor stream on traffic/sensors...")
client.loop_forever()
