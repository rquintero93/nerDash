"""
Initialization file for the models package.

- Re-exports MongoDB-related functions for easier access.
- Uses the centralized logger from utils.
"""

from . import queries
from .mongo import MongoDBClient, get_database, get_mongo_cards

__all__ = [
    "MongoDBClient",
    "get_database",
    "get_mongo_cards",
    "queries",
]
