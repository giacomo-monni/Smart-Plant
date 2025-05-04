
"""
handlers/plant/states.py
"""

from ...plant_manager import add_plant, remove_plant, modify_plant, get_user_plants, info_plant, get_plant_statistics
from ...state_manager import set_state, clear_state
from ..utils import send
from mqtt_client import client
import json

def handle_state(state, text, chat_id): # gestisce gli stati relativi alle azioni legate alle piante
    # Aggiunta pianta
    if state == "add_plant_pot":
        if len(get_user_plants(chat_id)) >= 3:
            clear_state(chat_id)
            return send(chat_id, "❌ Hai già raggiunto il numero massimo di piante (10).")
        set_state(chat_id, {"step": "add_plant_name", "pot_id": text})
        return send(chat_id, "🌱 Inserisci il nome della pianta da associare:")

    elif isinstance(state, dict) and state.get("step") == "add_plant_name":
        state["step"] = "add_plant_moisture"
        state["plant_name"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Inserisci il valore di umidità del terreno (eg. 10 = 10%):")

    elif isinstance(state, dict) and state.get("step") == "add_plant_moisture":
        state["step"] = "add_plant_tempmin"
        state["soil_threshold"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Inserisci il valore minimo di temperatura (eg. 10 = 10°C):")

    elif isinstance(state, dict) and state.get("step") == "add_plant_tempmin":
        state["step"] = "add_plant_tempmax"
        state["min_temperature"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Inserisci il valore massimo di temperatura (eg. 10 = 10°C):")

    elif isinstance(state, dict) and state.get("step") == "add_plant_tempmax":
        state["step"] = "add_plant_humidity"
        state["max_temperature"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Inserisci il valore di umidità dell'aria (eg. 10 = 10%):")

    elif isinstance(state, dict) and state.get("step") == "add_plant_humidity":
        temperature_range = [state["min_temperature"], state["max_temperature"]]
        success, msg = add_plant(chat_id, state["pot_id"], state["plant_name"], state["soil_threshold"], temperature_range, text)
        clear_state(chat_id)
        return send(chat_id, msg)

    # Rimozione pianta
    elif state == "remove_plant_select":
        success = remove_plant(chat_id, text)
        clear_state(chat_id)
        return send(chat_id, "🗑️ Pianta rimossa con successo." if success else "⚠️ Pianta non trovata.")

    # Info Plant
    elif state == "info_plant_select":
        plant_list = get_user_plants(chat_id)
        names = [p["plant_name"] for p in plant_list]
        clear_state(chat_id)
        if text not in names:
            return send(chat_id, "❌ Il nome della pianta non è valido.")
        return send(chat_id, info_plant(chat_id,text))

    # Modify Plant
    elif state == "modify_plant_select":
        plant_list = get_user_plants(chat_id)
        names = [p["plant_name"] for p in plant_list]
        if text not in names:
            clear_state(chat_id)
            return send(chat_id, "❌ Il nome della pianta non è valido.")
        set_state(chat_id, {"step": "modify_plant_name", "old_name": text})
        return send(chat_id, "✏️ Inserisci il nuovo nome della pianta:")

    elif isinstance(state, dict) and state.get("step") == "modify_plant_name":
        state["step"] = "modify_plant_moisture"
        state["new_name"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Inserisci il valore di umidità del terreno (eg. 10 = 10%):")

    elif isinstance(state, dict) and state.get("step") == "modify_plant_moisture":
        state["step"] = "modify_plant_tempmin"
        state["soil_threshold"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Inserisci il valore minimo di temperatura (eg. 10 = 10°C):")

    elif isinstance(state, dict) and state.get("step") == "modify_plant_tempmin":
        state["step"] = "modify_plant_tempmax"
        state["min_temperature"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Inserisci il valore massimo di temperatura (eg. 10 = 10°C):")

    elif isinstance(state, dict) and state.get("step") == "modify_plant_tempmax":
        state["step"] = "modify_plant_humidity"
        state["max_temperature"] = text
        set_state(chat_id, state)
        return send(chat_id, "🌱 Inserisci il valore di umidità dell'aria (eg. 10 = 10%):")

    elif isinstance(state, dict) and state.get("step") == "modify_plant_humidity":
        temperature_range = [state["min_temperature"], state["max_temperature"]]
        success, msg = modify_plant(chat_id, state["old_name"], state["new_name"], state["soil_threshold"], temperature_range, text)
        clear_state(chat_id)
        return send(chat_id, msg)

    elif state == "data_plant_select":
        plant_list = get_user_plants(chat_id)
        names = [p["plant_name"] for p in plant_list]
        clear_state(chat_id)
        if text not in names:
            return send(chat_id, "❌ Il nome della pianta non è valido.")

        plant = next(p for p in plant_list if p["plant_name"] == text)
        pot_id = plant["pot_id"]

        payload = {"action": "get_data_now"}
        topic = f"smartplant/{pot_id}/cmd"

        if not client.is_connected():
            return send(chat_id, "❌ Ci sono problemi con i server, riprova più tardi.")

        client.publish(topic, json.dumps(payload))  # Pubblica il comando

        return send(chat_id, "✅ Comando inviato, attendi la risposta.")

    elif state == "stat_plant_select":
        plant_list = get_user_plants(chat_id)
        names = [p["plant_name"] for p in plant_list]
        clear_state(chat_id)
        if text not in names:
            return send(chat_id, "❌ Il nome della pianta non è valido.")

        # Recupera la pianta
        plant = next(p for p in plant_list if p["plant_name"] == text)
        pot_id = plant["pot_id"]  # Assumiamo che ogni pianta abbia un pot_id

        # Recupera le statistiche dalla pianta, ad esempio tramite un'API del broker o database
        try:
            stats = get_plant_statistics(pot_id)  # Funzione da implementare per ottenere le statistiche
            if not stats:
                return send(chat_id, "❌ Non sono disponibili statistiche per questa pianta.")

            # Formattazione del report settimanale
            week_report = (
                f"🌱 Statistiche della pianta *{text}* per l'ultima settimana:\n\n"
                f"📅 Settimana dal {stats['week_start']} al {stats['week_end']}\n\n"
                f"📊 Temperatura media: {stats['avg_temperature']}°C\n"
                f"📈 Temperatura max: {stats['max_temperature']}°C\n"
                f"📉 Temperatura min: {stats['min_temperature']}°C\n"
                f"💧 Umidità media: {stats['avg_humidity']}%\n"
                f"🌿 Umidità minima: {stats['min_humidity']}%\n"
                f"💡 Luce assorbita media: {stats['avg_light']} lux\n"
                f"🌾 Umidità terreno media: {stats['avg_soil_moisture']}%\n\n"
                f"💧 La pianta è stata irrigata {stats['irrigations_count']} volte negli ultimi 7 giorni\n"
                f"🚱 {stats['missed_irrigations_percentage']}% delle volte la pianta doveva essere irrigata ma non aveva acqua\n\n"
                f"✅ Tutti i parametri della pianta sono rimasti nei limiti ideali per il {stats['ideal_conditions_percentage']}% del tempo."
            )

            return send(chat_id, week_report, markdown=True)

        except Exception as e:
            return send(chat_id, f"❌ Si è verificato un errore nel recuperare le statistiche: {str(e)}")
