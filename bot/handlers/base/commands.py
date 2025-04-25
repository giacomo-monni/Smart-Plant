from ..utils import send, get_welcome_message, get_help_message

def handle_command(text, chat_id):
    if text == "/start":
        return send(chat_id, get_welcome_message(chat_id))

    elif text == "/help":
        return send(chat_id, get_help_message(chat_id))

    elif text == "/info":
        return send(chat_id, (
            "🌿 *Smart Plant* è un sistema intelligente per monitorare e prendersi cura delle tue piante.\n\n"
            "• Monitora l'umidità del terreno\n"
            "• Ricevi notifiche automatiche\n"
            "• Automatizza l'irrigazione 🌱"
        ), markdown=True)

    elif text == "/assistence":
        return send(chat_id, "📞 Per problemi contatta l'assistenza (WIP).")


