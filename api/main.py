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