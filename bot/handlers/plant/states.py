
"""
plant/states.py
"""

from ...plant_manager import add_plant, remove_plant, modify_plant, get_user_plants, info_plant
from ...state_manager import set_state, clear_state
from ..utils import send


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

    # Riname pianta
    # elif state == "rename_plant_select":
    #     plant_list = get_user_plants(chat_id)
    #     names = [p["plant_name"] for p in plant_list]
    #     if text not in names:
    #         clear_state(chat_id)
    #         return send(chat_id, "❌ Il nome della pianta non è valido.")
    #     set_state(chat_id, {"step": "manage_plant_rename", "old_name": text})
    #     return send(chat_id, "✏️ Inserisci il nuovo nome della pianta:")
    #
    # elif isinstance(state, dict) and state.get("step") == "manage_plant_rename":
    #     success = rename_plant(chat_id, state["old_name"], text)
    #     clear_state(chat_id)
    #     return send(chat_id, "✅ Nome modificato con successo." if success else "⚠️ Pianta non trovata.")

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