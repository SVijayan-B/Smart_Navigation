import json
import random
import time
from typing import Dict, List

import networkx as nx
import paho.mqtt.client as mqtt

from routing.map_loader import load_city


BROKER_HOST = "localhost"
BROKER_PORT = 1883
TOPIC = "traffic/sensors"
VEHICLE_COUNT = 30
TICK_SECONDS = 1.0


def _node_xy(graph, node_id):
    return float(graph.nodes[node_id]["y"]), float(graph.nodes[node_id]["x"])


def _random_node(graph):
    return random.choice(list(graph.nodes))


def _pick_path(graph):
    for _ in range(30):
        start = _random_node(graph)
        end = _random_node(graph)
        if start == end:
            continue
        try:
            path = nx.shortest_path(graph, start, end, weight="length")
            if len(path) > 1:
                return path
        except nx.NetworkXNoPath:
            continue
    raise RuntimeError("Unable to generate a valid vehicle path")


def _edge_length(graph, u, v):
    edge_data = graph.get_edge_data(u, v)
    if not edge_data:
        return 1.0
    first_key = next(iter(edge_data))
    return float(edge_data[first_key].get("length", 1.0))


def _new_vehicle(graph, vehicle_id: str) -> Dict:
    path = _pick_path(graph)
    base_speed = random.uniform(18, 55)
    lat, lon = _node_xy(graph, path[0])
    return {
        "vehicle_id": vehicle_id,
        "path": path,
        "edge_index": 0,
        "distance_on_edge": 0.0,
        "speed": base_speed,
        "last_speed": base_speed,
        "lat": lat,
        "lon": lon,
    }


def _advance_vehicle(graph, vehicle: Dict, dt: float) -> Dict:
    path = vehicle["path"]
    if vehicle["edge_index"] >= len(path) - 1:
        vehicle.update(_new_vehicle(graph, vehicle["vehicle_id"]))
        path = vehicle["path"]

    u = path[vehicle["edge_index"]]
    v = path[vehicle["edge_index"] + 1]
    edge_length = max(_edge_length(graph, u, v), 1.0)

    vehicle["last_speed"] = vehicle["speed"]
    speed_delta = random.uniform(-6.0, 6.0)
    vehicle["speed"] = max(5.0, min(70.0, vehicle["speed"] + speed_delta))

    step_dist = (vehicle["speed"] * 1000.0 / 3600.0) * dt
    vehicle["distance_on_edge"] += step_dist

    while vehicle["distance_on_edge"] >= edge_length and vehicle["edge_index"] < len(path) - 1:
        vehicle["distance_on_edge"] -= edge_length
        vehicle["edge_index"] += 1

        if vehicle["edge_index"] >= len(path) - 1:
            vehicle.update(_new_vehicle(graph, vehicle["vehicle_id"]))
            path = vehicle["path"]
            u = path[0]
            v = path[1]
            edge_length = max(_edge_length(graph, u, v), 1.0)
            break

        u = path[vehicle["edge_index"]]
        v = path[vehicle["edge_index"] + 1]
        edge_length = max(_edge_length(graph, u, v), 1.0)

    ratio = min(max(vehicle["distance_on_edge"] / edge_length, 0.0), 1.0)
    u_lat, u_lon = _node_xy(graph, u)
    v_lat, v_lon = _node_xy(graph, v)

    vehicle["lat"] = u_lat + ((v_lat - u_lat) * ratio)
    vehicle["lon"] = u_lon + ((v_lon - u_lon) * ratio)

    acceleration = (vehicle["speed"] - vehicle["last_speed"]) / max(dt, 0.1)
    route_id = f"{u}-{v}"

    return {
        "vehicle_id": vehicle["vehicle_id"],
        "route_id": route_id,
        "latitude": round(vehicle["lat"], 7),
        "longitude": round(vehicle["lon"], 7),
        "speed": round(vehicle["speed"], 2),
        "Ax": round(acceleration + random.uniform(-0.4, 0.4), 3),
        "Ay": round(random.uniform(-0.8, 0.8), 3),
        "Az": round(random.uniform(-0.3, 0.3), 3),
        "front_distance": round(random.uniform(2.0, 80.0), 2),
        "temperature": round(random.uniform(28.0, 38.0), 2),
        "humidity": round(random.uniform(45.0, 88.0), 2),
        "ts": int(time.time()),
    }


def main():
    graph = load_city()
    vehicles: List[Dict] = [_new_vehicle(graph, f"veh-{idx:03d}") for idx in range(1, VEHICLE_COUNT + 1)]

    client = mqtt.Client()
    client.connect(BROKER_HOST, BROKER_PORT)

    print(f"Simulator started with {VEHICLE_COUNT} vehicles on Chennai road graph")

    while True:
        for vehicle in vehicles:
            payload = _advance_vehicle(graph, vehicle, TICK_SECONDS)
            client.publish(TOPIC, json.dumps(payload))
        print(f"Published tick for {VEHICLE_COUNT} vehicles")
        time.sleep(TICK_SECONDS)


if __name__ == "__main__":
    main()