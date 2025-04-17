"""
Functions to explore MongoDB database.
"""

import pandas as pd
from loguru import logger
from pymongo import MongoClient

from models import queries
from utils import constants

# Configure Loguru
logger.remove()  # Remove default logger to customize settings
logger.add(
    "logs/mongo_logs.log",
    rotation="10MB",
    level="INFO",
    format="{time} {level} {message}",
)


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
                logger.info("MongoDB connected successfully!")
            except Exception as e:
                logger.error(f"Error connecting to MongoDB: {e}")
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
        logger.info("MongoDB connection closed.")


# @st.cache_resource(ttl=3600, show_spinner=False)
def get_database(db_name: str) -> MongoClient:
    """
    Get a MongoDB database instance.

    Args:
        db_name (str): Name of the database.

    Returns:
        Database: MongoDB database instance.
    """

    client = MongoDBClient(constants.MONGO_URI).get_client()
    logger.info(f"Accessing database: {db_name}")
    return client[db_name]


# @st.cache_data(ttl=3600, show_spinner=False)
def get_mongo_cards(db: str, target_collection: str) -> pd.DataFrame:
    """
    Retrieve cards from the target collection using MongoDB aggregation.

    Args:
        db (str): The database name
        target_collection (str): The target collection to query

    Returns:
        pd.DataFrame: DataFrame containing the queried data.
    """

    logger.info(
        f"Fetching data from MongoDB | Database: {db}, Collection: {target_collection}"
    )

    collection = get_database(db)[target_collection]

    if target_collection == "kengrams":
        pipeline = queries.kengrams
    else:
        pipeline = queries.default

    cursor = collection.aggregate(pipeline)
    df = pd.DataFrame(list(cursor))

    logger.info(f"Retrieved {len(df)} records from {target_collection}")

    return df
