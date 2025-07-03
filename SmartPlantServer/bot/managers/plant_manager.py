
"""
bot/managers/plant_manager.py handles plant management on the database side, such as inserting a plant into the database,
deleting it, and modifying the parameters of the plants owned by a user.
"""

from db import plants_profile_collection, digital_replica_collection, pot_data_collection
from .pot_manager import is_valid_pot, mark_pot_as_used, free_pot


# Adds a plant in the database
def add_plant(chat_id, pot_id, plant_name, soil_threshold, temperature_range, humidity_threshold):
    valid, msg = is_valid_pot(pot_id)  # verifies if pot already exists and if it's currently used
    if not valid:
        return False, msg

    existing_name = plants_profile_collection.find_one({
        "chat_id": chat_id,
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

    plants_profile_collection.insert_one({  # inserts the plant and its user and pot in the database
        "chat_id": chat_id,
        "pot_id": pot_id,
        "plant_name": plant_name,
        "soil_threshold": soil_threshold,
        "temperature_range": temperature_range,
        "humidity_threshold": humidity_threshold
    })

    mark_pot_as_used(pot_id, chat_id)  # Marks in the database that the pot is now in use and by whom it is being used.

    return True, "✅ Plant successfully added."


def get_user_plants(chat_id): # Returns all plants associated with a specific user.
    return list(plants_profile_collection.find({"chat_id": chat_id}))


def remove_plant(chat_id, plant_name): # Removes a user's plant and frees the associated pot.
    plant = plants_profile_collection.find_one({
        "chat_id": chat_id,
        "plant_name": plant_name
    })

    if not plant: # Checks if the plant does not exist.
        return False

    pot_id = plant["pot_id"]

    plants_profile_collection.delete_one({ # deletes the plant from the database
        "chat_id": chat_id,
        "plant_name": plant_name
    })

    free_pot(pot_id)  # marks the pot as free

    pot_data_collection.delete_many({"pot_id": pot_id})

    digital_replica_collection.delete_one({  # deletes the digital replica
        "chat_id": chat_id,
        "plant_name": plant_name
    })

    return True


