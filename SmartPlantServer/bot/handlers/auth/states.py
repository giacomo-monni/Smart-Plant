"""
bot/handlers/auth/states.py
This module manages the finite state machine transitions for user authentication processes.
Each user interaction that requires multiple steps—such as providing a username followed by a password—
is tracked using a state machine based on the user's chat ID. This allows the bot to guide the user
through sequential inputs and update the internal session and authentication status accordingly.
"""

from ...auth import register_user, authenticate_user
from bot.managers.state_manager import set_state, clear_state, login_user
from bot.utils import send, get_welcome_message


def handle_state(state, text, chat_id):  # Handles states related to authentication actions
    if state == "register_username":  # Handles states related to /register
        set_state(chat_id, {"step": "register_password", "username": text})
        return send(chat_id, "🔐 Please enter a password:")  # Prompts for password input

    elif isinstance(state, dict) and state.get("step") == "register_password":
        success, msg = register_user(state["username"], text, chat_id)  # Saves credentials to the database
        clear_state(chat_id)
        return send(chat_id, msg)

    elif state == "login_username":  # Handles states related to /login
        set_state(chat_id, {"step": "login_password", "username": text})
        return send(chat_id, "🔐 Please enter your password:")  # Prompts for password input

    elif isinstance(state, dict) and state.get("step") == "login_password":
        if authenticate_user(state["username"], text, chat_id):  # Verifies if the user exists
            login_user(chat_id, state["username"])  # Tracks the logged-in user
            clear_state(chat_id)
            return send(chat_id, get_welcome_message(chat_id, state["username"]))
        else:
            clear_state(chat_id)
            return send(chat_id, "❌ Incorrect username and/or password.")
