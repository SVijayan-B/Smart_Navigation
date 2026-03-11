import paho.mqtt.client as mqtt
import json
import random
import time

client = mqtt.Client()

client.connect("BROKER_IP",1883)

road="12345-67890"

while True:

    sensor_data = {

        "road":road,

        "speed":random.uniform(10,60),

        "Ax":random.uniform(0,1),
        "Ay":random.uniform(0,1),
        "Az":random.uniform(0,1),

        "Gx":random.uniform(0,0.1),
        "Gy":random.uniform(0,0.1),
        "Gz":random.uniform(0,0.1),

        "front_distance":random.uniform(1,10),
        "back_distance":random.uniform(1,10),

        "jerk":random.uniform(0,1),

        "temperature":random.uniform(28,35),

        "humidity":random.uniform(50,80),

        "latitude":13.08,
        "longitude":80.27
    }

    client.publish(
        "traffic/sensors",
        json.dumps(sensor_data)
    )

    print("Sensor data sent")

    time.sleep(2)