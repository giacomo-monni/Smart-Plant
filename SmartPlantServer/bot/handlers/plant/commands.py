"""
bot/handles/plant/commands.py
This module handles all plant-related commands.
It provides functionalities for users to interact with their registered smart pots and manage their plants.
All commands first check if the user is logged in, and then validate if any plants are already associated
with the user where necessary.
"""

from bot.managers.plant_manager import get_user_plants
from bot.managers.state_manager import is_logged_in, set_state
from bot.utils import send


def handle_command(text, chat_id):  # Handles plant-related bot commands
    if text == "/add_plant":  # Add a new plant
        if not is_logged_in(chat_id):
            return send(chat_id, "🔒 You must be logged in to use this command.")
        set_state(chat_id, "add_plant_pot")
        return send(chat_id, "🔢 Enter the smart pot ID (pot_<id>):")

    elif text == "/remove_plant":  # Removes a plant
        if not is_logged_in(chat_id):
            return send(chat_id, "🔒 You must be logged in to use this command.")
        plant_list = get_user_plants(chat_id)
        if not plant_list:
            return send(chat_id, "🌿 You have no registered plants.")
        names = [p["plant_name"] for p in plant_list]
        set_state(chat_id, "remove_plant_select")
        return send(chat_id, "🗑️ Select the plant to remove:\n" + "\n".join(names))

    elif text == "/info_plant":  # Views plant info
        if not is_logged_in(chat_id):
            return send(chat_id, "🔒 You must be logged in to use this command.")
        plant_list = get_user_plants(chat_id)
        if not plant_list:
            return send(chat_id, "🌿 You have no registered plants.")
        names = [p["plant_name"] for p in plant_list]
        set_state(chat_id, "info_plant_select")
        return send(chat_id, "🛠️ Select a plant to view its information:\n" + "\n".join(names))

    elif text == "/modify_plant":  # Modifies plant info
        if not is_logged_in(chat_id):
            return send(chat_id, "🔒 You must be logged in to use this command.")
        plant_list = get_user_plants(chat_id)
        if not plant_list:
            return send(chat_id, "🌿 You have no registered plants.")
        names = [p["plant_name"] for p in plant_list]
        set_state(chat_id, "modify_plant_select")
        return send(chat_id, "🛠️ Select the plant to modify:\n" + "\n".join(names))

    elif text == "/stat_plant":  # Shows plant statistics
        if not is_logged_in(chat_id):
            return send(chat_id, "🔒 You must be logged in to use this command.")
        plant_list = get_user_plants(chat_id)
        if not plant_list:
            return send(chat_id, "🌿 You have no registered plants.")
        names = [p["plant_name"] for p in plant_list]
        set_state(chat_id, "stat_plant_select")
        return send(chat_id, "🛠️ Select the plant to receive statistical data:\n" + "\n".join(names))

    elif text == "/status":  # Shows the current plant status
        if not is_logged_in(chat_id):
            return send(chat_id, "🔒 You must be logged in to use this command.")
        plant_list = get_user_plants(chat_id)
        if not plant_list:
            return send(chat_id, "🌿 You have no registered plants.")
        names = [p["plant_name"] for p in plant_list]
        set_state(chat_id, "status_plant_select")
        return send(chat_id, "🛠️ Select the plant to modify:\n" + "\n".join(names))