"""
bot/handler.py acts as the central core for managing states and commands when a message is received by the bot.
It recognizes the user and decides how to handle the received information and what to return to the user.
"""

from .handlers.auth import commands as auth_cmds, states as auth_states
from .handlers.plant import commands as plant_cmds, states as plant_states
from .handlers.base import commands as base_cmds
from .state_manager import get_state
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("./logs/server.log", mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)


def handle_update(update):  # Handles messages received from or sent to the bot
    message = update.get("message", {})  # Message received from the user via the bot
    text = message.get("text", "")  # Extracts only the text component from the message
    chat_id = message.get("chat", {}).get("id")  # Extracts the chat_id from the message

    state = get_state(chat_id)  # Retrieves the current state of the user

    for handler in (auth_states, plant_states):  # Handles states
        response = handler.handle_state(state, text, chat_id)
        if response:
            return response

    logging.debug(f"Command {text} from {chat_id}")
    for handler in (auth_cmds, plant_cmds, base_cmds):  # Handles commands
        response = handler.handle_command(text, chat_id)
        if response:
            return response
