
"""
auth/states.py
"""

from ...auth import register_user, authenticate_user
from ...state_manager import set_state, get_state, clear_state, login_user
from ..utils import send, get_welcome_message


def handle_state(state, text, chat_id): # gestisce gli stati relativi alle azioni di autenticazione
    if state == "register_username":
        set_state(chat_id, {"step": "register_password", "username": text})
        return send(chat_id, "🔐 Inserisci una password:")

    elif isinstance(state, dict) and state.get("step") == "register_password":
        success, msg = register_user(state["username"], text, chat_id)
        clear_state(chat_id)
        return send(chat_id, msg)

    elif state == "login_username":
        set_state(chat_id, {"step": "login_password", "username": text})
        return send(chat_id, "🔐 Inserisci la password:")

    elif isinstance(state, dict) and state.get("step") == "login_password":
        if authenticate_user(state["username"], text, chat_id):
            login_user(chat_id, state["username"])
            clear_state(chat_id)
            return send(chat_id, get_welcome_message(chat_id, state["username"]))
        else:
            clear_state(chat_id)
            return send(chat_id, "❌ Username e/o password errati.")
