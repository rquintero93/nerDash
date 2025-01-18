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

# Check if the .env file exists at the specified path
if not os.path.exists(dotenv_path):
    print(f".env file not found at: {dotenv_path}")
else:
    success = load_dotenv(dotenv_path)
    if not success:
        print("Failed to load .env file")
    else:
        print(".env file loaded successfully")


def get_mongo_client():
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


def star_as_dataframe(collection):
    """
    Fetch MongoDB data and convert it into a Pandas DataFrame.
    """
    try:
        cursor = collection.find()
        df = pd.DataFrame(list(cursor))
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()


def get_globalstates_cards():
    """
    Returns: DataFrame with the cards from the globalstates collection.
    """
    client = get_mongo_client()
    db = client["nerDB"]
    collection = db["globalstates"]

    df = star_as_dataframe(collection)

    df = df.head(1)

    # Expand JSON column into rows
    json_df = df.explode("cards")

    # Convert the JSON objects into separate columns
    df = pd.json_normalize(json_df["cards"])

    client.close()

    return df


def get_globalstates_retrievalCount():

    client = get_mongo_client()
    db = client["nerDB"]
    collection = db["globalstates"]

    df = star_as_dataframe(collection)

    df = df.head(1)

    # Expand JSON column into rows
    df = df.explode("retrievalCount")

    client.close()

    return df


def get_history():

    client = get_mongo_client()
    db = client["nerDB"]
    collection = db["history"]

    df = star_as_dataframe(collection)

    client.close()

    return df


# define main tables
df_gs_cards = get_globalstates_cards()
df_gs_retrievalCount = get_globalstates_retrievalCount()
df_history = get_history()
