"""
app.py starts a Flask server to manage bidirectional communication between a Telegram bot and IoT devices using MQTT.
- It receives updates from the Telegram bot via a webhook.
- It receives data from smart pots via MQTT and stores it in MongoDB.
- It sends notifications to the user via Telegram with the received data.
- It also handles sending configuration parameters to the pot when it's ready.
"""

from flask import Flask, request, jsonify
from datetime import datetime
import requests
import json
import logging
from config import BOT_TOKEN
from db import plants_profile_collection, pots_collection, pot_data_collection, digital_replica_collection
from bot.main_handler import handle_update
from mqtt_client import start_mqtt_thread, set_on_message
from bot.managers.digital_replica_manager import set_digital_replica
from services.service import send_plant_status_message

app = Flask(__name__)

# Configure the logging generating and using the file app.log
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("./logs/server.log", mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Avoid the verbosity of the MongoDB connection
for logger_name in [
    "pymongo",
    "pymongo.monitoring",
    "pymongo.pool",
    "pymongo.topology",
    "pymongo.periodic",
    "pymongo.server",
    "pymongo.heartbeat",
]:
    logging.getLogger(logger_name).setLevel(logging.WARNING)


@app.route("/webhook", methods=["POST"])  # Webhook for communication from Telegram to the server
def webhook():
    update = request.get_json()
    logging.debug(f"Received update from Telegram")

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


# === MQTT Message Handling ===
def on_message(client, user, msg):  # Receives a MQTT message
    topic = msg.topic
    payload = msg.payload.decode()
    logging.debug(f"MQTT message received - Topic: {topic}, Payload: {payload}")

    topic_parts = topic.split('/')
    if len(topic_parts) != 3:
        logging.warning("Invalid topic format")
        return

    _, pot_id, subtopic = topic_parts
    node_data = {}

    if subtopic == "data":  # Checks if the subtopic is data (used when receive data from a Node)
        try:
            node_data = json.loads(payload)
        except Exception as data_error:
            logging.error(f"Error parsing data for pot {pot_id}: {data_error}")

        if len(node_data) != 4:
            logging.warning("Invalid received payload format")
            return

        pot_entry = pots_collection.find_one({"pot_id": pot_id})
        if not pot_entry:  # Checks if the pot_id of the Node exists
            logging.warning(f"Pot {pot_id} not found.")
            return

        # Checks if that data received comes an unregistered pot (the user should register the plant first)
        if not pot_entry["used"]:
            logging.info("Pot is not registered to any user")
            return

        # Extracts the data obtained from the Node message
        plant_entry = plants_profile_collection.find_one({"pot_id": pot_id})

        # Generate a timestamp
        timestamp = datetime.utcnow()

        # Generates a new entry to save the Node data in the database
        pot_data_entry = {
            "timestamp": timestamp,
            "pot_id": plant_entry["pot_id"],
            "chat_id": plant_entry["chat_id"],
            "plant_name": plant_entry["plant_name"],
            **node_data
        }

        pot_data_collection.insert_one(pot_data_entry)  # saves the data in the database (pot_data collection)

        # builds the digital replica
        dr = set_digital_replica(timestamp, node_data, plant_entry)

        # Update or insert the digital replica
        query = {
            "chat_id": plant_entry["chat_id"],
            "pot_id": pot_id,
            "plant_name": plant_entry["plant_name"]
        }

        # saves the digital replicas in the database (digital_replicas collection)
        digital_replica_collection.update_one(query, {"$set": dr}, upsert=True)

        logging.info(f"Data saved for pot {pot_id}")

        # Sends message to Telegram
        res = send_plant_status_message(dr, plant_entry["chat_id"])

        chat_id = plant_entry["chat_id"]
        logging.info(f"Telegram message sent to user {chat_id}: {res.status_code}")

    # This subtopic is used when the Node is ready to receive the thresholds information
    elif subtopic == "ready":
        try:
            plant_entry = plants_profile_collection.find_one({"pot_id": pot_id})
            if not plant_entry:
                logging.warning(f"No plant found for pot {pot_id}")
                return

            params = {  # Thresholds data required by the Node
                "action": "save_parameters",
                "soil_threshold": plant_entry["soil_threshold"],
                "temperature_range": plant_entry["temperature_range"],
                "humidity_threshold": plant_entry["humidity_threshold"]
            }

            client.publish(f"smartplant/{pot_id}/cmd", json.dumps(params))
            logging.info(f"Parameters sent to {pot_id}: {params}")
        except Exception as e:
            logging.error(f"Error sending parameters to pot {pot_id}: {e}")


# Starts MQTT
try:
    set_on_message(on_message)
    logging.info("Connecting to MQTT broker...")
    start_mqtt_thread()
    logging.info("Subscribed to MQTT topics.")
except Exception as mqtt_error:
    logging.critical(f"Failed to start MQTT client: {mqtt_error}")

if __name__ == "__main__":
    logging.info("Starting Flask server...")
    app.run(debug=True)
