import json

import pandas as pd

from graphs import make_agg_network_graph

# from chromadb import get_chroma
from mongo import get_globalstates_cards, get_globalstates_retrievalCount

pd.set_option("display.max_columns", None)

df_ragdb_gs_cards = get_globalstates_cards()
df_ragdb_gs_retrievalCount = get_globalstates_retrievalCount()
df_nerdb_gs_cards = get_globalstates_cards(db="nerDB")
df_nerdb_gs_retrievalCount = get_globalstates_retrievalCount(db="nerDB")

# chromadb = get_chroma(limit=20000, offset=293)
# chromadb = chromadb.dropna(subset=["timestamp"])

ragdb_merged_df = pd.merge(
    df_ragdb_gs_cards, df_ragdb_gs_retrievalCount, on="id", how="left"
)
ragdb_merged_df = ragdb_merged_df.dropna(subset=["metadata.timestamp"]).reset_index()

# Ensure metadata.timestamp is converted to Python datetime
ragdb_merged_df["metadata.timestamp"] = pd.to_datetime(
    ragdb_merged_df["metadata.timestamp"].astype(int), unit="ms"
).dt.to_pydatetime()

nerdb_merged_df = pd.merge(
    df_nerdb_gs_cards, df_nerdb_gs_retrievalCount, on="id", how="left"
)
nerdb_merged_df = nerdb_merged_df.dropna(subset=["metadata.timestamp"]).reset_index()

# Ensure metadata.timestamp is converted to Python datetime
nerdb_merged_df["metadata.timestamp"] = pd.to_datetime(
    nerdb_merged_df["metadata.timestamp"].astype(int), unit="ms"
).dt.to_pydatetime()

mongo_merge_df = pd.concat([nerdb_merged_df, ragdb_merged_df])

# chromadb["timestamp"] = (
#     chromadb["timestamp"].astype(int) if "timestamp" in chromadb.columns else None
# )
#
# chromadb["timestamp"] = (
#     pd.to_datetime(chromadb["timestamp"], unit="ms")
#     if "timestamp" in chromadb.columns
#     else None
# )

# Generate the network graph
# network_graph = make_network_graph(merged_df)
# network_graph.show()


def concat_unique(series):
    if series.dtype == "object" and isinstance(series.iloc[0], list):
        # Flatten the list of lists and remove duplicates
        return json.dumps(
            list(set([item for sublist in series.dropna() for item in sublist]))
        )
    elif series.dtype == "object" and isinstance(series.iloc[0], str):
        # Split the strings by "; " and remove duplicates
        return json.dumps(
            list(
                set(
                    [
                        item
                        for sublist in series.dropna()
                        for item in sublist.split("; ")
                    ]
                )
            )
        )
    else:
        return json.dumps(list(set(series.dropna())))


### Updated Aggregation Logic

# Convert the timestamp column to string
mongo_merge_df["metadata.timestamp"] = mongo_merge_df["metadata.timestamp"].astype(str)

# Define the aggregation functions for each column
agg_funcs = {
    "retrievalCount": "sum",
    "id": concat_unique,
    "metadata.data.colors": concat_unique,
    "metadata.data.manaCost": concat_unique,
    "metadata.data.type": concat_unique,
    "metadata.data.subtypes": concat_unique,
    "metadata.data.text": concat_unique,
    "metadata.data.flavorText": concat_unique,
    "metadata.data.power": concat_unique,
    "metadata.data.toughness": concat_unique,
    "metadata.timestamp": concat_unique,
    "metadata.chatId": concat_unique,
    "metadata.userId": concat_unique,
    "metadata.botId": concat_unique,
    "metadata.relatedCards": concat_unique,
    "metadata.relatedLore": concat_unique,
}

# Group by 'metadata.data.name' and aggregate
mongo_agg_df = mongo_merge_df.groupby("metadata.data.name").agg(agg_funcs)

# Reset index if needed
mongo_agg_df = mongo_agg_df.reset_index()

network_graph = make_agg_network_graph(mongo_agg_df)
network_graph.show()
