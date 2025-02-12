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


def get_globalstates_cards(
    db: str = "ragDB", target_collection: str = "kengrams"
) -> pd.DataFrame:
    """Retrieve cards from the globalstates collection using MongoDB aggregation."""
    client = get_mongo_client()
    collection = client[db][target_collection]

    # pipeline = [
    #     {
    #         "$match": {"cards": {"$exists": True, "$not": {"$size": 0}}}
    #     },  # Ensure "cards" field exists
    #     {"$unwind": "$cards"},  # Flatten the "cards" array
    #     {
    #         "$replaceRoot": {
    #             "newRoot": {
    #                 "id": {"$first": {"$objectToArray": "$cards"}},
    #                 "details": {"$last": {"$objectToArray": "$cards"}},
    #             }
    #         }
    #     },
    #     {
    #         "$replaceRoot": {"newRoot": {"id": "$id.k", "details": "$details.v"}}
    #     },  # Extract key as ID, value as details
    # ]

    pipeline = [
        {"$match": {}},  # No filter, but can be customized
        {
            "$project": {"_id": 0}
        },
    ]

    cursor = collection.aggregate(pipeline)
    df = pd.DataFrame(list(cursor))

    # if "anchorChange" in df.columns:
    #     anchorChange = pd.json_normalize(df["anchorChange"], sep='_', record_prefix='anchorChange')
    #     df = pd.concat([df.drop(columns=["anchorChange"]), anchorChange], axis=1)
    #
    # if "metadata" in df.columns:
    #     metadata = pd.json_normalize(df["metadata"], sep='_', record_prefix='metadata')
    #     df = pd.concat([df.drop(columns=["metadata"]), metadata], axis=1)


    client.close()
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
