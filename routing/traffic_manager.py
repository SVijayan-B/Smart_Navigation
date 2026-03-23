from traffic.traffic_store import get_route_average


def compute_edge_weight(base_weight: float, traffic_score: float) -> float:
    score = max(0.0, min(1.0, float(traffic_score)))
    return float(base_weight) / (score + 0.1)


def get_route_traffic_score(route_id: str) -> float:
    return get_route_average(route_id)
