import paho.mqtt.client as mqtt
import json
import random
import time

client = mqtt.Client()

client.connect("localhost",1883)

roads = ["A-B","B-C","C-D","D-E"]

while True:

    payload = {

        "road": random.choice(roads),

        "traffic": random.randint(0,3)

    }

    client.publish(
        "traffic/update",
        json.dumps(payload)
    )

    time.sleep(2)