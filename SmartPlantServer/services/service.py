"""
services/service.py contains all the services offered to the user for the management of their plants
"""

import requests
from config import BOT_TOKEN
from datetime import datetime, timedelta
from bot.utils import is_valid
from statistics import mean
from db import plants_profile_collection, pot_data_collection
from bot.utils import human_delta
from geopy.geocoders import Nominatim


def send_plant_status_message(dr, chat_id):  # sends the digital replica information
    msg = format_plant_status_report(dr)

    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(telegram_url, json={
        "chat_id": chat_id,
        "text": msg,
        "parse_mode": "Markdown"
    })

    return response


def info_plant(chat_id, plant_name): # queries the database to get plant information
    existing_plant = plants_profile_collection.find_one({
        "chat_id": chat_id,
        "plant_name": plant_name
    })
    existing_plant.pop("_id", None)  # Removes the _id field if it exists
    existing_plant.pop("chat_id", None)
    rows = [f"{chiave}: {valore}" for chiave, valore in existing_plant.items()]
    final_string = "\n".join(rows)

    return final_string


def modify_plant(chat_id, old_name, new_name, new_indoor, soil, soil_max, temp, humidity):  # modifies the plant
    old_plant = plants_profile_collection.find_one({
        "chat_id": chat_id,
        "plant_name": old_name
    })

    if not old_plant: # Checks if the plant does not exist
        return False, "❌ You don't own any plant with that name."

    duplicate = plants_profile_collection.find_one({
        "chat_id": chat_id,
        "plant_name": new_name
    })

    if duplicate and old_name != new_name: # Checks if a plant with the new name already exists
        return False, "❌ You already have a plant with this name. Please choose a different name."

    try:
        soil_threshold = abs(int(soil))
        soil_max = abs(int(soil_max))
        temperature_range = [abs(int(temp[0])), abs(int(temp[1]))]
        humidity_threshold = abs(int(humidity))
    except ValueError:
        return False, "❌ You have entered invalid data."

    plants_profile_collection.update_one( # Modifies the plant's data.
        {"chat_id": chat_id, "plant_name": old_name},
        {"$set": {
            "plant_name": new_name,
            "is_indoor": new_indoor,
            "soil_threshold": soil_threshold,
            "soil_max": soil_max,
            "temperature_range": temperature_range,
            "humidity_threshold": humidity_threshold}}
    )

    return True, "✅ Plant name updated!"


def get_plant_statistics(pot_id): # calculates statistic information using the plant's data stored in the database
    today = datetime.utcnow()
    week_ago = today - timedelta(days=7)

    try:
        # Fetches all data from the past week for that pot_id.
        records = list(pot_data_collection.find({
            "pot_id": pot_id,
            "timestamp": {"$gte": week_ago, "$lte": today}
        }))

        if not records:
            return None

        # Filter valid values only
        valid_temperatures = [r.get("temperature_value") for r in records if is_valid(r.get("temperature_value"))]
        valid_humidities = [r.get("humidity_value") for r in records if is_valid(r.get("humidity_value"))]
        valid_soil_moistures = [r.get("soil_moisture_value") for r in records if is_valid(r.get("soil_moisture_value"))]

        avg_temp = mean(valid_temperatures) if valid_temperatures else None
        avg_hum = mean(valid_humidities) if valid_humidities else None

        # Replace invalid temperature/humidity with the average
        temperatures = [
            r.get("temperature_value") if is_valid(r.get("temperature_value")) else avg_temp
            for r in records if avg_temp is not None
        ]

        humidities = [
            r.get("humidity_value") if is_valid(r.get("humidity_value")) else avg_hum
            for r in records if avg_hum is not None
        ]

        soil_moistures = valid_soil_moistures  # Keep only valid, no filling

        plant = plants_profile_collection.find_one({"pot_id": pot_id})
        ideal_conditions = 0

        for r in records:
            try:
                temp = r.get("temperature_value")
                hum = r.get("humidity_value")
                soil = r.get("soil_moisture_value")

                if is_valid(temp) and is_valid(hum) and is_valid(soil):
                    if (plant["temperature_range"][0] <= temp <= plant["temperature_range"][1] and
                            hum >= plant["humidity_threshold"] and
                            soil >= plant["soil_threshold"]):
                        ideal_conditions += 1
            except:
                continue

        total_records = len(records)

        return {
            'week_start': (today - timedelta(days=7)).strftime("%d/%m/%Y"),
            'week_end': today.strftime("%d/%m/%Y"),
            'avg_temperature': round(avg_temp, 2) if avg_temp is not None else None,
            'max_temperature': max(temperatures) if temperatures else None,
            'min_temperature': min(temperatures) if temperatures else None,
            'avg_humidity': round(avg_hum, 2) if avg_hum is not None else None,
            'min_humidity': min(humidities) if humidities else None,
            'avg_soil_moisture': round(mean(soil_moistures), 2) if soil_moistures else None,
            'ideal_conditions_percentage': round(ideal_conditions / total_records * 100, 2) if total_records else 0
        }

    except Exception as e:
        print(f"Error retrieving statistics: {e}")
        return None


# Formats the status report message for a plant digital replica.
def format_plant_status_report(dr):
    now = datetime.utcnow()
    delta = now - dr["timestamp"]

    msg = (
        f"🌿 *Plant Status Report — {dr['plant_name']}*\n\n"
        f"🆔 Pot ID: `{dr['pot_id']}`\n"
        f"📅 Timestamp: {dr['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"⏱️ Last update: {human_delta(delta)}\n\n"
        f"🌡️ Temperature: {dr['temperature_value']}°C\n"
        f"💧 Air Humidity: {dr['humidity_value']}%\n"
        f"🌾 Soil Moisture: {dr['soil_moisture_value']}%\n"
        f"🚿 Need Water: {'Yes' if dr['need_water'] else 'No'}\n"
        f"📌 *Status:* {dr['status']}\n\n"
        f"With thresholds:\n"
        f"Soil moisture = {dr['soil_threshold']}%\n"
        f"Soil moisture max = {dr['soil_max']}%\n"
        f"The plant was indoor: {dr['is_indoor']}\n"
        f"Temperature range (min, max) = ({dr['temperature_range']})°C\n"
        f"Humidity = {dr['humidity_threshold']}%\n"
    )

    if dr.get("alerts"):
        msg += "\n⚠️ *Alerts:*\n"
        for alert in dr["alerts"]:
            msg += f"• {alert}\n"

    return msg


# Formats the statistics report message
def format_plant_statistics_report(plant_name, stats):
    week_report = (
        f"🌱 Plant *{plant_name}* statistics for the past week:\n\n"
        f"📅 Week from {stats['week_start']} to {stats['week_end']}\n\n"
        f"📊 Average temperature: {stats['avg_temperature']}°C\n"
        f"📈 Maximum temperature: {stats['max_temperature']}°C\n"
        f"📉 Minimum temperature: {stats['min_temperature']}°C\n"
        f"💧 Average humidity: {stats['avg_humidity']}%\n"
        f"🌿 Minimum humidity: {stats['min_humidity']}%\n"
        f"🌾 Average soil moisture: {stats['avg_soil_moisture']}%\n\n"
        f"✅ All plant parameters remained within ideal limits for {stats['ideal_conditions_percentage']}% of the time."
    )

    return week_report


def will_it_rain(location: str) -> bool:
    # Convert location name to latitude and longitude using Nominatim (OpenStreetMap)
    geolocator = Nominatim(user_agent="weather-checker")
    loc = geolocator.geocode(location)
    if not loc:
        raise ValueError("Could not find location")

    lat, lon = loc.latitude, loc.longitude

    # Build the Open-Meteo API URL (no API key required)
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=precipitation_probability&timezone=auto"
    )

    # Request forecast data
    response = requests.get(url)
    data = response.json()

    # Get current time and the next 30-minute mark
    now = datetime.now()
    next_half_hour = now + timedelta(minutes=30)

    # Extract forecast times and precipitation probabilities
    times = data["hourly"]["time"]
    probs = data["hourly"]["precipitation_probability"]

    # Check if any forecasted time within the next 30 minutes has >30% chance of rain
    for t, prob in zip(times, probs):
        time_obj = datetime.fromisoformat(t)
        if now <= time_obj <= next_half_hour:
            if prob > 30:
                return True

    return False
