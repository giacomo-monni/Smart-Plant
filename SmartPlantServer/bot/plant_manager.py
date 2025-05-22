
"""
plant_manager.py si occupa della gestione delle piante lato database.
Quindi inserimento di una pianta dal database, la sua cancellazione e la modifica dei parametri delle piante possedute
da un utente. Si può espandere in base ai dati che vogliamo salvare nel database.
"""

from pymongo import MongoClient
from config import MONGO_URI
from .pot_manager import is_valid_pot, mark_pot_as_used, free_pot
from datetime import datetime, timedelta

client = MongoClient(MONGO_URI)
db = client.smartplant
plants = db.plants


def add_plant(user_id, pot_id, plant_name, soil_threshold, temperature_range, humidity_threshold): # aggiunge una pianta associata a un pot nel database
    valid, msg = is_valid_pot(pot_id) # verifica se il pot esiste e se sia già in uso
    if not valid:
        return False, msg

    existing_name = plants.find_one({
        "user_id": user_id,
        "plant_name": plant_name
    })
    if existing_name: # verifica se esiste già una pianta con lo stesso nome in uso
        return False, "❌ Hai già una pianta con questo nome."

    try:
        soil_threshold = abs(int(soil_threshold))
        temperature_range = [abs(int(temperature_range[0])), abs(int(temperature_range[1]))]
        humidity_threshold = abs(int(humidity_threshold))
    except ValueError:
        return False, "❌ Hai inserito dei dati invalidi."

    plants.insert_one({ # inserisce la pianta associata a un pot e uno user nel database
        "user_id": user_id,
        "pot_id": pot_id,
        "plant_name": plant_name,
        "soil_threshold": soil_threshold,
        "temperature_range": temperature_range,
        "humidity_threshold": humidity_threshold
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

    db.pot_data.delete_many({"pot_id": pot_id})

    return True


def info_plant(user_id, plant_name):
    existing_plant = plants.find_one({
        "user_id": user_id,
        "plant_name": plant_name
    })
    existing_plant.pop("_id", None)  # Rimuove il campo _id se esiste
    existing_plant.pop("user_id", None)
    righe = [f"{chiave}: {valore}" for chiave, valore in existing_plant.items()]
    stringa_finale = "\n".join(righe)

    return stringa_finale


def modify_plant(user_id, old_name, new_name, soil, temp, humidity): # modifica una pianta
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

    if duplicate and old_name != new_name: # Controlla se esiste già una pianta con il nuovo nome
        return False, "❌ Hai già una pianta con questo nome. Scegli un nome diverso."

    plants.update_one( # modifica i dati della pianta
        {"user_id": user_id, "plant_name": old_name},
        {"$set": {
            "plant_name": new_name,
            "soil_threshold": soil,
            "temperature_range": temp,
            "humidity_threshold": humidity}}
    )

    return True, "✅ Nome della pianta aggiornato!"


def get_plant_statistics(pot_id):
    from statistics import mean
    pot_data_col = db["pot_data"]

    today = datetime.utcnow()
    week_ago = today - timedelta(days=7)

    try:
        # Recupera tutti i dati dell'ultima settimana per quel pot_id
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

        # Per il calcolo del tempo in condizioni ideali
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
        print(f"Errore nel recuperare le statistiche: {e}")
        return None

