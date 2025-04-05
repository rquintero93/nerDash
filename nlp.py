import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer, util
from sklearn.manifold import TSNE
from transformers import pipeline

pd.set_option("display.max_columns", None)


def compute_embeddings(
    descriptions, model_name="sentence-transformers/all-MiniLM-L12-v2"
):
    model = SentenceTransformer(model_name)
    embeddings = model.encode(descriptions, convert_to_tensor=True)
    return embeddings, model


def run_topic_modeling(descriptions):
    topic_model = BERTopic()
    topics, probs = topic_model.fit_transform(descriptions)
    # Visualize top topics
    topic_model.visualize_barchart(top_n_topics=10).write_html("topics_barchart.html")
    topic_model.visualize_heatmap().write_html("topics_heatmap.html")
    topic_model.visualize_hierarchy().write_html("topics_hierarchy.html")

    return topics, topic_model


def analyze_sentiment_emotion(descriptions):
    sentiment_pipeline = pipeline(
        "text-classification", model="tabularisai/multilingual-sentiment-analysis"
    )
    emotion_pipeline = pipeline(
        "text-classification", model="ayoubkirouane/BERT-Emotions-Classifier"
    )

    sentiments = [sentiment_pipeline(desc)[0] for desc in descriptions]
    emotions = [emotion_pipeline(desc)[0] for desc in descriptions]
    return sentiments, emotions


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


def visualize_graph(G, concepts, output_file="similarity_graph.png"):
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(10, 8))
    nx.draw_networkx_nodes(G, pos, node_color="skyblue", node_size=500)
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.7)
    # labels = {i: concepts[i] for i in G.nodes()}
    # nx.draw_networkx_labels(G, pos, labels, font_size=10)
    plt.title("Concept Similarity Graph")
    plt.axis("off")
    plt.savefig(output_file)
    plt.close()


def visualize_tsne(
    embeddings, concepts, cluster_labels=None, output_file="tsne_plot.png"
):
    tsne = TSNE(n_components=2, perplexity=10, random_state=42)
    embeddings_np = (
        embeddings.cpu().numpy() if hasattr(embeddings, "cpu") else embeddings
    )
    reduced_embeddings = tsne.fit_transform(embeddings_np)
    plt.figure(figsize=(10, 8))
    if cluster_labels is None:
        plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1])
    else:
        plt.scatter(
            reduced_embeddings[:, 0],
            reduced_embeddings[:, 1],
            c=cluster_labels,
            cmap="viridis",
        )
    # for i, concept in enumerate(concepts):
    #     plt.annotate(concept, (reduced_embeddings[i, 0], reduced_embeddings[i, 1]), fontsize=8)
    plt.title("t-SNE visualization of Concept Embeddings")
    plt.savefig(output_file)
    plt.close()


def sentiment_over_time(df, sentiments, output_file="sentiment_time_series.png"):
    # If dataset has timestamps, aggregate sentiment scores over time
    if "createdAt" not in df.columns:
        print("No timestamp column available for temporal analysis.")
        return

    # Convert sentiment labels to a 5-point scale
    sentiment_mapping = {
        "Very Negative": -2,
        "Negative": -1,
        "Neutral": 0,
        "Positive": 1,
        "Very Positive": 2,
    }

    # Map each sentiment to our 5-point scale (defaulting to 0 for unknown labels)
    df["sentiment_score"] = [sentiment_mapping.get(s["label"], 0) for s in sentiments]

    df.set_index("createdAt", inplace=True)
    # Resample daily and take mean score
    sentiment_series = df["sentiment_score"].resample("D").mean()

    plt.figure(figsize=(10, 6))
    sentiment_series.plot()
    plt.title("Average Sentiment Over Time")
    plt.xlabel("Time")
    plt.ylabel("Sentiment Score (-2: Very Negative to +2: Very Positive)")
    plt.axhline(
        y=0, color="gray", linestyle="--", alpha=0.7
    )  # Add a zero line for reference
    plt.savefig(output_file)
    plt.close()


# 4. Build and visualize similarity graph
# sim_graph = build_similarity_graph(concepts, embeddings, threshold=0.7)
# visualize_graph(sim_graph, concepts)
# print("Similarity graph saved as 'similarity_graph.png'.")
