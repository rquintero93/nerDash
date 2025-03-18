"""
Initialization file for the models package.

- Re-exports MongoDB-related functions for easier access.
- Uses the centralized logger from utils.
"""

from utils import logger

from . import queries
from .mongo import MongoDBClient, get_database, get_mongo_cards

__all__ = [
    "get_database",
    "get_mongo_cards",
    "MongoDBClient",
    "logger",
    "queries",
]
