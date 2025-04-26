
"""
handler.py fa da nucleo centrale per la gestione degli stati e dei comandi quando riceve un messaggio dal bot.
Riconosce lo user e decide come gestire le informazioni ricevute e cosa restituire all'utente.
"""

from .handlers.auth import commands as auth_cmds, states as auth_states
from .handlers.plant import commands as plant_cmds, states as plant_states
from .handlers.base import commands as base_cmds
from .state_manager import get_state


def handle_update(update): # gestisce i messaggi ricevuti dal bot o da mandare al bot
    message = update.get("message", {}) # messaggio che riceve dall'utente tramite il bot
    text = message.get("text", "") # estrae solo la componente del testo dal messaggio
    chat_id = message.get("chat", {}).get("id") # estrae il chat_id dal messaggio

    state = get_state(chat_id) # rileva lo stato attuale dello user

    for handler in (auth_states, plant_states): # gestisce gli stati
        response = handler.handle_state(state, text, chat_id)
        if response:
            return response

    for handler in (auth_cmds, plant_cmds, base_cmds): # gestisce i comandi
        response = handler.handle_command(text, chat_id)
        if response:
            return response
