traffic_data = {}

def update_traffic(road,intensity):

    traffic_data[road] = intensity

def get_traffic(road):

    return traffic_data.get(road,0)