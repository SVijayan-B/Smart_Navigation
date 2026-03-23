from fastapi import FastAPI
from fastapi import WebSocket
from fastapi import WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import osmnx as ox

from routing.map_loader import load_city
from routing.router import best_route
from traffic.traffic_store import get_all_route_averages, get_live_vehicles

app = FastAPI()

# allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading map...")

graph = load_city()

print("Map loaded")


@app.get("/route")
def route(start_lat: float, start_lon: float, end_lat: float, end_lon: float):
    start_node = ox.distance.nearest_nodes(graph, start_lon, start_lat)
    end_node = ox.distance.nearest_nodes(graph, end_lon, end_lat)
    path = best_route(graph, start_node, end_node)
    return {"route": path}


@app.get("/traffic")
def traffic():
    roads = []
    for route_id, value in get_all_route_averages().items():
        try:
            start, end = route_id.split("-")
            start = int(start)
            end = int(end)
            lat1 = graph.nodes[start]["y"]
            lon1 = graph.nodes[start]["x"]
            lat2 = graph.nodes[end]["y"]
            lon2 = graph.nodes[end]["x"]
            roads.append({"coords": [[lat1, lon1], [lat2, lon2]], "traffic": value})
        except Exception:
            continue
    return {"roads": roads}


@app.get("/vehicles")
def vehicles():
    return {"vehicles": get_live_vehicles()}


@app.websocket("/ws/live")
async def live_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            roads = []
            for route_id, value in get_all_route_averages().items():
                try:
                    start, end = route_id.split("-")
                    start = int(start)
                    end = int(end)
                    lat1 = graph.nodes[start]["y"]
                    lon1 = graph.nodes[start]["x"]
                    lat2 = graph.nodes[end]["y"]
                    lon2 = graph.nodes[end]["x"]
                    roads.append({"coords": [[lat1, lon1], [lat2, lon2]], "traffic": value})
                except Exception:
                    continue

            payload = {"traffic": roads, "vehicles": get_live_vehicles()}
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        return
