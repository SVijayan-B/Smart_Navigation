import json
import paho.mqtt.client as mqtt

from ml.predictor import predict_traffic
from traffic.traffic_store import update_traffic


def on_connect(client, userdata, flags, rc):

    print("Connected to MQTT broker")

    client.subscribe("traffic/sensors")


def on_message(client, userdata, msg):

    try:

        data = json.loads(msg.payload.decode())

        road = data["road"]

        traffic = predict_traffic(data)

        update_traffic(road, traffic)

        print(
            f"Traffic predicted → Road: {road} | Intensity: {traffic}"
        )

    except Exception as e:

        print("Error processing sensor message:", e)


client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883)

print("Listening for sensor data...")

client.loop_forever()