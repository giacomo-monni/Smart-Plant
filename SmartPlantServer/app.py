
"""
app.py è incaricato di avviare il server e gestire la comunicazione tra bot telegram e server, inoltre avvia il client MQTT.
"""

from flask import Flask, request, jsonify
from config import BOT_TOKEN, MQTT_URI, MONGO_URI
from bot.handler import handle_update
import requests
import threading
import json
from pymongo import MongoClient
from datetime import datetime
from mqtt_client import client

app = Flask(__name__)

@app.route("/webhook", methods=["POST"]) # Webhook incaricata della connessione con Telegram
def webhook():
    update = request.get_json() # legge le risposte di telegram (sono in formato json)
    response = handle_update(update) # interpreta la risposta ottenuta eseguendo il metodo dedicato

    if response: # se l'operazione esiste ed è andata a buon fine
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/{response.pop('method')}"
        requests.post(url, json=response) # mandiamo la risposta al bot telegram

    return jsonify(success=True)


@app.route("/", methods=["GET"]) # Se visiti l'URL del server ti mostra se è attivo.
def check_server():
    return "The server is up"


# === MongoDB Setup ===
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["smartplant"]
plants_col = db["plants"]
pots_col = db["pots"]
pot_data_col = db["pot_data"]


# === MQTT Logic ===
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    topic_parts = topic.split('/')
    if len(topic_parts) < 3:
        print("Invalid topic format")
        return

    _, pot_id, subtopic = topic_parts

    if subtopic == "data":
        try:
            data = json.loads(payload)
            pot = pots_col.find_one({"pot_id": pot_id})
            if not pot:
                print(f"Pot {pot_id} not found.")
                return

            if not pot["used"]:
                print("Pot non registrato da nessuno")
                return

            plant = plants_col.find_one({"pot_id": pot_id})
            plant_name = plant["plant_name"]
            light_value = data.get("light_value")

            timestamp = datetime.utcnow() # inserisco il timestamp dal server, non sarà accurato.
            timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

            if light_value < 300:
                light_map = "poco"
            elif 300 <= light_value < 700:
                light_map = "media"
            else:
                light_map = "molto"

            user_id = pot["user_id"]
            pot_data_entry = {
                "pot_id": pot_id,
                "plant_name": plant_name,
                "timestamp": timestamp,
                "light_value": data.get("light_value"),
                "humidity_value": data.get("humidity_value"),
                "temperature_value": data.get("temperature_value"),
                "soil_moisture_value": data.get("soil_moisture"),
                "must_be_irrigated": data.get("must_be_irrigated"), # nel node manca questo
                "is_irrigated": data.get("is_irrigated"),
                "user_id": user_id
            }
            pot_data_col.insert_one(pot_data_entry)
            print(f"Data saved for {pot_id}")

            # === INVIO MESSAGGIO A TELEGRAM ===
            message = (
                f"🌱 Dati ricevuti per il pot `{pot_id}`:\n"
                f"🌱 Pianta associata: `{plant_name}`:\n"
                f"🌱 Data: `{timestamp_str}`:\n"
                f"📡 Luce: {data.get('light_value')} lux ({light_map})\n"
                f"💧 Umidità Aria: {data.get('humidity_value')}%\n"
                f"🌡️ Temperatura: {data.get('temperature_value')}°C\n"
                f"🌍 Umidità Suolo: {data.get('soil_moisture_value')}%\n"
                f"🌍 Richiedeva irrigazione? {data.get('must_be_irrigated')}\n"
                f"🌍 E' stato irrigato? {data.get('is_irrigated')}\n"
            )

            telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            requests.post(telegram_url, json={
                "chat_id": user_id,
                "text": message,
                "parse_mode": "Markdown"
            })

        except Exception as e:
            print(f"Error parsing data: {e}")

    elif subtopic == "ready":
        try:
            plant = plants_col.find_one({"pot_id": pot_id})
            if not plant:
                print(f"No plant for {pot_id}")
                return
            params = {
                "action": "save_parameters",
                "soil_threshold": plant.get("soil_threshold"),
                "temperature_range": plant.get("temperature_range"),
                "humidity_threshold": plant.get("humidity_threshold")
            }
            client.publish(f"smartplant/{pot_id}/cmd", json.dumps(params))
            print(f"Parameters sent to {pot_id}")
        except Exception as e:
            print(f"Error sending parameters: {e}")


client.on_message = on_message


def start_mqtt():
    client.connect(MQTT_URI, 1883, 60)
    client.subscribe("smartplant/+/data")
    client.subscribe("smartplant/+/ready")
    client.loop_forever()


mqtt_thread = threading.Thread(target=start_mqtt)
mqtt_thread.daemon = True  # termina insieme a Flask se chiudi il processo
mqtt_thread.start()

if __name__ == "__main__":
    app.run(debug=True)

