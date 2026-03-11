import osmnx as ox

def load_city():

    city = "Chennai, India"

    graph = ox.graph_from_place(
        city,
        network_type="drive"
    )

    return graph