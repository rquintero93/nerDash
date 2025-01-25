import pandas as pd
import streamlit as st

from graphs import make_network_graph
from mongo import get_globalstates_cards, get_globalstates_retrievalCount


def main():
    st.title("AI Thought Network Visualization")

    # Load data
    st.header("Loading data...")
    df_gs_cards = get_globalstates_cards()
    df_gs_retrievalCount = get_globalstates_retrievalCount()

    # Merge DataFrames
    st.header("Merging data...")
    merged_df = pd.merge(df_gs_cards, df_gs_retrievalCount, on="id", how="left")
    merged_df = merged_df.reset_index()

    # Ensure metadata.timestamp is a datetime
    merged_df["metadata.timestamp"] = merged_df["metadata.timestamp"].astype(int)
    merged_df["metadata.timestamp"] = pd.to_datetime(
        merged_df["metadata.timestamp"], unit="ms"
    )

    # Generate the network graph
    st.header("Generating the network graph...")
    network_graph = make_network_graph(merged_df)

    # Display the graph in Streamlit
    st.plotly_chart(network_graph, use_container_width=True)


if __name__ == "__main__":
    main()
