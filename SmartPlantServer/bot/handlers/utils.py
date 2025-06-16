"""
bot/handlers/utils.py contains utility functions that support other, more central functions.
Mainly used to reduce repetition of commonly used functions.
"""

from ..commands import commands
from ..state_manager import is_logged_in


def send(chat_id, text, markdown=False):  # Creates the message to be sent to the bot and shown to the user
    return {
        "method": "sendMessage",
        "chat_id": chat_id,
        "text": text,
        **({"parse_mode": "Markdown"} if markdown else {})
    }


def get_available_commands(user_id):  # Returns the list of commands based on whether the user is logged in or not
    return (
        ["/help", "/info", "/add_plant", "/remove_plant", "/assistance", "/info_plant",
         "/stat_plant", "/get_data_now", "/modify_plant"]
        if is_logged_in(user_id)
        else ["/help", "/info", "/login", "/register", "/assistance"]
    )


def get_welcome_message(chat_id, username=None):  # Welcome message shown when /start is triggered
    intro = f"✅ Welcome {username}!\n\n" if username else "🌱 Welcome to the Smart Plant bot!\n\n"
    available = get_available_commands(chat_id)
    return intro + "Here are the available commands:\n" + "\n".join([f"{cmd}: {commands[cmd]}" for cmd in available])


def get_help_message(chat_id):  # Shows the list of commands depending on whether the user is logged in
    available = get_available_commands(chat_id)
    return "📋 Available commands:\n\n" + "\n".join([f"{cmd}: {commands[cmd]}" for cmd in available])
