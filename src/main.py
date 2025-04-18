"""
Streamlit app for visualizing the AI Thought Network.

"""

import pandas as pd
import streamlit as st

from controllers import count_card_names, get_cards_df
from controllers.nlp import (
    analyze_sentiment_emotion,
    build_similarity_graph,
    cluster_concepts,
    compute_embeddings,
    reduce_embeddings_tsne,
)
from views import (
    make_bar_chart,
    make_line_chart,
    make_pie_chart,
    make_sentiment_over_time,
    visualize_graph,
    visualize_tsne,
)


def main():
    st.set_page_config(page_title="AI Thought Network Visualization", layout="wide")
    st.title("AI Thought Network Visualization")

    # Load data
    st.header("Loading data...")
    df_cards = get_cards_df()

    # Calculate KPIs
    total_retrieval_count = df_cards["retrievalCount"].sum()
    total_count = df_cards["_id"].count()
    unique_concepts = df_cards["name"].nunique()
    # unique_chats = df_cards['chatId'].nunique()

    # display KPIs in columns
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Cards", value=total_count)
    col2.metric(label="Total Retrievals", value=total_retrieval_count)
    col3.metric(label="Total Concepts", value=unique_concepts)
    # col4.metric(label="Total Chats", value=unique_chats)

    # Generate and display the charts in columns
    col5, col6, col7 = st.columns(3)
    with col5:
        st.subheader("Cards Created Over Time")
        createdAt_timeline_chart = make_line_chart(
            data=df_cards, y="createdAt", x="_id"
        )
        st.plotly_chart(createdAt_timeline_chart, use_container_width=True)

    with col6:
        st.subheader("Concepts Over Time")
        updatedAt_timeline_chart = make_line_chart(
            data=df_cards, y="updatedAt", x="name"
        )
        st.plotly_chart(updatedAt_timeline_chart, use_container_width=True)

    with col7:
        st.subheader("Types")
        type_pie_chart = make_pie_chart(data=df_cards, column="type")
        st.plotly_chart(type_pie_chart, use_container_width=True)

    st.header("Popular Concepts")
    name_counter = count_card_names(df_cards, "name")
    filtered_name_counter = dict(
        sorted(name_counter.items(), key=lambda item: item[1], reverse=True)[:20]
    )
    name_counter_bar_chart = make_bar_chart(data=filtered_name_counter, orientation="h")
    st.plotly_chart(name_counter_bar_chart, use_container_width=True)

    st.header("Concept Clustering and Similarity Graph... (please wait)")
    col10, col11 = st.columns(2)
    with col10:
        card_names = list(set(df_cards["name"].tolist()))
        embeddings, st_name_model = compute_embeddings(card_names)

        df_embeddings = pd.DataFrame(card_names, columns=["name"])
        df_embeddings["cluster"] = cluster_concepts(embeddings, num_clusters=8)

        reduced_embeddings = reduce_embeddings_tsne(embeddings)
        tsne_graph = visualize_tsne(
            reduced_embeddings, df_embeddings["cluster"], card_names
        )
        st.subheader("Embedding Clustering")
        st.plotly_chart(tsne_graph, use_container_width=True)

    with col11:
        similarity_graph = build_similarity_graph(
            card_names, embeddings, threshold=0.5, max_edges=10000
        )
        similarity_chart = visualize_graph(similarity_graph, card_names)
        st.subheader("Concept Similarity Graph")
        st.plotly_chart(similarity_chart, use_container_width=True)

    st.header("Sentiment and Emotion Analysis... (please wait a lot)")
    # 3. Sentiment and Emotion Analysis
    sentiments = analyze_sentiment_emotion(df_cards["flavorText"].tolist())
    df_cards["sentiment"] = [s["label"] for s in sentiments]

    sentimer_over_time_graph = make_sentiment_over_time(df_cards.copy(), sentiments)
    st.subheader("Average Mood Over Time")
    st.plotly_chart(sentimer_over_time_graph, use_container_width=True)

    st.header("Raw Data")
    st.dataframe(df_cards)


if __name__ == "__main__":
    main()
