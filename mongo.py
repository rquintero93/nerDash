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

    if "cards" in df.columns:
        # Explode the "cards" column to process each card separately
        df = df.explode("cards")

        # Extract both the ID and card details
        cards_data = df["cards"].apply(
            lambda x: (
                {"id": list(x.keys())[0], "details": list(x.values())[0]}
                if isinstance(x, dict)
                else None
            )
        )

        cards_data = cards_data.dropna()

        # Create a new DataFrame with the ID and normalized details
        if not cards_data.empty:
            cards_df = pd.DataFrame(
                cards_data.tolist()
            )  # Split "id" and "details" into columns
            normalized_df = pd.json_normalize(cards_df["details"])
            normalized_df["id"] = cards_df[
                "id"
            ]  # Add the ID back to the normalized DataFrame
        else:
            print("No valid 'cards_data' found.")
            normalized_df = pd.DataFrame()
    else:
        print("The 'cards' column is missing.")
        normalized_df = pd.DataFrame()

    client.close()

    normalized_df = normalized_df.drop(columns=["pageContent"])
    return normalized_df


def get_globalstates_retrievalCount():

    client = get_mongo_client()
    db = client["nerDB"]
    collection = db["globalstates"]

    df = star_as_dataframe(collection)
    retrieval_data = df["retrievalCount"].iloc[0]  # Assuming only one document
    # Convert the JSON object into a DataFrame
    df = pd.DataFrame(list(retrieval_data.items()), columns=["id", "retrievalCount"])

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
# df_history = get_history()

merged_df = pd.merge(df_gs_cards, df_gs_retrievalCount, on="id", how="left")
