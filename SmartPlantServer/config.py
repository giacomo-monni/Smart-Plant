"""
config.py is responsible for loading environment variables such as the Telegram bot token,
the webhook URL, and the MongoDB connection URI.
"""

import os
from dotenv import load_dotenv

# Load environment variables from a .env file into the process environment
load_dotenv()

# Telegram bot token used for authentication with the Telegram API
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Webhook URL used to receive updates from Telegram
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# MongoDB connection URI to connect to the MongoDB database
MONGO_URI = os.getenv("MONGO_URI")

# MQTT broker URI for connecting to the Mosquitto MQTT server
MQTT_URI = os.getenv("MQTT_URI")
