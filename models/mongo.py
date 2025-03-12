"""
Functions to explore MongoDB database.
"""

import pandas as pd
from pymongo import MongoClient

import models.queries as queries
import utils.constants as constants


def get_mongo_client(connection_url:str) -> MongoClient:
    """
    Create and return a MongoDB client.

    Args:
        connection_url (str): MongoDB connection URI. defined in .env in constants module
    """
    try:
        client = MongoClient(connection_url)
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

    client = get_mongo_client(constants.MONGO_URI)
    collection = client[db][target_collection]

    if target_collection == "kengrams":
        pipeline = queries.kengrams

    else:
        pipeline = queries.default

    cursor = collection.aggregate(pipeline)
    df = pd.DataFrame(list(cursor))

    client.close()

    if target_collection == "kengrams" and "anchorChange" in df.columns and "metadata" in df.columns:
        df = df.drop(columns=["anchorChange", "metadata"])

    return df
