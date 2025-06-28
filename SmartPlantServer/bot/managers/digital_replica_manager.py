"""
bot/managers/digital_replica_manager.py manages the functions that create, update and visualize the digital twin
"""

from db import digital_replica_collection
from bot.utils import is_valid


# Updates or creates the digital replica for a plant using the latest data.
def set_digital_replica(timestamp, new_data, plant_entry):
    # Thresholds from the plant configuration
    temp_th = plant_entry["temperature_range"]
    min_temp = temp_th[0]
    max_temp = temp_th[1]
    humidity_air_th = plant_entry["humidity_threshold"]
    soil_moisture_th = plant_entry["soil_threshold"]

    temperature = new_data["temperature_value"]
    humidity = new_data["humidity_value"]

    alerts = []
    status = "Healthy"

    valid_temp = is_valid(temperature)
    valid_humidity = is_valid(humidity)

    # Evaluate conditions
    if new_data["soil_moisture_value"] < soil_moisture_th:
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

    if new_data["need_water"] and not new_data["is_irrigated"]:
        status = "The plant needs water"

    if not new_data["need_water"] and new_data["is_irrigated"]:
        status = "Water excess"

    # Construct the replica format
    dr = {
        "timestamp": timestamp,
        **new_data,
        **plant_entry,
        "status": status,
        "alerts": alerts
    }

    return dr


# Retrieves a digital replica document from MongoDB by chat_id and plant_name.
def get_digital_replica(chat_id, plant_name):
    query = {
        "chat_id": chat_id,
        "plant_name": plant_name
    }

    result = digital_replica_collection.find_one(query)

    if not result:
        return None

    return result


# Modifies the digital replica when the user uses /modify_plant
def modify_digital_replica(chat_id, old_name, new_name, soil_th, temp_range, humidity_th):
    old_plant = digital_replica_collection.find_one({
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

    digital_replica_collection.update_one(query, {"$set": new_twin})

    return True, "✅ Digital Twin updated!"
