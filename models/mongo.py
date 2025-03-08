"""
Functions to explore MongoDB database.
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
    """
    Create and return a MongoDB client.
    """
    try:
        client = MongoClient(MONGO_URI)
        print("MongoDB connected successfully!")
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise


def get_mongo_cards(db: str , target_collection: str) -> pd.DataFrame:
    """
    Retrieve cards from the target collection using MongoDB aggregation.

    Args: 
        db (str): The database name
        target_collection (str): The target collection to query
    """

    client = get_mongo_client()
    collection = client[db][target_collection]

    if target_collection == "kengrams":
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

        if "anchorChange" in df.columns and "metadata" in df.columns:
            df = df.drop(columns=["anchorChange", "metadata"])

        return df
    else:
        
        pipeline = [
        {"$match": {}},
        ]

        cursor = collection.aggregate(pipeline)
        df = pd.DataFrame(list(cursor))

        client.close()

        return df
