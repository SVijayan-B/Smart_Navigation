import networkx as nx
from routing.traffic_manager import traffic_data


def compute_weight(distance, traffic):

    # traffic multiplier
    traffic_factor = 1 + (traffic * 5)

    return distance * traffic_factor


def best_route(G, start, end):

    for u, v, k, data in G.edges(keys=True, data=True):

        road = f"{u}-{v}"

        traffic = traffic_data.get(road, 0)

        distance = data.get("length", 1)

        data["weight"] = compute_weight(distance, traffic)

    route = nx.shortest_path(
        G,
        start,
        end,
        weight="weight"
    )

    return route