import datetime

import pandas as pd
import streamlit as st

from graphs import (make_agg_network_graph, make_network_dataframe,
                    make_network_graph)
from mongo import get_globalstates_cards, get_globalstates_retrievalCount


def make_agg_df(mongo_merge_df):

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
    mongo_merge_df["metadata.timestamp"] = mongo_merge_df["metadata.timestamp"].astype(
        str
    )

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
    mongo_agg_df = mongo_merge_df.groupby("metadata.data.name", sort=False).agg(
        agg_funcs
    )

    # Reset index if needed
    mongo_agg_df = mongo_agg_df.reset_index()

    return mongo_agg_df


def main():
    st.set_page_config(page_title="AI Thought Network Visualization", layout="wide")
    st.title("AI Thought Network Visualization")

    # Load data
    st.header("Loading data (be patient)...")
    df_ragdb_gs_cards = get_globalstates_cards()
    df_ragdb_gs_retrievalCount = get_globalstates_retrievalCount()
    df_nerdb_gs_cards = get_globalstates_cards(db="nerDB")
    df_nerdb_gs_retrievalCount = get_globalstates_retrievalCount(db="nerDB")

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

    mongo_merge_df = pd.concat([nerdb_merged_df, ragdb_merged_df])

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

    # Add a timestamp filter slider
    st.header("Filter by Timestamp (heavy operation, will take time)...")
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

    filtered_df = mongo_merge_df[
        (mongo_merge_df["metadata.timestamp"] >= start_time)
        & (mongo_merge_df["metadata.timestamp"] <= end_time)
    ]

    # Display the selected time range
    st.write(f"Selected time range: {start_time} to {end_time}")


    # apply a filter by card ID
    st.header("Filter by Card ID")

# Create a filter dropdown with available ID values
    id_filter = st.selectbox("Select an ID:", options=[None] + mongo_merge_df["id"].tolist())

# Filter DataFrame based on selection
    if id_filter:
        filtered_df = mongo_merge_df[
            (mongo_merge_df["id"] == id_filter) | 
            (mongo_merge_df["metadata.relatedCards"].apply(lambda x: id_filter in x if isinstance(x, list) else False))
        ]
    else:
        filtered_df = mongo_merge_df

    # Display DataFrame in Streamlit 
    st.subheader("Thought Level Data")
    st.dataframe(filtered_df)

    # Generate the network graph based on the selected time range
    st.header("Generating the Thought Level Graph...")
    if filtered_df.empty or filtered_df.shape[0] == 1:
        st.write("No network data to display.")
    else:
        network_graph = make_network_graph(filtered_df)

    # Display the graph in Streamlit
    st.plotly_chart(network_graph, use_container_width=True)

    st.subheader("Concept Network Data")
    if filtered_df.empty or filtered_df.shape[0] == 1:
        st.write("No network data to display.")
    else:
        agg_df = make_agg_df(filtered_df)
        st.dataframe(make_network_dataframe(agg_df))
        # Generate the network graph based on the selected time range
        st.header("Generating the Concept Level Graph...")

        network_graph = make_agg_network_graph(agg_df)
        print(type(network_graph))
        # Display the graph in Streamlit
        st.plotly_chart(network_graph, use_container_width=True)


if __name__ == "__main__":
    main()
