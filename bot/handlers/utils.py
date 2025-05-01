
"""
utils.py contiene funzioni utili ad altre funzioni considerabili principali.
Principalmente roba per gestire meglio la ripetizione di funzioni richiamate spesso.
Non è molto importante ai fini del progetto.
"""

from ..commands import commands
from ..state_manager import is_logged_in


def send(chat_id, text, markdown=False): # crea il messaggio da inviare al bot e quindi visualizzare all'utente
    return {
        "method": "sendMessage",
        "chat_id": chat_id,
        "text": text,
        **({"parse_mode": "Markdown"} if markdown else {})
    }


def get_available_commands(user_id): # estrae i comandi da dover mostrare all'utente loggato e non loggato
    return (
        ["/help", "/info", "/add_plant", "/remove_plant", "/assistance", "/info_plant",
         "/stat_plant", "/get_data_now", "/get_data", "/modify_plant"]
        if is_logged_in(user_id)
        else ["/help", "/info", "/login", "/register", "/assistance"]
    )


def get_welcome_message(chat_id, username=None): # messaggio di benvenuto quando si verifica il comando /start
    intro = f"✅ Benvenuto {username}!\n\n" if username else "🌱 Benvenuto nel bot Smart Plant!\n\n"
    available = get_available_commands(chat_id)
    return intro + "Ecco i comandi disponibili:\n" + "\n".join([f"{cmd}: {commands[cmd]}" for cmd in available])


def get_help_message(chat_id): # # mostra la lista dei comandi in base all'utente se è loggato o no
    available = get_available_commands(chat_id)
    return "📋 Comandi disponibili:\n\n" + "\n".join([f"{cmd}: {commands[cmd]}" for cmd in available])
