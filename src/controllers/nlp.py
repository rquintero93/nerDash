"""
NLP Analysis functions

"""

import os
import pickle

import networkx as nx
import pandas as pd
import streamlit as st
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer, util
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from transformers import pipeline

pd.set_option("display.max_columns", None)
USE_CACHED = False


def compute_embeddings(
    descriptions,
    model_name="sentence-transformers/all-MiniLM-L12-v2",
    use_cached=USE_CACHED,
):
    cache_path = "models/embeddings.pkl"
    model_path = f"models/{model_name.replace('/', '_')}"

    if use_cached and os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            return pickle.load(f), SentenceTransformer(
                model_path if os.path.exists(model_path) else model_name
            )

    model = SentenceTransformer(model_name)
    embeddings = model.encode(descriptions, convert_to_tensor=True)

    # os.makedirs("models", exist_ok=True)
    # with open(cache_path, "wb") as f:
    #     pickle.dump(embeddings, f)
    #
    # # Save the model for future use
    # if not os.path.exists(model_path):
    #     model.save(model_path)

    return embeddings, model


@st.cache_resource(ttl=3600, show_spinner=False)
def model_topics(descriptions, use_cached=USE_CACHED):
    cache_path = "models/topics.pkl"
    model_path = "models/bertopic_model"

    if use_cached and os.path.exists(cache_path) and os.path.exists(model_path):
        with open(cache_path, "rb") as f:
            topics = pickle.load(f)
        topic_model = BERTopic.load(model_path)
        return topics, topic_model

    topic_model = BERTopic()
    topics, probs = topic_model.fit_transform(descriptions)

    # os.makedirs("models", exist_ok=True)
    # with open(cache_path, "wb") as f:
    #     pickle.dump(topics, f)
    # topic_model.save(model_path)

    return topics, topic_model


@st.cache_resource(ttl=3600, show_spinner=False)
def analyze_sentiment_emotion(descriptions, use_cached=USE_CACHED):
    cache_path = "models/sentiment_emotion.pkl"

    if use_cached and os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            return pickle.load(f)

    sentiment_pipeline = pipeline(
        "text-classification", model="tabularisai/multilingual-sentiment-analysis"
    )
    emotion_pipeline = pipeline(
        "text-classification", model="ayoubkirouane/BERT-Emotions-Classifier"
    )

    sentiments = [sentiment_pipeline(desc)[0] for desc in descriptions]
    emotions = [emotion_pipeline(desc)[0] for desc in descriptions]

    # os.makedirs("models", exist_ok=True)
    # with open(cache_path, "wb") as f:
    #     pickle.dump((sentiments, emotions), f)

    return sentiments, emotions


@st.cache_resource(ttl=3600, show_spinner=False)
def build_similarity_graph(concepts, embeddings, threshold=0.7):
    # Build a graph where each node is a concept and edges exist if similarity exceeds threshold
    G = nx.Graph()
    num_cards = len(concepts)

    for i in range(num_cards):
        G.add_node(i, concept=concepts[i])

    # Use cosine similarity from sentence-transformers util
    cosine_scores = util.cos_sim(embeddings, embeddings)

    for i in range(num_cards):
        for j in range(i + 1, num_cards):
            score = cosine_scores[i][j].item()
            if score > threshold:
                G.add_edge(i, j, weight=score)
    return G


def reduce_embeddings_tsne(embeddings, use_cached=USE_CACHED):
    cache_path = "models/tsne_embeddings.pkl"

    if use_cached and os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            return pickle.load(f)

    tsne = TSNE(n_components=2, perplexity=10, random_state=42, n_jobs=-1)
    embeddings_np = (
        embeddings.cpu().numpy() if hasattr(embeddings, "cpu") else embeddings
    )
    reduced_embeddings = tsne.fit_transform(embeddings_np)

    # os.makedirs("models", exist_ok=True)
    # with open(cache_path, "wb") as f:
    #     pickle.dump(reduced_embeddings, f)

    return reduced_embeddings


@st.cache_resource(ttl=3600, show_spinner=False)
def cluster_concepts(descriptions, num_clusters, use_cached=USE_CACHED, len_df=None):
    cache_path = f"models/clusters_{num_clusters}.pkl"

    # Check if cache exists AND has the correct length
    if use_cached and os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            cached_labels = pickle.load(f)
            # Verify that the cached data matches the current data size
            if len(cached_labels) == len(descriptions):
                return cached_labels
            # If lengths don't match, continue to recompute
            else:
                descriptions = descriptions[: len(cached_labels)]

    embeddings, st_model = compute_embeddings(descriptions)
    print("Embeddings computed.")

    clustering_model = KMeans(n_clusters=num_clusters, random_state=42)
    cluster_labels = clustering_model.fit_predict(embeddings.cpu().numpy())

    # os.makedirs("models", exist_ok=True)
    # with open(cache_path, "wb") as f:
    #     pickle.dump(cluster_labels, f)

    return cluster_labels[:len_df]


# 4. Build and visualize similarity graph
# sim_graph = build_similarity_graph(concepts, embeddings, threshold=0.7)
# visualize_graph(sim_graph, concepts)
# print("Similarity graph saved as 'similarity_graph.png'.")
