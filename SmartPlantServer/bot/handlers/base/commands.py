"""
bot/handlers/base/commands.py
This module handles the basic, non-authentication-related commands.
These include general-purpose commands such as /start, /help, /info, and /assistance.
It serves as the entry point for new users and a help tool for logged-in users.
"""

from ..utils import send, get_welcome_message, get_help_message


def handle_command(text, chat_id):  # Handles commands related to general functionalities
    if text == "/start":  # Sends a welcome message and displays the list of available commands
        return send(chat_id, get_welcome_message(chat_id))

    elif text == "/help":  # Shows the list of available commands
        return send(chat_id, get_help_message(chat_id))

    elif text == "/info":  # Provides project-related information
        return send(chat_id, (
            "🌿 *Smart Plant* is an intelligent system for monitoring and taking care of your plants.\n\n"
            "• Monitors soil moisture\n"
            "• Sends automatic notifications\n"
            "• Automates irrigation 🌱"
        ), markdown=True)

    elif text == "/assistance":  # Placeholder for user support/help requests
        return send(chat_id, "📞 For issues, please contact support.")
