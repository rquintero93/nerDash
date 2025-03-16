"""
Functions to explore MongoDB database.
"""

import pandas as pd
from pymongo import MongoClient

import models.queries as queries
import utils.constants as constants


class MongoDBClient:
    """
    Singleton MongoDB Client to manage the connection.
    """
    _instance = None

    def __new__(cls, connection_url: str):
        if cls._instance is None:
            try:
                cls._instance = super(MongoDBClient, cls).__new__(cls)
                cls._instance.client = MongoClient(connection_url)
                print("MongoDB connected successfully!")
            except Exception as e:
                print(f"Error connecting to MongoDB: {e}")
                raise
        return cls._instance
    
    def get_client(self) -> MongoClient:
        """
        Return the MongoDB client instance.
        """
        return self.client

    def close(self):
        """
        Close the MongoDB client connection.
        """
        self.client.close()


def get_database(db_name: str) -> MongoClient:
    """
    Get a MongoDB database instance.

    Args:
        db_name (str): Name of the database.
    
    Returns:
        Database: MongoDB database instance.
    """
    client = MongoDBClient(constants.MONGO_URI).get_client()
    return client[db_name]

def get_mongo_cards(db: str, target_collection: str) -> pd.DataFrame:
    """
    Retrieve cards from the target collection using MongoDB aggregation.

    Args: 
        db (str): The database name
        target_collection (str): The target collection to query
    
    Returns:
        pd.DataFrame: DataFrame containing the queried data.
    """
    collection = get_database(db)[target_collection]
    
    if target_collection == "kengrams":
        pipeline = queries.kengrams
    else:
        pipeline = queries.default
    
    cursor = collection.aggregate(pipeline)
    df = pd.DataFrame(list(cursor))
    
    if target_collection == "kengrams" and "anchorChange" in df.columns and "metadata" in df.columns:
        df = df.drop(columns=["anchorChange", "metadata"])
    
    return df

