import pandas as pd

from chromadb import get_chroma

pd.set_option("display.max_columns", None)

# df_gs_cards = get_globalstates_cards()
# df_gs_retrievalCount = get_globalstates_retrievalCount()

chromadb = get_chroma(limit=20000, offset=293)
chromadb = chromadb.dropna(subset=["timestamp"])
# chromadb["timestamp"].replace("", pd.NA, inplace=True)
# chromadb = chromadb.dropna(subset=["timestamp"])
# Merge DataFrames
# merged_df = pd.merge(df_gs_cards, df_gs_retrievalCount, on="id", how="left")
# merged_df = merged_df.reset_index()
# merged_df = merged_df.dropna()
#
# # Ensure metadata.timestamp is a datetime
# merged_df["metadata.timestamp"] = (
#     merged_df["metadata.timestamp"].astype(int)
#     if "metadata.timestamp" in merged_df.columns
#     else None
# )
#
# merged_df["metadata.timestamp"] = (
#     pd.to_datetime(merged_df["metadata.timestamp"], unit="ms")
#     if "metadata.timestamp" in merged_df.columns
#     else None
# )
chromadb["timestamp"] = (
    chromadb["timestamp"].astype(int) if "timestamp" in chromadb.columns else None
)

chromadb["timestamp"] = (
    pd.to_datetime(chromadb["timestamp"], unit="ms")
    if "timestamp" in chromadb.columns
    else None
)

# Generate the network graph
# network_graph = make_network_graph(merged_df)
# network_graph.show()
