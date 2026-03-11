import paho.mqtt.client as mqtt
import json

from routing.traffic_manager import update_traffic


def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")

    client.subscribe("traffic/update")


def on_message(client, userdata, msg):

    try:
        payload = json.loads(msg.payload.decode())

        road = payload["road"]
        intensity = payload["traffic"]

        update_traffic(road, intensity)

        print(f"Traffic updated → Road: {road} | Intensity: {intensity}")

    except Exception as e:
        print("Error processing message:", e)


client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883)

print("Waiting for traffic updates...")

client.loop_forever()