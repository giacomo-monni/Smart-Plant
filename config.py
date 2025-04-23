import os
from dotenv import load_dotenv

load_dotenv() # Carica le variabili dal file .env

# Token bot
BOT_TOKEN = os.getenv("BOT_TOKEN")

# URL/webhook
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# URI MongoDB server
MONGO_URI = os.getenv("MONGO_URI")








