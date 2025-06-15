"""
app.py starts a Flask server to manage bidirectional communication between a Telegram bot and IoT devices using MQTT.
- It receives updates from the Telegram bot via a webhook.
- It receives data from smart pots via MQTT and stores it in MongoDB.
- It sends notifications to the user via Telegram with the received data.
- It also handles sending configuration parameters to the pot when it's ready.
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
import logging

# === Logging setup ===
# Avoid the verbosity of the MongoDB connection
logging.getLogger("pymongo").setLevel(logging.WARNING)
logging.getLogger("pymongo.monitoring").setLevel(logging.WARNING)
logging.getLogger("pymongo.pool").setLevel(logging.WARNING)
logging.getLogger("pymongo.topology").setLevel(logging.WARNING)

# Configure the logging generating and using the file app.log
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("./logs/app.log", mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])  # Webhook for communication from Telegram to the server
def webhook():
    update = request.get_json()
    logging.debug(f"Received update from Telegram: {update}")

    response = handle_update(update)  # Manages the response for a given Telegram request
    logging.debug(f"Generated response: {response}")

    if response:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/{response.pop('method')}"
        res = requests.post(url, json=response)  # Sends back the response to the user (through the Telegram bot)
        logging.info(f"Response sent to Telegram: {res.status_code}")

    return jsonify(success=True)


@app.route("/", methods=["GET"])  # Endpoint to check if the server is active
def check_server():
    logging.info("GET request received on /")
    return "The server is up"


# === MongoDB Setup ===
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["smartplant"]
plants_col = db["plants"]
pots_col = db["pots"]
pot_data_col = db["pot_data"]


# === MQTT Message Handling ===
def on_message(client, userdata, msg):  # Receives a MQTT message
    topic = msg.topic
    payload = msg.payload.decode()
    logging.debug(f"MQTT message received - Topic: {topic}, Payload: {payload}")

    topic_parts = topic.split('/')
    if len(topic_parts) < 3:
        logging.warning("Invalid topic format")
        return

    _, pot_id, subtopic = topic_parts

    if subtopic == "data":  # Checks if the subtopic is data (used when receive data from a Node)
        try:
            data = json.loads(payload)
            pot = pots_col.find_one({"pot_id": pot_id})
            if not pot:  # Checks if the pot_id of the Node exists
                logging.warning(f"Pot {pot_id} not found.")
                return

            if not pot["used"]:  # Checks if that pot_id is already used
                logging.info("Pot is not registered to any user")
                return

            # Extracts the data obtain by the Node message
            plant = plants_col.find_one({"pot_id": pot_id})
            plant_name = plant["plant_name"]
            light_value = data.get("light_value")

            # Generate a timestamp
            timestamp = datetime.utcnow()
            timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

            # Maps the corresponding light values received
            if light_value < 300:
                light_map = "low"
            elif 300 <= light_value < 700:
                light_map = "medium"
            else:
                light_map = "high"

            # Generates a new entry to save the Node data in the database
            user_id = pot["user_id"]
            pot_data_entry = {
                "pot_id": pot_id,
                "plant_name": plant_name,
                "timestamp": timestamp,
                "light_value": data.get("light_value"),
                "humidity_value": data.get("humidity_value"),
                "temperature_value": data.get("temperature_value"),
                "soil_moisture_value": data.get("soil_moisture"),
                "need_water": data.get("need_water"),
                "is_irrigated": data.get("is_irrigated"),
                "user_id": user_id
            }

            pot_data_col.insert_one(pot_data_entry)
            logging.info(f"Data saved for pot {pot_id}")

            # === Send message to Telegram ===
            message = (
                f"🌱 Data received for pot `{pot_id}`:\n"
                f"🌱 Associated plant: `{plant_name}`\n"
                f"📅 Date: `{timestamp_str}`\n"
                f"📡 Light: {data.get('light_value')} lux ({light_map})\n"
                f"💧 Air Humidity: {data.get('humidity_value')}%\n"
                f"🌡️ Temperature: {data.get('temperature_value')}°C\n"
                f"🌍 Soil Moisture: {data.get('soil_moisture_value')}%\n"
                f"❓ Needed irrigation? {data.get('need_water')}\n"
                f"✅ Was it irrigated? {data.get('is_irrigated')}\n"
            )

            telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            res = requests.post(telegram_url, json={
                "chat_id": user_id,
                "text": message,
                "parse_mode": "Markdown"
            })
            logging.info(f"Telegram message sent to user {user_id}: {res.status_code}")

        except Exception as e:
            logging.error(f"Error parsing data for pot {pot_id}: {e}")

    elif subtopic == "ready":  # This subtopic is used when the Node is ready to receive the thresholds information
        try:
            plant = plants_col.find_one({"pot_id": pot_id})
            if not plant:
                logging.warning(f"No plant found for pot {pot_id}")
                return

            params = {  # Thresholds data required by the Node
                "action": "save_parameters",
                "soil_threshold": plant.get("soil_threshold"),
                "temperature_range": plant.get("temperature_range"),
                "humidity_threshold": plant.get("humidity_threshold")
            }
            client.publish(f"smartplant/{pot_id}/cmd", json.dumps(params))
            logging.info(f"Parameters sent to pot {pot_id}: {params}")
        except Exception as e:
            logging.error(f"Error sending parameters to pot {pot_id}: {e}")


client.on_message = on_message


def start_mqtt():  # Starts the MQTT connection and subscriptions
    try:
        logging.info("Connecting to MQTT broker...")
        client.connect(MQTT_URI, 1883, 60)
        client.subscribe("smartplant/+/data")  # The + is a wildcard, so accept the message for every smart pot
        client.subscribe("smartplant/+/ready")
        logging.info("Subscribed to MQTT topics.")
        client.loop_forever()
    except Exception as e:
        logging.critical(f"Failed to start MQTT client: {e}")


mqtt_thread = threading.Thread(target=start_mqtt)  # Necessary to run MQTT in a different thread
mqtt_thread.daemon = True  # Terminates with Flask if process is closed
mqtt_thread.start()  # The thread is useful to run Flask together with MQTT.

if __name__ == "__main__":
    logging.info("Starting Flask server...")
    app.run(debug=True)
