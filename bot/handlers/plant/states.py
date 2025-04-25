from ...plant_manager import add_plant, remove_plant, rename_plant, get_user_plants
from ...state_manager import set_state, clear_state
from ..utils import send


def handle_state(state, text, chat_id):
    # Aggiunta pianta
    if state == "add_plant_pot":
        if len(get_user_plants(chat_id)) >= 10:
            clear_state(chat_id)
            return send(chat_id, "❌ Hai già raggiunto il numero massimo di piante (10).")
        set_state(chat_id, {"step": "add_plant_name", "pot_id": text})
        return send(chat_id, "🌱 Inserisci il nome della pianta da associare:")

    elif isinstance(state, dict) and state.get("step") == "add_plant_name":
        success, msg = add_plant(chat_id, state["pot_id"], text)
        clear_state(chat_id)
        return send(chat_id, msg)

    # Rimozione pianta
    elif state == "remove_plant_select":
        success = remove_plant(chat_id, text)
        clear_state(chat_id)
        return send(chat_id, "🗑️ Pianta rimossa con successo." if success else "⚠️ Pianta non trovata.")

    # Gestione pianta
    elif state == "manage_plant_select":
        plant_list = get_user_plants(chat_id)
        names = [p["plant_name"] for p in plant_list]
        if text not in names:
            clear_state(chat_id)
            return send(chat_id, "❌ Il nome della pianta non è valido.")
        set_state(chat_id, {"step": "manage_plant_rename", "old_name": text})
        return send(chat_id, "✏️ Inserisci il nuovo nome della pianta:")

    elif isinstance(state, dict) and state.get("step") == "manage_plant_rename":
        success = rename_plant(chat_id, state["old_name"], text)
        clear_state(chat_id)
        return send(chat_id, "✅ Nome modificato con successo." if success else "⚠️ Pianta non trovata.")
