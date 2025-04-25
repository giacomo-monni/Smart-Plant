from ..commands import commands
from ..state_manager import is_logged_in


def send(chat_id, text, markdown=False):
    return {
        "method": "sendMessage",
        "chat_id": chat_id,
        "text": text,
        **({"parse_mode": "Markdown"} if markdown else {})
    }


def get_available_commands(user_id):
    return (
        ["/help", "/info", "/add_plant", "/manage_plant", "/remove_plant", "/logout", "/assistence", "/status_plant"]
        if is_logged_in(user_id)
        else ["/help", "/info", "/login", "/register", "/assistence"]
    )


def get_welcome_message(chat_id, username=None):
    intro = f"✅ Benvenuto {username}!\n\n" if username else "🌱 Benvenuto nel bot Smart Plant!\n\n"
    available = get_available_commands(chat_id)
    return intro + "Ecco i comandi disponibili:\n" + "\n".join([f"{cmd}: {commands[cmd]}" for cmd in available])


def get_help_message(chat_id):
    available = get_available_commands(chat_id)
    return "📋 Comandi disponibili:\n\n" + "\n".join([f"{cmd}: {commands[cmd]}" for cmd in available])
