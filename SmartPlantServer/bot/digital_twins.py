"""
bot/digital_twins.py manages the functions that create, update and visualize the digital twin
"""

from pymongo import MongoClient
from config import MONGO_URI
from bot.handlers.utils import human_delta, is_valid
from datetime import datetime
import math

client = MongoClient(MONGO_URI)
db = client["smartplant"]
digital_twins = db["digital_twins"]


# Updates or creates the digital twin for a plant using the latest data.
def update_digital_twin(last_data, plant, pot_id, chat_id):
    # Thresholds from the plant configuration
    temp_th = plant.get("temperature_range")
    min_temp = temp_th[0]
    max_temp = temp_th[1]
    humidity_air_th = plant.get("humidity_threshold")
    soil_moisture_th = plant.get("soil_threshold")

    temperature = last_data["temperature_value"]
    humidity = last_data["humidity_value"]

    alerts = []
    status = "Healthy"

    valid_temp = is_valid(temperature)
    valid_humidity = is_valid(humidity)

    # Evaluate conditions
    if last_data["soil_moisture_value"] < soil_moisture_th:
        alerts.append("Soil moisture out of range")
        status = "Dry"

    if valid_temp:
        if temperature < min_temp:
            alerts.append("Temperature below minimum threshold")
            status = "Cold"
        elif temperature > max_temp:
            alerts.append("Temperature above maximum threshold")
            status = "Hot"
    else:
        alerts.append("Possible malfunction in temperature and humidity sensor")
        temperature = "Unknown"

    if valid_humidity:
        if humidity < humidity_air_th:
            alerts.append("Humidity out of range")
    else:
        if "Possible malfunction in temperature and humidity sensor" not in alerts:
            alerts.append("Possible malfunction in temperature and humidity sensor")
        humidity = "Unknown"

    if last_data["need_water"] and not last_data["is_irrigated"]:
        status = "The plant needs water"

    if not last_data["need_water"] and last_data["is_irrigated"]:
        status = "Water excess"

    # Construct the twin document
    twin = {
        "timestamp": last_data["timestamp"],
        "pot_id": pot_id,
        "chat_id": chat_id,
        "plant_name": plant["plant_name"],
        "soil_moisture_value": last_data["soil_moisture_value"],
        "temperature_value": temperature,
        "humidity_value": humidity,
        "need_water": last_data["need_water"],
        "is_irrigated": last_data["is_irrigated"],
        "status": status,
        "alerts": alerts
    }

    return twin


# Formats the status report message for a plant digital twin.
def format_plant_status_report(twin):
    now = datetime.utcnow()
    delta = now - twin["timestamp"]

    msg = (
        f"🌿 *Plant Status Report — {twin['plant_name']}*\n\n"
        f"🆔 Pot ID: `{twin['pot_id']}`\n"
        f"📅 Timestamp: {twin['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"⏱️ Last update: {human_delta(delta)}\n\n"
        f"🌡️ Temperature: {twin['temperature_value']}°C\n"
        f"💧 Air Humidity: {twin['humidity_value']}%\n"
        f"🌾 Soil Moisture: {twin['soil_moisture_value']}%\n"
        f"🚿 Need Water: {'Yes' if twin['need_water'] else 'No'}\n"
        f"💦 Irrigated: {'Yes' if twin['is_irrigated'] else 'No'}\n\n"
        f"📌 *Status:* {twin['status']}\n"
    )

    if twin.get("alerts"):
        msg += "\n⚠️ *Alerts:*\n"
        for alert in twin["alerts"]:
            msg += f"• {alert}\n"

    return msg


# Retrieves a digital twin document from MongoDB by chat_id and plant_name.
def get_digital_twin(chat_id, plant_name):
    query = {
        "chat_id": chat_id,
        "plant_name": plant_name
    }

    result = digital_twins.find_one(query)

    if not result:
        return None

    return result


def modify_digital_twin(chat_id, old_name, new_name, soil_th, temp_range, humidity_th):
    old_plant = digital_twins.find_one({
        "chat_id": int(chat_id),
        "plant_name": old_name
    })

    if not old_plant:
        return False, "❌ You don't own any plant with that name."

    min_temp = temp_range[0]
    max_temp = temp_range[1]

    valid_temp = old_plant["temperature_value"]
    valid_humidity = old_plant["humidity_value"]

    alerts = []
    status = "Healthy"

    if old_plant["soil_moisture_value"] < float(soil_th):
        alerts.append("Soil moisture out of range")
        status = "Dry"

    if valid_temp:
        if old_plant["temperature_value"] < float(min_temp):
            alerts.append("Temperature below minimum threshold")
            status = "Cold"
        elif old_plant["temperature_value"] > float(max_temp):
            alerts.append("Temperature above maximum threshold")
            status = "Hot"
    else:
        alerts.append("Possible malfunction in temperature and humidity sensor")

    if valid_humidity:
        if old_plant["humidity_value"] < float(humidity_th):
            alerts.append("Humidity out of range")
    else:
        if "Possible malfunction in temperature and humidity sensor" not in alerts:
            alerts.append("Possible malfunction in temperature and humidity sensor")

    new_twin = {
        "plant_name": new_name,
        "status": status,
        "alerts": alerts
    }

    query = {
        "chat_id": chat_id,
        "plant_name": old_name
    }

    digital_twins.update_one(query, {"$set": new_twin})

    return True, "✅ Digital Twin updated!"
