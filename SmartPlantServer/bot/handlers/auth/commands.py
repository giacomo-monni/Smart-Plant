
"""
handlers/auth/commands.py
"""

from ...state_manager import set_state, logout_user, is_logged_in
from ..utils import send


def handle_command(text, chat_id): # gestisce i comandi di autenticazione
    if text == "/register": # registra l'utente solo se non è già loggato
        if is_logged_in(chat_id):
            return send(chat_id, "🔐 Sei già loggato.")
        set_state(chat_id, "register_username")
        return send(chat_id, "📝 Inserisci uno username per registrarti:")

    elif text == "/login": # puoi fare il login ma solo se non sei già loggato
        if is_logged_in(chat_id):
            return send(chat_id, "🔐 Sei già loggato.")
        set_state(chat_id, "login_username")
        return send(chat_id, "🔑 Inserisci il tuo username:")

    # elif text == "/logout": # puoi fare il loggout ma solo se sei già loggato
    #     if is_logged_in(chat_id):
    #         logout_user(chat_id)
    #         return send(chat_id, "🔓 Logout effettuato con successo.")
    #     return send(chat_id, "ℹ️ Non sei loggato.")
