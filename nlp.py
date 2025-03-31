
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
# BERTopic for topic modeling
from bertopic import BERTopic
# Sentence Transformers for embeddings
from sentence_transformers import SentenceTransformer, util
# Scikit-learn for clustering & dimensionality reduction
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
# Transformers for sentiment and emotion analysis
from transformers import pipeline

from models import get_mongo_cards
from utils import clean_colors, clean_timestamp

pd.set_option("display.max_columns", None)

# Check if timestamps are in dataset
def load_dataset(file_path):
    """
    Expects a CSV with at least 'concept' and 'description' columns.
    Optionally, a 'timestamp' column for temporal analysis.
    """
    df = pd.read_csv(file_path)
    if 'createdAt' in df.columns:
        df['createdAt'] = pd.to_datetime(df['createdAt'])
    return df

def compute_embeddings(descriptions, model_name="sentence-transformers/all-MiniLM-L12-v2"):
    model = SentenceTransformer(model_name)
    embeddings = model.encode(descriptions, convert_to_tensor=True)
    return embeddings, model

def run_topic_modeling(descriptions):
    topic_model = BERTopic()
    topics, probs = topic_model.fit_transform(descriptions)
    # Visualize top topics
    topic_model.visualize_barchart(top_n_topics=10).write_html("topics_barchart.html")
    topic_model.visualize_heatmap().write_html("topics_heatmap.html")
    topic_model.visualize_hierarchy().write_html('topics_hierarchy.html')

    return topics, topic_model

def analyze_sentiment_emotion(descriptions):
    sentiment_pipeline = pipeline("text-classification", model="tabularisai/multilingual-sentiment-analysis")
    emotion_pipeline = pipeline("text-classification", model="ayoubkirouane/BERT-Emotions-Classifier")
    
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
        for j in range(i+1, num_cards):
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

def visualize_tsne(embeddings, concepts, cluster_labels=None, output_file="tsne_plot.png"):
    tsne = TSNE(n_components=2, perplexity=10, random_state=42)
    embeddings_np = embeddings.cpu().numpy() if hasattr(embeddings, "cpu") else embeddings
    reduced_embeddings = tsne.fit_transform(embeddings_np)
    plt.figure(figsize=(10, 8))
    if cluster_labels is None:
        plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1])
    else:
        plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1], c=cluster_labels, cmap="viridis")
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
        "Very Positive": 2
    }
    
    # Map each sentiment to our 5-point scale (defaulting to 0 for unknown labels)
    df['sentiment_score'] = [sentiment_mapping.get(s["label"], 0) for s in sentiments]
    
    df.set_index("createdAt", inplace=True)
    # Resample daily and take mean score
    sentiment_series = df['sentiment_score'].resample("D").mean()
    
    plt.figure(figsize=(10, 6))
    sentiment_series.plot()
    plt.title("Average Sentiment Over Time")
    plt.xlabel("Time")
    plt.ylabel("Sentiment Score (-2: Very Negative to +2: Very Positive)")
    plt.axhline(y=0, color='gray', linestyle='--', alpha=0.7)  # Add a zero line for reference
    plt.savefig(output_file)
    plt.close()


ragdb_cards = get_mongo_cards(db="ragDB", target_collection="kengrams")
nerdb_cards = get_mongo_cards(db="nerDB",target_collection="kengrams")
df_cards = pd.concat([ragdb_cards, nerdb_cards], ignore_index=True)

df_cards['colors'] = df_cards['colors'].apply(lambda x: clean_colors(x))

df_cards['updatedAt'] = df_cards['updatedAt'].apply(lambda x: clean_timestamp(x))
df_cards['createdAt'] = df_cards['createdAt'].apply(lambda x: clean_timestamp(x))

df = df_cards

concepts = df['name'].tolist()
descriptions = df['flavorText'].tolist()

# 1. Compute embeddings using SentenceTransformer
embeddings, st_model = compute_embeddings(descriptions)
print("Embeddings computed.")

# 2. Topic Modeling with BERTopic
topics, topic_model = run_topic_modeling(descriptions)
df["topic"] = topics
print("Topic modeling completed. Visualizations saved as HTML files.")

# 3. Sentiment and Emotion Analysis
sentiments, emotions = analyze_sentiment_emotion(descriptions)
# Store results in the dataframe for further analysis
df["sentiment"] = [s["label"] for s in sentiments]
df["emotion"] = [e["label"] for e in emotions]
print("Sentiment and emotion analysis completed.")

# 5. Visualize embeddings with t-SNE (with optional clustering)

# Determine the optimal number of clusters using the elbow method
# inertia = []
# K = range(1, 11)
# for k in K:
#     model = KMeans(n_clusters=k, random_state=42)
#     model.fit_predict(embeddings.cpu().numpy())
#     inertia.append(model.inertia_)
#
# # Plot the elbow curve
# plt.figure(figsize=(8, 6))
# plt.plot(K, inertia, "bx-")
# plt.xlabel("Number of clusters")
# plt.ylabel("Inertia")
# plt.title("Elbow Method for Optimal Number of Clusters")
# plt.show()

num_clusters = 8
clustering_model = KMeans(n_clusters=num_clusters, random_state=42)
cluster_labels = clustering_model.fit_predict(embeddings.cpu().numpy())
df["cluster"] = cluster_labels
visualize_tsne(embeddings, concepts, cluster_labels)
print("t-SNE plot with clustering saved as 'tsne_plot.png'.")

# 4. Build and visualize similarity graph
# sim_graph = build_similarity_graph(concepts, embeddings, threshold=0.7)
# visualize_graph(sim_graph, concepts)
# print("Similarity graph saved as 'similarity_graph.png'.")

# 6. Temporal Sentiment Analysis (if timestamps exist)
if "createdAt" in df.columns:
    sentiment_over_time(df.copy(), sentiments)
    print("Sentiment over time plot saved as 'sentiment_time_series.png'.")

# Save the enriched dataset for further inspection
df.to_csv("enriched_concepts.csv", index=False)
print("Enriched dataset saved as 'enriched_concepts.csv'.")

