"""
bot/auth.py handles the authentication aspect related to the database, so it does not consider
the current state of the user. Its role is also to register and authenticate a user.
"""

import bcrypt
from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)  # Connection to the MongoDB server
db = client.smartplant  # Extracts the 'smartplant' database
users = db.users  # Extracts the 'users' collection


def register_user(username, password, chat_id):  # Responsible for registering a user
    if users.find_one({"chat_id": chat_id}):  # If the account already exists, don't register
        return False, "❌ You are already linked to a profile with this account."

    if users.find_one({"username": username}):  # If the username is already taken, don't register
        return False, "❌ Username already in use."

    salt = bcrypt.gensalt()  # Generates a salt to use when hashing the password
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt)  # Applies the bcrypt hashing algorithm

    user_data = {  # Data to be saved to the database
        "chat_id": chat_id,
        "username": username,
        "password_hash": hashed_pw,
        "salt": salt
    }

    users.insert_one(user_data)  # Saves the user data to the database
    return True, "✅ Registration successful."


def authenticate_user(username, password, chat_id):  # Responsible for user login
    user = users.find_one({"username": username})
    if not user:  # Check if the user exists in the database
        return False

    if user.get("chat_id") != chat_id:  # Prevent login from different Telegram accounts
        return False  # Note: no detailed error message to avoid leaking info.

    hashed_input = bcrypt.hashpw(password.encode('utf-8'), user['salt'])  # Hashes the provided password
    if hashed_input != user['password_hash']:  # Verifies if password matches the stored one
        return False

    return True
