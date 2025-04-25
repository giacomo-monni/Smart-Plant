from .handlers.auth import commands as auth_cmds, states as auth_states
from .handlers.plant import commands as plant_cmds, states as plant_states
from .handlers.base import commands as base_cmds
from .state_manager import get_state

# ordina per priorità: prima stati, poi comandi
def handle_update(update):
    message = update.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")

    state = get_state(chat_id)

    # Se esiste uno stato attivo, gestiscilo prima
    for handler in (auth_states, plant_states):
        response = handler.handle_state(state, text, chat_id)
        if response:
            return response

    # Altrimenti, gestisci il comando
    for handler in (auth_cmds, plant_cmds, base_cmds):
        response = handler.handle_command(text, chat_id)
        if response:
            return response
