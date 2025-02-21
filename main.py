"""
 Streamlit app for visualizing the AI Thought Network.

"""

import streamlit as st

from graphs import make_bar_chart, make_pie_chart
from mongo import get_mongo_cards
from utils import clean_colors, count_concept


def main():
    st.set_page_config(page_title="AI Thought Network Visualization", layout="wide")
    st.title("AI Thought Network Visualization")

    # Load data
    st.header("Loading data...")
    df_cards = get_mongo_cards(db="ragDB",target_collection="kengrams")
    df_cards['colors'] = df_cards['colors'].apply(lambda x: clean_colors(x))

    # Calculate KPIs
    total_retrieval_count = df_cards['retrievalCount'].sum()
    total_count = df_cards['_id'].count()
    unique_users = df_cards['from'].nunique()
    unique_chats = df_cards['chatId'].nunique()

    st.header("Network KPIs")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Total Count", value=total_count)
    col2.metric(label="Total Retrievals", value=total_retrieval_count)
    col3.metric(label="Unique Users", value=unique_users)
    col4.metric(label="Total Chats", value=unique_chats)

    # Generate and display the charts in columns
    col5, col6, col7 = st.columns(3)
    with col5:
        st.subheader("Bot IDs")
        botid_pie_chart = make_pie_chart(df_cards, 'botId')
        st.plotly_chart(botid_pie_chart, use_container_width=True)
    with col6:
        st.subheader("Types")
        type_pie_chart = make_pie_chart(df_cards, 'type')
        st.plotly_chart(type_pie_chart, use_container_width=True)
 
    with col7:
        st.subheader("Actions")
        type_pie_chart = make_bar_chart(df_cards,'action')
        st.plotly_chart(type_pie_chart, use_container_width=True)
 
    st.header("Primary Color Distribution")

    color_counter = count_concept(df_cards,'colors')
    color_counter_bar_chart = make_bar_chart(color_counter)
    st.plotly_chart(color_counter_bar_chart, use_container_width=True)

    st.header("Full Color Distribution")

    color_pie_chart = make_pie_chart(df_cards, 'colors')
    st.plotly_chart(color_pie_chart, use_container_width=True)
    st.header("Raw Data")
    st.dataframe(df_cards)

if __name__ == "__main__":
    main()
