import pandas as pd

from graphs import make_network_graph
from mongo import get_globalstates_cards, get_globalstates_retrievalCount
from chromadb import get_chroma

pd.set_option("display.max_columns", None)

df_gs_cards = get_globalstates_cards()
df_gs_retrievalCount = get_globalstates_retrievalCount()

chromadb = get_chroma()
# Merge DataFrames
merged_df = pd.merge(df_gs_cards, df_gs_retrievalCount, on="id", how="left")
merged_df = merged_df.reset_index()

# Ensure metadata.timestamp is a datetime
merged_df["metadata.timestamp"] = (
    merged_df["metadata.timestamp"].astype(int)
    if "metadata.timestamp" in merged_df.columns
    else None
)

merged_df["metadata.timestamp"] = (
    pd.to_datetime(merged_df["metadata.timestamp"], unit="ms")
    if "metadata.timestamp" in merged_df.columns
    else None
)

# Generate the network graph
network_graph = make_network_graph(merged_df)
network_graph.show()
