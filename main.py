import datetime

import pandas as pd
import streamlit as st

from graphs import make_network_graph
from mongo import get_globalstates_cards, get_globalstates_retrievalCount


def main():
    st.title("AI Thought Network Visualization")

    # Load data
    st.header("Loading data...")
    df_ragdb_gs_cards = get_globalstates_cards()
    df_ragdb_gs_retrievalCount = get_globalstates_retrievalCount()
    df_nerdb_gs_cards = get_globalstates_cards(db="nerDB")
    df_nerdb_gs_retrievalCount = get_globalstates_retrievalCount(db="nerDB")

    # Merge DataFrames
    st.header("Merging data...")
    ragdb_merged_df = pd.merge(
        df_ragdb_gs_cards, df_ragdb_gs_retrievalCount, on="id", how="left"
    )
    ragdb_merged_df = ragdb_merged_df.dropna(
        subset=["metadata.timestamp"]
    ).reset_index()

    # Ensure metadata.timestamp is converted to Python datetime
    ragdb_merged_df["metadata.timestamp"] = pd.to_datetime(
        ragdb_merged_df["metadata.timestamp"].astype(int), unit="ms"
    ).dt.to_pydatetime()

    nerdb_merged_df = pd.merge(
        df_nerdb_gs_cards, df_nerdb_gs_retrievalCount, on="id", how="left"
    )
    nerdb_merged_df = nerdb_merged_df.dropna(
        subset=["metadata.timestamp"]
    ).reset_index()

    # Ensure metadata.timestamp is converted to Python datetime
    nerdb_merged_df["metadata.timestamp"] = pd.to_datetime(
        nerdb_merged_df["metadata.timestamp"].astype(int), unit="ms"
    ).dt.to_pydatetime()

    mongo_merge_df = pd.concat([ragdb_merged_df, nerdb_merged_df])

    # Display DataFrame in Streamlit (optional)
    st.subheader("Data Preview")
    st.dataframe(mongo_merge_df)

    # Add a timestamp filter slider
    st.header("Filter by Timestamp")
    min_time = mongo_merge_df["metadata.timestamp"].min()
    max_time = mongo_merge_df["metadata.timestamp"].max()

    # Convert min_time and max_time to datetime.datetime explicitly
    min_time = datetime.datetime.fromisoformat(min_time.isoformat())
    max_time = datetime.datetime.fromisoformat(max_time.isoformat())

    # Add a Streamlit slider for the timestamp range
    start_time, end_time = st.slider(
        "Select Timestamp Range",
        min_value=min_time,
        max_value=max_time,
        value=(min_time, max_time),  # Default range is the full range
        format="YYYY-MM-DD HH:mm:ss",
    )

    # Display the selected time range
    st.write(f"Selected time range: {start_time} to {end_time}")

    # Generate the network graph based on the selected time range
    st.header("Generating the network graph...")
    filtered_df = mongo_merge_df[
        (mongo_merge_df["metadata.timestamp"] >= start_time)
        & (mongo_merge_df["metadata.timestamp"] <= end_time)
    ]
    network_graph = make_network_graph(filtered_df)

    # Display the graph in Streamlit
    st.plotly_chart(network_graph, use_container_width=True)


if __name__ == "__main__":
    main()
