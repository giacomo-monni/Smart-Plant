"""
bot/managers/state_manager.py implements a state machine to manage bot actions and keeps track of user sessions
through their chat_id. It is also used to manage a command that requires multiple steps to be executed.
"""

user_states = {}  # Populated with user states using entries like "chat_id: state"
user_sessions = {}  # Populated with logged-in users using entries like "chat_id: username"


def set_state(chat_id, state):  # Sets the current state of a user (logged in or not)
    user_states[chat_id] = state


def get_state(chat_id):  # Returns the current state of a user (logged in or not)
    return user_states.get(chat_id)


def clear_state(chat_id):  # Removes the user's state
    user_states.pop(chat_id, None)


def login_user(chat_id, username):  # Handles user login by adding them to the list of logged-in users
    user_sessions[chat_id] = username


def logout_user(chat_id):  # Handles user logout by removing them from the list of logged-in users
    user_sessions.pop(chat_id, None)


def is_logged_in(chat_id):  # Checks whether a user is currently logged in
    return chat_id in user_sessions  # Returns True if the user is in the logged-in users list


def get_logged_username(chat_id):  # Returns the username associated with the user's chat_id
    return user_sessions.get(chat_id)
