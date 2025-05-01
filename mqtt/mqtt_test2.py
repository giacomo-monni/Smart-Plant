""""
import paho.mqtt.client as mqtt
import time
import datetime

BROKER = "broker.hivemq.com" #inserire mosquitto uri.


def on_message(client, userdata, msg):
    print(f"[SERVER] Stato ricevuto da {msg.topic}: {msg.payload.decode()}")
    # Qui puoi inviare notifiche Telegram all'utente corretto
    topic_parts = msg.topic.split('/')
    chat_id = topic_parts[0]
    plant_id = topic_parts[1]


def send_cmd(chat_id, pot_id, cmd): # collegare a un cmd telegram
    topic = f"smartplant/{chat_id}/{pot_id}/command"
    client.publish(topic, cmd)


client = mqtt.Client()
client.on_message = on_message
client.connect(BROKER, 1883, 60)

client.subscribe("smartplant/+/+/data")  # Wildcard! Si iscrive a TUTTI gli status

client.loop_start()
"""




