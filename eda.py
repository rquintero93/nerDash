import pandas as pd

from graphs import make_network_dataframe

# from chromadb import get_chroma
from mongo import get_globalstates_cards, get_globalstates_retrievalCount

pd.set_option("display.max_columns", None)

df_ragdb_gs_cards = get_globalstates_cards()
df_ragdb_gs_retrievalCount = get_globalstates_retrievalCount()
df_nerdb_gs_cards = get_globalstates_cards(db="nerDB")
df_nerdb_gs_retrievalCount = get_globalstates_retrievalCount(db="nerDB")

# chromadb = get_chroma(limit=20000, offset=293)
# chromadb = chromadb.dropna(subset=["timestamp"])
df_ragdb_gs_cards = df_ragdb_gs_cards.drop(columns=["pageContent"])
df_nerdb_gs_cards = df_nerdb_gs_cards.drop(columns=["pageContent"])
df_ragdb_gs_retrievalCount = df_ragdb_gs_retrievalCount.drop(columns=["_id"])
df_nerdb_gs_retrievalCount = df_nerdb_gs_retrievalCount.drop(columns=["_id"])


id_column_indexes = [
    i for i, col in enumerate(df_ragdb_gs_cards.columns) if col == "id"
]

df_ragdb_gs_cards.columns.values[id_column_indexes[1]] = "id_duplicate"
df_ragdb_gs_cards = df_ragdb_gs_cards.drop(columns=["id_duplicate"])

id_column_indexes = [
    i for i, col in enumerate(df_nerdb_gs_cards.columns) if col == "id"
]

df_nerdb_gs_cards.columns.values[id_column_indexes[1]] = "id_duplicate"
df_nerdb_gs_cards = df_nerdb_gs_cards.drop(columns=["id_duplicate"])

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

# for color in enumerate(mongo_merge_df["metadata.data.colors"]):
#     index, value = color
#     print(index, value, type(value))


def ensure_list(column):
    """
    Ensure all values in the column are lists. If a value is not a list,
    convert it to a list with the value as the only item.
    """
    return column.apply(lambda x: x if isinstance(x, list) else [x])


# Apply the function to the metadata.data.colors column
mongo_merge_df["metadata.data.colors"] = ensure_list(
    mongo_merge_df["metadata.data.colors"]
)

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
# network_graph = make_network_graph(mongo_merge_df)
# network_graph.show()


def concat_unique(series):
    """Ensure lists remain lists, and unique values are preserved."""
    if series.apply(lambda x: isinstance(x, list)).any():
        unique_items = set()
        result = []
        for sublist in series.dropna():
            for item in sublist:
                if item not in unique_items:
                    unique_items.add(item)
                    result.append(item)
        return result  # Keep as a list

    elif series.dtype == "object":
        seen = set()
        result = [
            item
            for sublist in series.dropna().astype(str)
            for item in sublist.split("; ")
            if not (item in seen or seen.add(item))
        ]
        return result  # Keep as list

    else:
        seen = set()
        return [x for x in series.dropna() if not (x in seen or seen.add(x))]


# Convert timestamp to datetime and sort
mongo_merge_df["metadata.timestamp"] = pd.to_datetime(
    mongo_merge_df["metadata.timestamp"]
)
mongo_merge_df = mongo_merge_df.sort_values("metadata.timestamp")

# Convert `id` column to string
mongo_merge_df["id"] = mongo_merge_df["id"].astype(str)
mongo_merge_df["metadata.timestamp"] = mongo_merge_df["metadata.timestamp"].astype(str)

# Define aggregation functions
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
    "metadata.timestamp": concat_unique,  # Ensures order from sorted dataframe
    "metadata.chatId": concat_unique,
    "metadata.userId": concat_unique,
    "metadata.botId": concat_unique,
    "metadata.relatedCards": concat_unique,
    "metadata.relatedLore": concat_unique,
}

# Group by 'metadata.data.name' and aggregate
mongo_agg_df = mongo_merge_df.groupby("metadata.data.name", sort=False).agg(agg_funcs)

# Reset index if needed
mongo_agg_df = mongo_agg_df.reset_index()

# network_graph = make_agg_network_graph(mongo_agg_df)
# network_graph.show()

network_df = make_network_dataframe(mongo_agg_df)
