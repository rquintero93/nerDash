"""
Script to explore nerDB MongoDB database.
"""

import os

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient

# MongoDB Connection Details
dotenv_path = os.path.expanduser("~/Documents/DeSciWorld/nerdBot/.env")
load_dotenv(dotenv_path)
MONGO_URI = os.getenv("MONGO_URI")


def get_mongo_client() -> MongoClient:
    """Create and return a MongoDB client."""
    try:
        client = MongoClient(MONGO_URI)
        print("MongoDB connected successfully!")
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise


def get_mongo_cards(
    db: str = "ragDB", target_collection: str = "kengrams"
) -> pd.DataFrame:
    """Retrieve cards from the globalstates collection using MongoDB aggregation."""
    client = get_mongo_client()
    collection = client[db][target_collection]

    pipeline = [
        {
            "$match": {"anchorChange": {"$exists": True, "$not": {"$size": 0}}}
        },  # Ensure "anchorChange" field exists
        {"$unwind": "$anchorChange"},  # Flatten the "anchorChange" array
        {
            "$replaceRoot": {
                "newRoot": {
                    "$mergeObjects": ["$$ROOT", "$anchorChange"]
                }
            }
        },
        {
            "$unwind": "$metadata"  # Flatten the "metadata" array
        },
        {
            "$replaceRoot": {
                "newRoot": {
                    "$mergeObjects": ["$$ROOT", "$metadata"]
                }
            }
        }
    ]

    cursor = collection.aggregate(pipeline)
    df = pd.DataFrame(list(cursor))

    client.close()

    df = df.drop(columns=["anchorChange", "metadata"])
    return df


def get_globalstates_retrievalCount(
    db: str = "ragDB", target_collection: str = "kengrams"
) -> pd.DataFrame:
    """Retrieve retrievalCount data from the globalstates collection using MongoDB aggregation."""
    client = get_mongo_client()
    collection = client[db][target_collection]

    pipeline = [
        {"$match": {"retrievalCount": {"$exists": True}}},
        {
            "$project": {"retrievalCount": {"$objectToArray": "$retrievalCount"}}
        },  # Convert to key-value array
        {"$unwind": "$retrievalCount"},  # Flatten retrievalCount dictionary
        {
            "$project": {
                "id": "$retrievalCount.k",
                "retrievalCount": "$retrievalCount.v",
            }
        },  # Extract ID & count
    ]

    cursor = collection.aggregate(pipeline)
    df = pd.DataFrame(list(cursor))

    client.close()
    return df


def get_history(db: str = "ragDB", target_collection: str = "history") -> pd.DataFrame:
    """Retrieve the history collection efficiently."""
    client = get_mongo_client()
    collection = client[db][target_collection]

    pipeline = [
        {"$match": {}},  # No filter, but can be customized
        {
            "$project": {"_id": 0}
        },  # Remove MongoDB default `_id` field for cleaner DataFrame
    ]

    cursor = collection.aggregate(pipeline)
    df = pd.DataFrame(list(cursor))

    client.close()
    return df
