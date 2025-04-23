from pymongo import MongoClient
from config import MONGO_URI
from .pot_manager import is_valid_pot, mark_pot_as_used, free_pot

client = MongoClient(MONGO_URI)
db = client.smartplant
plants = db.plants


def add_plant(user_id, pot_id, plant_name): # aggiunge una pianta associata a un pot nel database
    valid, msg = is_valid_pot(pot_id) # verifica se il pot esiste e se sia già in uso
    if not valid:
        return False, msg

    existing_name = plants.find_one({
        "user_id": user_id,
        "plant_name": plant_name
    })
    if existing_name: # verifica se esiste già una pianta con lo stesso nome in uso
        return False, "❌ Hai già una pianta con questo nome."

    plants.insert_one({ # inserisce la pianta associata a un pot e uno user nel database
        "user_id": user_id,
        "pot_id": pot_id,
        "plant_name": plant_name
    })

    mark_pot_as_used(pot_id, user_id) # segna nel database che il pot ora è usato e da chi è usato.

    return True, "✅ Pianta aggiunta con successo!"


def get_user_plants(user_id): # Restituisce tutte le piante associate a uno specifico utente.
    return list(plants.find({"user_id": user_id}))


def remove_plant(user_id, plant_name): # Rimuove una pianta dell'utente e libera il pot associato
    plant = plants.find_one({
        "user_id": user_id,
        "plant_name": plant_name
    })

    if not plant: # controlla se non esiste la pianta
        return False

    pot_id = plant["pot_id"]

    plants.delete_one({ # cancella la pianta
        "user_id": user_id,
        "plant_name": plant_name
    })

    free_pot(pot_id) # libera il pot

    return True


def rename_plant(user_id, old_name, new_name): # rinomina una pianta
    old_plant = plants.find_one({
        "user_id": user_id,
        "plant_name": old_name
    })

    if not old_plant: # controlla se non esiste la pianta
        return False, "❌ Non possiedi nessuna pianta con quel nome."

    duplicate = plants.find_one({
        "user_id": user_id,
        "plant_name": new_name
    })

    if duplicate: # Controlla se esiste già una pianta con il nuovo nome
        return False, "❌ Hai già una pianta con questo nome. Scegli un nome diverso."

    plants.update_one( # modifica il nome della pianta
        {"user_id": user_id, "plant_name": old_name},
        {"$set": {"plant_name": new_name}}
    )

    return True, "✅ Nome della pianta aggiornato!"
