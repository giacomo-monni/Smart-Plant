
"""
bot/commands.py contains the list of all commands the bot can execute, which are shown when using the /help command,
followed by their description.
"""

commands = {
    "/help": "Shows the list of available commands",
    "/login": "Log in with username and password",
    "/register": "Create a new account",
    "/add_plant": "Add a new plant to your smart pot",
    "/remove_plant": "Remove an existing plant",
    "/modify_plant": "Edit plant parameters (name, soil, temperature, humidity)",
    "/info_plant": "Returns the saved plant's information",
    "/stat_plant": "Displays the plant's statistics for the past 7 days",
    "/status": "Displays the plant's current status"
}

