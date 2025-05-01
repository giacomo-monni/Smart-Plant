from ..utils import send, get_welcome_message, get_help_message

"""
base/commands.py
"""

def handle_command(text, chat_id): # gestisce i comandi relativi a funzionalità base
    if text == "/start": # manda un messaggio di benvenuto e mostra la lista dei comandi
        return send(chat_id, get_welcome_message(chat_id))

    elif text == "/help": # mostra la lista dei comandi
        return send(chat_id, get_help_message(chat_id))

    elif text == "/info": # mostra info varie sul progetto
        return send(chat_id, (
            "🌿 *Smart Plant* è un sistema intelligente per monitorare e prendersi cura delle tue piante.\n\n"
            "• Monitora l'umidità del terreno\n"
            "• Ricevi notifiche automatiche\n"
            "• Automatizza l'irrigazione 🌱"
        ), markdown=True)

    elif text == "/assistance": # opzione di richiesta assistenza se ci sono problemi WIP.
        return send(chat_id, "📞 Per problemi contatta l'assistenza (WIP).")


