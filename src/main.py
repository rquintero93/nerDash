"""
Streamlit app for visualizing the AI Thought Network.

"""

import streamlit as st

from controllers import count_card_names, get_cards_df
from controllers.nlp import (
    analyze_sentiment_emotion,
    cluster_concepts,
    compute_embeddings,
    model_topics,
    reduce_embeddings_tsne,
)
from views import (
    make_bar_chart,
    make_line_chart,
    make_pie_chart,
    make_sentiment_over_time,
    visualize_topic_heatmap,
    visualize_topic_hierarchy,
    visualize_tsne,
    visulize_topic_barchart,
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
    col3.metric(label="Unique Concepts", value=unique_concepts)
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

    st.header("Popular Card Names")
    name_counter = count_card_names(df_cards, "name")
    filtered_name_counter = dict(
        sorted(name_counter.items(), key=lambda item: item[1], reverse=True)[:20]
    )
    name_counter_bar_chart = make_bar_chart(data=filtered_name_counter, orientation="h")
    st.plotly_chart(name_counter_bar_chart, use_container_width=True)

    descriptions = df_cards["flavorText"].tolist()

    # 1. Compute embeddings using SentenceTransformer
    # 5. Visualize embeddings with t-SNE (with optional clustering)
    embeddings, st_model = compute_embeddings(descriptions)

    staging = cluster_concepts(descriptions, num_clusters=8, len_df=df_cards.shape[0])

    df_cards = df_cards.head(staging.shape[0])
    df_cards["cluster"] = staging

    reduced_embeddings = reduce_embeddings_tsne(embeddings)
    tsne_graph = visualize_tsne(reduced_embeddings, df_cards["cluster"])
    st.plotly_chart(tsne_graph, use_container_width=True)

    # 2. Topic Modeling with BERTopic
    topics, topic_model = model_topics(descriptions)
    df_cards["topic"] = topics

    st.plotly_chart(visulize_topic_barchart(topic_model), use_container_width=True)
    st.plotly_chart(visualize_topic_heatmap(topic_model), use_container_width=True)
    st.plotly_chart(visualize_topic_hierarchy(topic_model), use_container_width=True)

    # 3. Sentiment and Emotion Analysis
    sentiments, emotions = analyze_sentiment_emotion(descriptions)
    # Store results in the dataframe for further analysis
    df_cards["sentiment"] = [s["label"] for s in sentiments]
    df_cards["emotion"] = [e["label"] for e in emotions]

    sentimer_over_time_graph = make_sentiment_over_time(df_cards.copy(), sentiments)
    st.plotly_chart(sentimer_over_time_graph, use_container_width=True)

    st.header("Raw Data")
    st.dataframe(df_cards)


if __name__ == "__main__":
    main()
