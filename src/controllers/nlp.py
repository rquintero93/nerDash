"""
NLP Analysis functions

"""

import networkx as nx
import pandas as pd
import streamlit as st
import torch
from sentence_transformers import SentenceTransformer, util
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from transformers import pipeline

pd.set_option("display.max_columns", None)


@st.cache_resource(ttl=3600, show_spinner=False)
def load_embedding_model(model_name="sentence-transformers/all-MiniLM-L12-v2"):
    """
    Load the SentenceTransformer model for embedding generation.
    """
    model = SentenceTransformer(model_name)
    return model


@st.cache_data(ttl=3600, show_spinner=False)
def compute_embeddings(
    descriptions, model_name="sentence-transformers/all-MiniLM-L12-v2"
):
    # Create placeholder elements
    status_placeholder = st.empty()
    progress_placeholder = st.empty()

    status_placeholder.write("Computing embeddings...")
    progress_placeholder.progress(0)

    model = load_embedding_model(model_name)
    # Process in batches to show progress
    batch_size = 32
    embeddings_list = []

    for i in range(0, len(descriptions), batch_size):
        batch = descriptions[i : i + batch_size]
        batch_embeddings = model.encode(batch, convert_to_tensor=True)
        embeddings_list.append(batch_embeddings)
        progress_placeholder.progress(min(1.0, (i + batch_size) / len(descriptions)))

    # Combine all batches
    if len(embeddings_list) > 1:
        embeddings = torch.cat(embeddings_list, dim=0)
    else:
        embeddings = embeddings_list[0]

    # Clear placeholders when done
    status_placeholder.empty()
    progress_placeholder.empty()

    return embeddings.detach().cpu().numpy(), model


@st.cache_resource(ttl=3600, show_spinner=False)
def analyze_sentiment_emotion(descriptions):
    sentiment_pipeline = pipeline(
        "text-classification",
        model="tabularisai/multilingual-sentiment-analysis",
        batch_size=16,
    )

    # Create placeholder elements that we can update and clear
    status_placeholder = st.empty()
    progress_placeholder = st.empty()

    status_placeholder.write("Analyzing sentiment...")
    progress_placeholder.progress(0)

    # Process in batches with progress bar
    batch_size = 32  # Size of each progress update batch
    results = []

    for i in range(0, len(descriptions), batch_size):
        batch = descriptions[i : i + batch_size]
        batch_results = sentiment_pipeline(batch)
        results.extend(batch_results)
        progress_placeholder.progress(min(1.0, (i + batch_size) / len(descriptions)))

    # Clear placeholders when done
    status_placeholder.empty()
    progress_placeholder.empty()

    return results


@st.cache_resource(ttl=3600, show_spinner=False)
def build_similarity_graph(concepts, embeddings, threshold=0.5, max_edges=1000):
    # Each node is a concept and edges exist if similarity > threshold
    G = nx.Graph()
    num_cards = len(concepts)

    # Create placeholder elements
    status_placeholder = st.empty()
    progress_placeholder = st.empty()

    status_placeholder.write("Building similarity graph...")
    progress_placeholder.progress(0)

    # First add all nodes to the graph
    for i in range(num_cards):
        G.add_node(i, concept=concepts[i])

    embeddings = torch.from_numpy(embeddings)
    # Use cosine similarity from sentence-transformers util
    cosine_scores = util.cos_sim(embeddings, embeddings)

    # Collect all edges with scores
    all_edges = []
    total_comparisons = (num_cards * (num_cards - 1)) // 2
    comparisons_done = 0

    for i in range(num_cards):
        for j in range(i + 1, num_cards):
            score = cosine_scores[i][j].item()
            if score > threshold:
                all_edges.append((i, j, score))

            comparisons_done += 1
            if (
                comparisons_done % max(1, total_comparisons // 100) == 0
            ):  # Update every 1%
                progress_placeholder.progress(
                    min(0.9, comparisons_done / total_comparisons)
                )

    # Sort edges by weight (highest first) and take only the top max_edges
    status_placeholder.write(
        f"Found {len(all_edges)} edges, sorting and adding top {max_edges}..."
    )
    all_edges.sort(key=lambda x: x[2], reverse=True)

    # Add the top edges to the graph
    for idx, (i, j, score) in enumerate(all_edges[:max_edges]):
        G.add_edge(i, j, weight=score)
        if idx % max(1, max_edges // 50) == 0:  # Update every 2%
            progress_placeholder.progress(
                min(1.0, 0.9 + (0.1 * idx / min(len(all_edges), max_edges)))
            )

    # Clear placeholders when done
    status_placeholder.empty()
    progress_placeholder.empty()

    return G


@st.cache_resource(ttl=3600, show_spinner=False)
def reduce_embeddings_tsne(embeddings):
    # Create placeholder elements
    status_placeholder = st.empty()
    progress_placeholder = st.empty()

    status_placeholder.write(
        "Reducing dimensions with t-SNE (this may take a while)..."
    )
    progress_placeholder.progress(
        0.3
    )  # Indeterminate progress as t-SNE doesn't report progress

    tsne = TSNE(n_components=2, perplexity=10, random_state=42, n_jobs=-1)
    embeddings_np = (
        embeddings.cpu().numpy() if hasattr(embeddings, "cpu") else embeddings
    )

    # t-SNE doesn't provide progress updates, so we'll just update to show it's working
    progress_placeholder.progress(0.6)
    reduced_embeddings = tsne.fit_transform(embeddings_np)
    progress_placeholder.progress(1.0)

    # Clear placeholders when done
    status_placeholder.empty()
    progress_placeholder.empty()

    return reduced_embeddings


@st.cache_resource(ttl=3600, show_spinner=False)
def cluster_concepts(embeddings, num_clusters):
    # Create placeholder elements
    status_placeholder = st.empty()
    progress_placeholder = st.empty()

    status_placeholder.write(f"Clustering concepts into {num_clusters} clusters...")
    progress_placeholder.progress(0.5)  # KMeans doesn't report progress

    clustering_model = KMeans(n_clusters=num_clusters, random_state=42)
    cluster_labels = clustering_model.fit_predict(embeddings)

    progress_placeholder.progress(1.0)

    # Clear placeholders when done
    status_placeholder.empty()
    progress_placeholder.empty()

    return cluster_labels


# 4. Build and visualize similarity graph
# sim_graph = build_similarity_graph(concepts, embeddings, threshold=0.7)
# visualize_graph(sim_graph, concepts)
# print("Similarity graph saved as 'similarity_graph.png'.")
