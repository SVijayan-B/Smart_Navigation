import random
import json
import time
import paho.mqtt.client as mqtt

client = mqtt.Client()

client.connect("localhost", 1883)

roads = [
"A-B",
"B-C",
"C-D",
"D-E",
"E-F"
]

while True:

    data = {
        "road": random.choice(roads),
        "traffic": random.uniform(0, 1)
    }

    client.publish(
        "traffic/update",
        json.dumps(data)
    )

    print("Traffic sent:", data)

    time.sleep(2)