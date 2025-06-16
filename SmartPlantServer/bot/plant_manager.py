
"""
bot/plant_manager.py handles plant management on the database side, such as inserting a plant into the database,
deleting it, and modifying the parameters of the plants owned by a user.
"""

from pymongo import MongoClient
from config import MONGO_URI
from .pot_manager import is_valid_pot, mark_pot_as_used, free_pot
from datetime import datetime, timedelta

client = MongoClient(MONGO_URI)
db = client.smartplant
plants = db.plants


# Adds a plant in the database
def add_plant(user_id, pot_id, plant_name, soil_threshold, temperature_range, humidity_threshold):
    valid, msg = is_valid_pot(pot_id)  # verifies if pot already exists and if it's currently used
    if not valid:
        return False, msg

    existing_name = plants.find_one({
        "user_id": user_id,
        "plant_name": plant_name
    })
    if existing_name:  # verifies if a plant with the same name already exists
        return False, "❌ You already have a plant with this name."

    try:
        soil_threshold = abs(int(soil_threshold))
        temperature_range = [abs(int(temperature_range[0])), abs(int(temperature_range[1]))]
        humidity_threshold = abs(int(humidity_threshold))
    except ValueError:
        return False, "❌ You have entered invalid data."

    plants.insert_one({  # inserts the plant and its user and pot in the database
        "user_id": user_id,
        "pot_id": pot_id,
        "plant_name": plant_name,
        "soil_threshold": soil_threshold,
        "temperature_range": temperature_range,
        "humidity_threshold": humidity_threshold
    })

    mark_pot_as_used(pot_id, user_id)  # Marks in the database that the pot is now in use and by whom it is being used.

    return True, "✅ Plant successfully added."


def get_user_plants(user_id): # Returns all plants associated with a specific user.
    return list(plants.find({"user_id": user_id}))


def remove_plant(user_id, plant_name): # Removes a user's plant and frees the associated pot.
    plant = plants.find_one({
        "user_id": user_id,
        "plant_name": plant_name
    })

    if not plant: # Checks if the plant does not exist.
        return False

    pot_id = plant["pot_id"]

    plants.delete_one({ # deletes the plant from the database
        "user_id": user_id,
        "plant_name": plant_name
    })

    free_pot(pot_id) # marks the pot as free

    db.pot_data.delete_many({"pot_id": pot_id})

    return True


def info_plant(user_id, plant_name): # queries the database to get plant information
    existing_plant = plants.find_one({
        "user_id": user_id,
        "plant_name": plant_name
    })
    existing_plant.pop("_id", None)  # Removes the _id field if it exists
    existing_plant.pop("user_id", None)
    righe = [f"{chiave}: {valore}" for chiave, valore in existing_plant.items()]
    stringa_finale = "\n".join(righe)

    return stringa_finale


def modify_plant(user_id, old_name, new_name, soil, temp, humidity): # modifies the plant
    old_plant = plants.find_one({
        "user_id": user_id,
        "plant_name": old_name
    })

    if not old_plant: # Checks if the plant does not exist
        return False, "❌ You don't own any plant with that name."

    duplicate = plants.find_one({
        "user_id": user_id,
        "plant_name": new_name
    })

    if duplicate and old_name != new_name: # Checks if a plant with the new name already exists
        return False, "❌ You already have a plant with this name. Please choose a different name."

    plants.update_one( # Modifies the plant's data.
        {"user_id": user_id, "plant_name": old_name},
        {"$set": {
            "plant_name": new_name,
            "soil_threshold": soil,
            "temperature_range": temp,
            "humidity_threshold": humidity}}
    )

    return True, "✅ Plant name updated!"


def get_plant_statistics(pot_id): # calculates statistic information using the plant's data stored in the database
    from statistics import mean
    pot_data_col = db["pot_data"]

    today = datetime.utcnow()
    week_ago = today - timedelta(days=7)

    try:
        # Fetches all data from the past week for that pot_id.
        records = list(pot_data_col.find({
            "pot_id": pot_id,
            "timestamp": {"$gte": week_ago, "$lte": today}
        }))

        if not records:
            return None

        temperatures = [r.get("temperature_value") for r in records if r.get("temperature_value") is not None]
        humidities = [r.get("humidity_value") for r in records if r.get("humidity_value") is not None]
        lights = [r.get("light_value") for r in records if r.get("light_value") is not None]
        soil_moistures = [r.get("soil_moisture_value") for r in records if r.get("soil_moisture_value") is not None]

        irrigations = [r for r in records if r.get("is_irrigated") is True]
        missed_irrigations = [r for r in records if r.get("must_be_irrigated") is True and r.get("is_irrigated") is False]

        plant = plants.find_one({"pot_id": pot_id})
        ideal_conditions = 0

        for r in records:
            try:
                temp = r.get("temperature_value")
                hum = r.get("humidity_value")
                soil = r.get("soil_moisture_value")
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
            'avg_temperature': round(mean(temperatures), 2) if temperatures else None,
            'max_temperature': max(temperatures) if temperatures else None,
            'min_temperature': min(temperatures) if temperatures else None,
            'avg_humidity': round(mean(humidities), 2) if humidities else None,
            'min_humidity': min(humidities) if humidities else None,
            'avg_light': round(mean(lights), 2) if lights else None,
            'avg_soil_moisture': round(mean(soil_moistures), 2) if soil_moistures else None,
            'irrigations_count': len(irrigations),
            'missed_irrigations_percentage': round(len(missed_irrigations) / total_records * 100, 2) if total_records else 0,
            'ideal_conditions_percentage': round(ideal_conditions / total_records * 100, 2) if total_records else 0
        }

    except Exception as e:
        print(f"Error retrieving statistics: {e}")
        return None

