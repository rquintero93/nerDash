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


def star_as_dataframe(collection, filter_query=None) -> pd.DataFrame:
    """
    Fetch MongoDB data and convert it into a Pandas DataFrame.
    """
    try:
        cursor = collection.find(filter_query or {})
        df = pd.DataFrame(list(cursor))
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()


def get_globalstates_cards(
    db: str = "nerDB", target_collection: str = "globalstates"
) -> pd.DataFrame:
    """
    Retrieve cards from the globalstates collection.
    """
    client = get_mongo_client()
    db = client[db]
    collection = db[target_collection]

    df = star_as_dataframe(collection)

    if df.empty or "cards" not in df.columns:
        print("The 'cards' column is missing or the DataFrame is empty.")
        return pd.DataFrame()

    # Explode the "cards" column
    df = df.explode("cards")

    cards_data = df["cards"].apply(
        lambda x: (
            {"id": list(x.keys())[0], "details": list(x.values())[0]}
            if isinstance(x, dict)
            else None
        )
    )

    cards_data = cards_data.dropna()

    if not cards_data.empty:
        cards_df = pd.DataFrame(cards_data.tolist())
        normalized_df = pd.json_normalize(cards_df["details"])
        normalized_df["id"] = cards_df["id"]
    else:
        print("No valid 'cards_data' found.")
        normalized_df = pd.DataFrame()

    if "pageContent" in normalized_df.columns:
        normalized_df = normalized_df.drop(columns=["pageContent"])

    client.close()
    return normalized_df


def get_globalstates_retrievalCount(
    db: str = "nerDB", target_collection: str = "globalstates"
) -> pd.DataFrame:
    """
    Retrieve retrievalCount data from the globalstates collection.
    """
    client = get_mongo_client()
    db = client[db]
    collection = db[target_collection]

    df = star_as_dataframe(collection)

    if df.empty or "retrievalCount" not in df.columns:
        print("The 'retrievalCount' field is missing or the DataFrame is empty.")
        return pd.DataFrame()

    retrieval_data = df["retrievalCount"].iloc[0]
    df = pd.DataFrame(list(retrieval_data.items()), columns=["id", "retrievalCount"])

    client.close()
    return df


def get_history(db: str = "nerDB", target_collection: str = "history") -> pd.DataFrame:
    """
    Retrieve the history collection.
    """
    client = get_mongo_client()
    db = client[db]
    collection = db[target_collection]

    df = star_as_dataframe(collection)

    client.close()
    return df
