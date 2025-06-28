"""
db.py creates a MongoDB connection and makes the various collections available.
"""

from pymongo import MongoClient
from config import MONGO_URI

mongo_client = MongoClient(MONGO_URI)

db = mongo_client["smartplant"]

plants_profile_collection = db["plants_profile"]
pots_collection = db["pots"]
pot_data_collection = db["pot_data"]
digital_replica_collection = db["digital_replicas"]
users_collection = db["users"]