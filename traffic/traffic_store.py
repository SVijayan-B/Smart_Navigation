traffic_db = {}

def update_traffic(road_id, value):

    traffic_db[road_id] = value


def get_traffic(road_id):

    return traffic_db.get(road_id, 0)