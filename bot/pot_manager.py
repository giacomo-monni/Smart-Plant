
"""
pot_manager.py contiene alcune funzioni utili per la gestione dei pot come verificare se un pot ha un id valido,
se un pot è già stato usato, per impostare un pot come usato o renderlo nuovamente disponibile.
"""

from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client.smartplant
pots = db.pots


def is_valid_pot(pot_id): # Verifica se il pot esiste e non sia già stato usato
    pot = pots.find_one({"pot_id": pot_id}) # i pot sono identificati da un id
    if not pot:
        return False, "❌ Questo ID non esiste nei nostri sistemi."
    if pot.get("used"):
        return False, "⚠️ Questo smart pot è già in uso."
    return True, ""


def mark_pot_as_used(pot_id, user_id): # imposta un pot come utilizzato da uno user
    pots.update_one(
        {"pot_id": pot_id},
        {"$set": {"used": True, "user_id": user_id}}
    )


def free_pot(pot_id): # libera un pot rendendolo nuovamente disponibile
    pots.update_one(
        {"pot_id": pot_id},
        {"$set": {"used": False, "user_id": None}}
    )
