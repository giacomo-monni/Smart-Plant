"""
mqtt_client.py creates an MQTT client instance that will be used to connect and interact with the MQTT broker.
"""

import paho.mqtt.client as mqtt
from config import MQTT_URI
import threading

client = mqtt.Client()


def set_on_message(on_message):
    client.on_message = on_message


# Starts the MQTT connection and subscriptions
def start_mqtt():
    client.connect(MQTT_URI, 1883, 60)
    client.subscribe("smartplant/+/data")  # The + is a wildcard, so accepts the message for every smart pot
    client.subscribe("smartplant/+/ready")
    client.loop_forever()


# Starts MQTT in a different thread
def start_mqtt_thread():
    mqtt_thread = threading.Thread(target=start_mqtt)  # Necessary to run MQTT in a different thread
    mqtt_thread.daemon = True  # Terminates with Flask if process is closed
    mqtt_thread.start()  # The thread is useful to run Flask together with MQTT.
