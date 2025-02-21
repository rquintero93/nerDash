
import streamlit as st

from graphs import make_bar_chart, make_pie_chart
from mongo import get_mongo_cards


def main():
    st.set_page_config(page_title="AI Thought Network Visualization", layout="wide")
    st.title("AI Thought Network Visualization")

    # Load data
    st.header("Loading data (be patient)...")
    df_ragdb_gs_cards = get_mongo_cards(db="ragDB",target_collection="kengrams")
    # df_ragdb_gs_retrievalCount = get_globalstates_retrievalCount()
    # df_nerdb_gs_cards = get_globalstates_cards(db="nerDB")
    # df_nerdb_gs_retrievalCount = get_globalstates_retrievalCount(db="nerDB")
    # print(df_ragdb_gs_cards.columns)

    st.dataframe(df_ragdb_gs_cards)

    # Generate and display the pie charts
    st.header("Distribution of Bot IDs")
    botid_pie_chart = make_pie_chart(df_ragdb_gs_cards,'botId')
    st.plotly_chart(botid_pie_chart, use_container_width=True)
 
    st.header("Distribution of types")
    type_pie_chart = make_pie_chart(df_ragdb_gs_cards,'type')
    st.plotly_chart(type_pie_chart, use_container_width=True)
 
    st.header("Distribution of actions")
    type_pie_chart = make_bar_chart(df_ragdb_gs_cards,'action')
    st.plotly_chart(type_pie_chart, use_container_width=True)
 
    # st.header("Merging data...")
    # ragdb_merged_df = pd.merge(
    #     df_ragdb_gs_cards, df_ragdb_gs_retrievalCount, on="id", how="left"
    # )
    # ragdb_merged_df = ragdb_merged_df.dropna(
    #     subset=["metadata.timestamp"]
    # ).reset_index()
    #
    # # Ensure metadata.timestamp is converted to Python datetime
    # ragdb_merged_df["metadata.timestamp"] = pd.to_datetime(
    #     ragdb_merged_df["metadata.timestamp"].astype(int), unit="ms"
    # ).dt.to_pydatetime()
    #
    # nerdb_merged_df = pd.merge(
    #     df_nerdb_gs_cards, df_nerdb_gs_retrievalCount, on="id", how="left"
    # )
    # nerdb_merged_df = nerdb_merged_df.dropna(
    #     subset=["metadata.timestamp"]
    # ).reset_index()
    #
    # # Ensure metadata.timestamp is converted to Python datetime
    # nerdb_merged_df["metadata.timestamp"] = pd.to_datetime(
    #     nerdb_merged_df["metadata.timestamp"].astype(int), unit="ms"
    # ).dt.to_pydatetime()
    #
    # mongo_merge_df = pd.concat([nerdb_merged_df, ragdb_merged_df])
    #
    # def ensure_list(column):
    #     """
    #     Ensure all values in the column are lists. If a value is not a list,
    #     convert it to a list with the value as the only item.
    #     """
    #     return column.apply(lambda x: x if isinstance(x, list) else [x])
    #
    # # Apply the function to the metadata.data.colors column
    # mongo_merge_df["metadata.data.colors"] = ensure_list(
    #     mongo_merge_df["metadata.data.colors"]
    # )
    #
    # # Add a timestamp filter slider
    # st.header("Filter by Timestamp (heavy operation, will take time)...")
    # min_time = mongo_merge_df["metadata.timestamp"].min()
    # max_time = mongo_merge_df["metadata.timestamp"].max()
    #
    # # Convert min_time and max_time to datetime.datetime explicitly
    # min_time = datetime.datetime.fromisoformat(min_time.isoformat())
    # max_time = datetime.datetime.fromisoformat(max_time.isoformat())
    #
    # # Add a Streamlit slider for the timestamp range
    # start_time, end_time = st.slider(
    #     "Select Timestamp Range",
    #     min_value=min_time,
    #     max_value=max_time,
    #     value=(min_time, max_time),  # Default range is the full range
    #     format="YYYY-MM-DD HH:mm:ss",
    # )
    #
    # filtered_df = mongo_merge_df[
    #     (mongo_merge_df["metadata.timestamp"] >= start_time)
    #     & (mongo_merge_df["metadata.timestamp"] <= end_time)
    # ]
    #
    # # Display the selected time range
    # st.write(f"Selected time range: {start_time} to {end_time}")
    #
    #
    # # apply a filter by card ID
    # st.header("Filter by Card ID")
    #
    # # Create a filter dropdown with available ID values
    # id_filter = st.selectbox("Select an ID:", options=[None] + filtered_df["id"].tolist())
    #
    # # Filter DataFrame based on selection
    # if id_filter:
    #     id_filtered_df = filtered_df[
    #         (filtered_df["id"] == id_filter) | 
    #         (filtered_df["metadata.relatedCards"].apply(lambda x: id_filter in x if isinstance(x, list) else False))
    #     ]
    # else:
    #     id_filtered_df = filtered_df
    #
    # # apply a filter by card name
    # st.header("Filter by Card Name")
    #
    # # Create a filter dropdown with available ID values
    # id_filter = st.selectbox("Select a Card Name:", options=[None] + sorted(list(set(id_filtered_df["metadata.data.name"].tolist()))))
    #
    # # Filter DataFrame based on selection
    # if id_filter:
    #     name_filtered_df = id_filtered_df[
    #         (id_filtered_df["metadata.data.name"] == id_filter)
    #     ]
    # else:
    #     name_filtered_df = id_filtered_df
    #
    # # Display DataFrame in Streamlit 
    # st.subheader("Thought Level Data")
    # name_filtered_df["metadata.data.colors"] = name_filtered_df["metadata.data.colors"].apply(clean_colors)
    # name_filtered_df["metadata.data.manaCost"] = name_filtered_df["metadata.data.manaCost"].apply(clean_mana_cost)
    # st.dataframe(name_filtered_df)
    #
    # # Generate the network graph based on the selected time range
    # st.header("Generating the Thought Level Graph...")
    # if name_filtered_df.empty or name_filtered_df.shape[0] == 1:
    #     st.write("No network data to display.")
    # else:
    #     network_graph = make_network_graph(name_filtered_df)
    #
    # try:
    #     if network_graph is None:
    #         st.write("No network data to display.")
    #     # Display the graph in Streamlit
    #     else:
    #         st.plotly_chart(network_graph, use_container_width=True)
    # except Exception:
    #     st.write("No network data to display.")
    #
    # st.subheader("Concept Network Data")
    # if name_filtered_df.empty or name_filtered_df.shape[0] == 1:
    #     st.write("No network data to display.")
    # else:
    #     agg_df = make_agg_df(name_filtered_df)
    #     agg_df["metadata.data.colors"] = agg_df["metadata.data.colors"].apply(clean_colors)
    #     agg_df["metadata.data.manaCost"] = agg_df["metadata.data.manaCost"].apply(clean_mana_cost)
    #
    #     # Generate the network graph based on the selected time range
    #     st.dataframe(make_network_dataframe(agg_df))
    #     st.header("Generating the Concept Level Graph...")
    #
    #
    #     network_graph = make_agg_network_graph(agg_df)
    #
    # try:
    #     if network_graph is None:
    #         st.write("No network data to display.")
    #     else:
    #     # Display the graph in Streamlit
    #         st.plotly_chart(network_graph, use_container_width=True)
    # except Exception:
    #     st.write("No network data to display.")


if __name__ == "__main__":
    main()
