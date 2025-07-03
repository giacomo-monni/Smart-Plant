"""
bot/handlers/auth/commands.py handles commands related to user registration and login
"""

from bot.managers.state_manager import set_state, is_logged_in
from bot.utils import send


def handle_command(text, chat_id):  # Handles authentication commands
    if text == "/register":  # Registers the user only if they are not already logged in
        if is_logged_in(chat_id):
            return send(chat_id, "🔐 You are already logged in.")
        set_state(chat_id, "register_username")
        return send(chat_id, "📝 Please enter a username to register:") # Asks to register a username

    elif text == "/login":  # Allows login only if the user is not already logged in
        if is_logged_in(chat_id):
            return send(chat_id, "🔐 You are already logged in.")
        set_state(chat_id, "login_username")
        return send(chat_id, "🔑 Please enter your username:") # Asks a username to log in
