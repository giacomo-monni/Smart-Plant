
"""
 config.py si occupa di caricare le variabili d'ambiente come il token del bot telegram, l'url del webhook
 e l'uri del database mongodb.
"""

import os
from dotenv import load_dotenv

load_dotenv() # Carica le variabili dal file .env

# Token bot
BOT_TOKEN = os.getenv("BOT_TOKEN")

# URL/webhook
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# URI MongoDB server
MONGO_URI = os.getenv("MONGO_URI")

# URI Mosquitto broker
MQTT_URI = os.getenv("MQTT_URI")


