from ...plant_manager import get_user_plants
from ...state_manager import is_logged_in, set_state
from ..utils import send


def handle_command(text, chat_id):
    if text == "/add_plant":
        if not is_logged_in(chat_id):
            return send(chat_id, "🔒 Devi essere loggato per usare questo comando.")
        set_state(chat_id, "add_plant_pot")
        return send(chat_id, "🔢 Inserisci l'ID dello smart pot:")

    elif text == "/remove_plant":
        if not is_logged_in(chat_id):
            return send(chat_id, "🔒 Devi essere loggato per usare questo comando.")
        plant_list = get_user_plants(chat_id)
        if not plant_list:
            return send(chat_id, "🌿 Non hai piante registrate.")
        names = [p["plant_name"] for p in plant_list]
        set_state(chat_id, "remove_plant_select")
        return send(chat_id, "🗑️ Scegli la pianta da rimuovere:\n" + "\n".join(names))

    elif text == "/manage_plant":
        if not is_logged_in(chat_id):
            return send(chat_id, "🔒 Devi essere loggato per usare questo comando.")
        plant_list = get_user_plants(chat_id)
        if not plant_list:
            return send(chat_id, "🌿 Non hai piante registrate.")
        names = [p["plant_name"] for p in plant_list]
        set_state(chat_id, "manage_plant_select")
        return send(chat_id, "🛠️ Scegli la pianta da gestire:\n" + "\n".join(names))

    elif text == "/status_plant":
        if not is_logged_in(chat_id):
            return send(chat_id, "🔒 Devi essere loggato per usare questo comando.")
        return send(chat_id, "📡 Qui verrà restituito lo status della pianta.")