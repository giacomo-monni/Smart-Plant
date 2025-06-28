"""
bot/managers/pot_manager.py contains some utility functions for managing pots, such as checking if a pot has a valid ID,
if a pot has already been used, and for marking a pot as used or making it available again.
"""

from db import pots_collection


def is_valid_pot(pot_id):  # Checks whether the pot exists and hasn't already been used
    pot = pots_collection.find_one({"pot_id": pot_id})  # Pots are identified by an ID
    if not pot:
        return False, "❌ This ID does not exist in our system."
    if pot.get("used"):
        return False, "⚠️ This smart pot is already in use."
    return True, ""


def mark_pot_as_used(pot_id, chat_id):  # Marks a pot as used by a user
    pots_collection.update_one(
        {"pot_id": pot_id},
        {"$set": {"used": True, "chat_id": chat_id}}
    )


def free_pot(pot_id):  # Frees a pot, making it available again
    pots_collection.update_one(
        {"pot_id": pot_id},
        {"$set": {"used": False, "chat_id": None}}
    )
