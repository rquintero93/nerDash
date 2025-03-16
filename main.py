"""
 Streamlit app for visualizing the AI Thought Network.

"""

import streamlit as st

from controllers.utils import (count_card_names, count_primary_colors,
                               get_cards_df)
from views.graphs import make_bar_chart, make_pie_chart


def main():
    st.set_page_config(page_title="AI Thought Network Visualization", layout="wide")
    st.title("AI Thought Network Visualization")

    # Load data
    st.header("Loading data...")
    df_cards = get_cards_df()

    # Calculate KPIs
    total_retrieval_count = df_cards['retrievalCount'].sum()
    total_count = df_cards['_id'].count()
    unique_users = df_cards['from'].nunique()
    unique_chats = df_cards['chatId'].nunique()

    # display KPIs in columns
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Total Cards", value=total_count)
    col2.metric(label="Total Retrievals", value=total_retrieval_count)
    col3.metric(label="Unique Users", value=unique_users)
    col4.metric(label="Total Chats", value=unique_chats)

    # Generate and display the charts in columns
    col5, col6, col7 = st.columns(3)
    with col5:
        st.subheader("Bot IDs")
        botid_pie_chart = make_pie_chart(data=df_cards, column='botId')
        st.plotly_chart(botid_pie_chart, use_container_width=True, on_select='rerun')
    with col6:
        st.subheader("Types")
        type_pie_chart = make_pie_chart(data=df_cards, column='type')
        st.plotly_chart(type_pie_chart, use_container_width=True)
 
    with col7:
        st.subheader("Actions")
        type_pie_chart = make_bar_chart(data=df_cards,column='action')
        st.plotly_chart(type_pie_chart, use_container_width=True)
 
    st.header("Primary Color Distribution")
    color_counter = count_primary_colors(data=df_cards,concept='colors')
    color_counter_bar_chart = make_bar_chart(data=color_counter)
    event = st.plotly_chart(color_counter_bar_chart, use_container_width=True, on_select='rerun')
    event
    col8, col9 = st.columns(2)
    with col8:
        st.header("Full Color Distribution")
        color_pie_chart = make_pie_chart(data=df_cards, column='colors')
        st.plotly_chart(color_pie_chart, use_container_width=True)

    
    with col9:
        st.header("Popular Card Names")
        name_counter = count_card_names(df_cards,'name')
        filtered_name_counter = dict(sorted(name_counter.items(), key=lambda item: item[1], reverse=True)[:20])
        name_counter_bar_chart = make_bar_chart(data=filtered_name_counter, orientation="h")
        st.plotly_chart(name_counter_bar_chart, use_container_width=True)

    st.header("Raw Data")
    st.dataframe(df_cards)

if __name__ == "__main__":
    main()
