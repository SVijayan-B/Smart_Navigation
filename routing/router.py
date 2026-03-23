import networkx as nx
from routing.traffic_manager import compute_edge_weight, get_route_traffic_score


def best_route(G, start, end):
    for u, v, k, data in G.edges(keys=True, data=True):
        route_id = f"{u}-{v}"
        traffic_score = get_route_traffic_score(route_id)
        base_weight = data.get("length", 1.0)
        data["weight"] = compute_edge_weight(base_weight, traffic_score)

    node_path = nx.shortest_path(G, start, end, weight="weight")
    return [[G.nodes[node]["y"], G.nodes[node]["x"]] for node in node_path]
