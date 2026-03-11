from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import osmnx as ox

from routing.map_loader import load_city
from routing.router import best_route

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

    route_coords = []

    for node in path:
        lat = graph.nodes[node]['y']
        lon = graph.nodes[node]['x']
        route_coords.append([lat, lon])

    return {"route": route_coords}

from traffic.traffic_store import traffic_db


@app.get("/traffic")
def traffic():

    roads = []

    for road, value in traffic_db.items():

        start, end = road.split("-")

        start = int(start)
        end = int(end)

        lat1 = graph.nodes[start]['y']
        lon1 = graph.nodes[start]['x']

        lat2 = graph.nodes[end]['y']
        lon2 = graph.nodes[end]['x']

        roads.append({
            "coords":[[lat1,lon1],[lat2,lon2]],
            "traffic":value
        })

    return {"roads":roads}