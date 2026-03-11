import paho.mqtt.client as mqtt
import json

from routing.traffic_manager import update_traffic


def on_message(client, userdata, msg):

    payload = json.loads(msg.payload.decode())

    road = payload["road"]
    intensity = payload["traffic"]

    update_traffic(road, intensity)

    print("Traffic updated:", road, intensity)


client = mqtt.Client()

client.on_message = on_message

client.connect("localhost", 1883)

client.subscribe("traffic/update")

client.loop_forever()