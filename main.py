import pandas as pd
import streamlit as st

from graphs import make_network_graph
from mongo import get_globalstates_cards, get_globalstates_retrievalCount


def filter_graph_by_timestamp(df, start_time, end_time):
    # Filter DataFrame for nodes within the selected time range
    filtered_df = df[
        (df["metadata.timestamp"] >= start_time)
        & (df["metadata.timestamp"] <= end_time)
    ]
    return filtered_df


def make_network_graph_with_filter(df, start_time, end_time):
    # Filter the DataFrame by the selected time range
    filtered_df = filter_graph_by_timestamp(df, start_time, end_time)

    # Generate the graph
    return make_network_graph(filtered_df)


def main():
    st.title("AI Thought Network Visualization")

    # Load data
    st.header("Loading data...")
    df_gs_cards = get_globalstates_cards()
    df_gs_retrievalCount = get_globalstates_retrievalCount()

    # Merge DataFrames
    st.header("Merging data...")
    merged_df = pd.merge(df_gs_cards, df_gs_retrievalCount, on="id", how="left")
    merged_df = merged_df.dropna(subset=["metadata.timestamp"]).reset_index()

    # Ensure metadata.timestamp is a datetime
    merged_df["metadata.timestamp"] = merged_df["metadata.timestamp"].astype(int)
    merged_df["metadata.timestamp"] = pd.to_datetime(
        merged_df["metadata.timestamp"], unit="ms"
    )

    # Display DataFrame in Streamlit (optional)
    st.subheader("Merged DataFrame Preview")
    st.dataframe(merged_df)

    # Add a timestamp filter slider
    st.header("Filter by Timestamp")
    min_time = merged_df["metadata.timestamp"].min()
    max_time = merged_df["metadata.timestamp"].max()

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
    network_graph = make_network_graph_with_filter(merged_df, start_time, end_time)

    # Display the graph in Streamlit
    st.plotly_chart(network_graph, use_container_width=True)


if __name__ == "__main__":
    main()
