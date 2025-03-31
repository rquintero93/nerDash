'''
NLP Analysis functions

'''

import networkx as nx
import pandas as pd
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer, util
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from transformers import pipeline

pd.set_option("display.max_columns", None)

def compute_embeddings(descriptions, model_name="sentence-transformers/all-MiniLM-L12-v2"):
    model = SentenceTransformer(model_name)
    embeddings = model.encode(descriptions, convert_to_tensor=True)
    return embeddings, model

def model_topics(descriptions):
    topic_model = BERTopic()
    topics, probs = topic_model.fit_transform(descriptions)
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

def reduce_embeddings_tsne(embeddings):
    tsne = TSNE(n_components=2, perplexity=10, random_state=42)
    embeddings_np = embeddings.cpu().numpy() if hasattr(embeddings, "cpu") else embeddings
    reduced_embeddings = tsne.fit_transform(embeddings_np)
    return reduced_embeddings


def cluster_concepts(descriptions,num_clusters):
    
    embeddings, st_model = compute_embeddings(descriptions)
    print("Embeddings computed.")

    clustering_model = KMeans(n_clusters=num_clusters, random_state=42)
    cluster_labels = clustering_model.fit_predict(embeddings.cpu().numpy())
    return cluster_labels


# 4. Build and visualize similarity graph
# sim_graph = build_similarity_graph(concepts, embeddings, threshold=0.7)
# visualize_graph(sim_graph, concepts)
# print("Similarity graph saved as 'similarity_graph.png'.")
