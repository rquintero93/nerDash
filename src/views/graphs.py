"""
Graphing functions for the AI Thought Network.

"""

from typing import Optional, Union

import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from loguru import logger

from controllers import get_bar_df, get_line_df, get_pie_df
from utils import constants, is_valid_chart_data

# Configure Loguru
logger.remove()  # Remove default logger to customize settings
logger.add(
    "logs/graph_logs.log",
    rotation="10MB",
    level="INFO",
    format="{time} {level} {message}",
)


def make_line_chart(data: pd.DataFrame = None, x: str = None, y: str = None) -> px.line:
    """
    Creates a plotly line chart with some default settings.

    Args:
        data (pd.DataFrame): The data to plot.
        x (str): The column to plot on the x-axis.
        y (str): The column to plot on the y-axis.

    Returns:
        px.line: A plotly line chart.

    """
    # TODO: Add input validation

    logger.info(f"Generating line chart | X: {x}, Y: {y}")

    line_df = data[[x, y]]

    line_counts = get_line_df(line_df, x, y)
    fig = px.line(
        line_counts,
        y="count",
        x=y,
        markers=True,
    )

    fig.update_layout(
        template="plotly_dark",
        xaxis_title=y,
        yaxis_title=x,
        hovermode="x unified",
        margin=dict(l=40, r=40, t=60, b=40),
        height=500,
        xaxis=dict(rangeslider=dict(visible=True), type="date"),
    )

    if y == "createdAt":
        fig.update_traces(line=dict(width=2), marker=dict(size=6))
    else:
        fig.update_traces(
            line=dict(width=2, color="limegreen"),
            marker=dict(size=6, color="limegreen"),
        )

    return fig


@st.cache_resource(ttl=3600, show_spinner=False)
def visualize_graph(_G, concepts, highlight_node=None) -> go.Figure:
    """
    Visualizes a networkx graph using Plotly.

    Args:
        G: The networkx graph to visualize
        concepts: A dict or list mapping node IDs to labels
        highlight_node: Optional node to highlight along with its connections

    Returns:
        plotly.graph_objects.Figure: A Plotly figure showing the graph
    """

    # Create placeholder elements
    status_placeholder = st.empty()
    progress_placeholder = st.empty()

    status_placeholder.write("Creating graph visualization...")
    progress_placeholder.progress(0)

    # If highlighting a specific node, create a subgraph with that node and its connections
    if highlight_node is not None and highlight_node in _G.nodes():
        status_placeholder.write(
            f"Filtering graph to show node '{concepts[highlight_node]}' and its connections..."
        )
        # Get all connections, handling both directed and undirected graphs
        if hasattr(_G, "predecessors"):  # Check if it's a directed graph
            neighbors = list(_G.neighbors(highlight_node)) + list(
                _G.predecessors(highlight_node)
            )
        else:  # For undirected graphs
            neighbors = list(_G.neighbors(highlight_node))
        nodes_to_keep = [highlight_node] + neighbors
        _G = _G.subgraph(nodes_to_keep).copy()

    # Limit to largest connected component if graph is too large
    elif len(_G.nodes()) > 200:
        progress_placeholder.progress(0.1)
        status_placeholder.write(
            "Graph is large, limiting to largest connected component..."
        )
        largest_cc = max(nx.connected_components(_G), key=len)
        _G = _G.subgraph(largest_cc).copy()

    # Use faster layout algorithm for large graphs
    progress_placeholder.progress(0.2)
    status_placeholder.write(f"Computing layout for {len(_G.nodes())} nodes...")
    if len(_G.nodes()) > 100:
        pos = nx.kamada_kawai_layout(_G)
    else:
        pos = nx.spring_layout(_G, seed=42)

    # --- edge trace ---
    progress_placeholder.progress(0.5)
    status_placeholder.write("Building edge traces...")
    edge_x, edge_y = [], []
    total_edges = len(_G.edges())
    for i, (u, v) in enumerate(_G.edges()):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        if i % max(1, total_edges // 10) == 0:  # Update every 10%
            progress_placeholder.progress(0.5 + (0.2 * i / total_edges))

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1, color="gray"),
        hoverinfo="none",
        mode="lines",
        opacity=0.3,
    )

    # --- node trace ---
    progress_placeholder.progress(0.7)
    status_placeholder.write("Building node traces...")
    node_x, node_y = [], []
    hover_text = []
    node_colors = []
    node_sizes = []
    total_nodes = len(_G.nodes())

    # Define colors for highlighting
    highlight_color = "red"
    neighbor_color = "orange"
    default_color = "skyblue"

    for i, node in enumerate(_G.nodes()):
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        hover_text.append(concepts[node])

        # Set node color and size based on highlighting
        if highlight_node is not None:
            if node == highlight_node:
                node_colors.append(highlight_color)
                node_sizes.append(15)  # Larger size for highlighted node
            else:
                node_colors.append(neighbor_color)
                node_sizes.append(10)
        else:
            node_colors.append(default_color)
            node_sizes.append(10)

        if i % max(1, total_nodes // 10) == 0:  # Update every 10%
            progress_placeholder.progress(0.7 + (0.2 * i / total_nodes))

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        marker=dict(
            size=node_sizes, color=node_colors, line=dict(width=1, color="white")
        ),
        hovertext=hover_text,
        hoverinfo="text",
        name="Concepts",
    )

    # --- assemble figure ---
    progress_placeholder.progress(0.9)
    status_placeholder.write("Assembling final visualization...")

    title = "Concept Similarity Graph"
    if highlight_node is not None:
        title += f" - Highlighting: {concepts[highlight_node]}"

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title=title,
        template="plotly_dark",
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40),
        height=600,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )

    progress_placeholder.progress(1.0)

    # Clear placeholders when done
    status_placeholder.empty()
    progress_placeholder.empty()

    return fig


def visualize_tsne(reduced_embeddings, cluster_labels, names) -> px.scatter:
    """
    Performs t-SNE dimensionality reduction and returns a Plotly visualization.

    Args:
        embeddings: The embeddings to reduce and visualize
        cluster_labels: Labels for coloring the points by cluster
        output_file: Deprecated. Kept for backwards compatibility.

    Returns:
        plotly.graph_objects.Figure: A Plotly figure object showing the t-SNE
    """
    # Create placeholder elements
    status_placeholder = st.empty()
    progress_placeholder = st.empty()

    status_placeholder.write("Creating t-SNE visualization...")
    progress_placeholder.progress(0.3)

    cluster_labels = cluster_labels.astype(str)

    # Data preparation
    progress_placeholder.progress(0.6)

    # Create plotly figure
    fig = px.scatter(
        x=reduced_embeddings[:, 0],
        y=reduced_embeddings[:, 1],
        color=cluster_labels,
        hover_name=names,
        title="t-SNE visualization of Embeddings by Cluster",
        color_discrete_sequence=px.colors.qualitative.Bold,
    )

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="t-SNE Dimension 1",
        yaxis_title="t-SNE Dimension 2",
        margin=dict(l=40, r=40, t=60, b=40),
        height=600,
        width=800,
    )

    progress_placeholder.progress(1.0)

    # Clear placeholders when done
    status_placeholder.empty()
    progress_placeholder.empty()

    return fig


def make_sentiment_over_time(df, sentiments, output_file=None) -> px.line:
    """
    Creates a Plotly line chart showing sentiment trends over time.

    Args:
        df (pd.DataFrame): DataFrame containing the data with timestamps
        sentiments (list): List of sentiment dictionaries with labels
        output_file (str, optional): Deprecated. Kept for backwards compatibility.

    Returns:
        plotly.graph_objects.Figure: A Plotly figure object showing sentiment over time
    """
    # If dataset has timestamps, aggregate sentiment scores over time
    if "createdAt" not in df.columns:
        print("No timestamp column available for temporal analysis.")
        return None

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

    df = df.set_index("createdAt")
    # Resample daily and take mean score
    sentiment_series = df["sentiment_score"].resample("D").mean().reset_index()

    # Create plotly figure

    fig = px.line(
        sentiment_series,
        x="createdAt",
        y="sentiment_score",
        markers=True,
        # title="Average Mood Over Time",
    )

    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Time",
        yaxis_title="Sentiment Score",
        hovermode="x unified",
        margin=dict(l=40, r=40, t=60, b=40),
        height=500,
        xaxis=dict(rangeslider=dict(visible=True), type="date"),
    )

    # Add horizontal reference line at y=0
    fig.add_shape(
        type="line",
        line=dict(dash="dash", color="gray", width=1),
        y0=0,
        y1=0,
        x0=0,
        x1=1,
        xref="paper",
    )

    print("creating figure finished")
    return fig


def make_bar_chart(
    data: Union[pd.DataFrame, dict] = None,
    orientation: Optional[str] = None,
    column: str = None,
) -> px.bar:
    """
    Creates a plotly bar chart with some default settings.

    Args:
        data (Union[pd.DataFrame, dict]): The data to plot.
        orientation (Optional[str]): The orientation of the bar chart.
        column (str): The column to plot from the DataFrame.

    Returns:
        px.bar: A plotly bar chart.
    """

    # Input validation
    is_valid, error_code = is_valid_chart_data(data, column)
    if not is_valid:
        logger.error(f"Invalid chart data: {error_code}")
        raise ValueError(error_code)

    logger.info(f"Generating bar chart | Column: {column}, Orientation: {orientation}")

    bar_counts = get_bar_df(data, column)

    # Create the bar chart
    fig = px.bar(
        bar_counts,
        x="count" if orientation == "h" else bar_counts.columns[0],
        y=bar_counts.columns[0] if orientation == "h" else "count",
        color=bar_counts.columns[0],
        color_discrete_map=constants.COLOR_TO_HEX_MAP,
        orientation=orientation,
    )

    fig.update_traces(marker_line_color="white", marker_line_width=2)

    # Truncate legend labels
    for trace in fig.data:
        trace.name = trace.name[:15]

    layout_updates = {"showlegend": True}

    if orientation == "h":
        layout_updates.update(
            {"height": len(bar_counts) * 25, "margin": dict(l=200), "bargap": 0.15}
        )

    fig.update_layout(**layout_updates)
    logger.info("Bar chart successfully created.")
    return fig


def make_pie_chart(
    data: pd.DataFrame = None, column: str = None, show_legend: str = None
) -> px.pie:
    """
    Creates a plotly pie chart with some default settings.

    Args:
        data (pd.DataFrame): The data to plot.
        column (str): The column to plot from the DataFrame.
        show_legend (str): Whether to show the legend. Defaults to True.

    Returns:
        px.pie: A plotly pie chart.
    """

    # Input validation
    is_valid, error_code = is_valid_chart_data(data, column)
    if not is_valid:
        logger.error(f"Invalid pie chart data: {error_code}")
        raise ValueError(error_code)

    logger.info(f"Generating pie chart | Column: {column}, Show legend: {show_legend}")

    pie_counts = get_pie_df(data, column)

    # Create the pie chart
    fig = px.pie(
        pie_counts,
        names=column,
        values="count",
        color=column,
        color_discrete_map=constants.COLOR_TO_HEX_MAP,
    )

    fig.update_traces(
        textinfo="percent",
        textposition="inside",
        insidetextorientation="auto",
        showlegend=show_legend,
    )

    logger.info("Pie chart successfully created.")
    return fig


# def make_network_dataframe(df):
#     #     # Prepare the analytical DataFrame from the graph
#
#     G = nx.DiGraph()
#     valid_nodes = {}  # Stores nodes with valid aggregated IDs
#
#     # Step 1: Create nodes indexed by name but store ID references
#     for _, row in df.iterrows():
#         node_name = row.get("metadata.data.name", "Unknown")
#         if not node_name:
#             continue  # Skip rows with no name
#
#         if row["retrievalCount"] == 0:
#             continue
#
#         ids = row["id"] if isinstance(row["id"], list) else [row["id"]]
#         if len(ids) == 0:
#             continue  # Skip nodes with no associated IDs
#
#         valid_nodes[node_name] = {
#             "name": node_name,
#             "node_type": row.get("metadata.data.type", "Unknown"),
#             "colors": row.get("metadata.data.colors", "Unknown"),
#             "mana_cost": row.get("metadata.data.manaCost", "Unknown"),
#             "retrievalCount": row.get("retrievalCount", "Unknown"),
#             "ids": set(ids),  # Store as a set for quick lookup
#         }
#
#     # Add nodes to the graph
#     for node_name, attributes in valid_nodes.items():
#         G.add_node(node_name, **attributes)
#
#     # Step 2: Add edges only if relatedCards match valid IDs in other nodes
#     for node_name, attributes in valid_nodes.items():
#         related_ids = df.loc[
#             df["metadata.data.name"] == node_name, "metadata.relatedCards"
#         ].values[0]
#
#         if isinstance(related_ids, list):
#             for related_id in related_ids:
#                 for target_name, target_attrs in valid_nodes.items():
#                     if related_id in target_attrs["ids"]:  # Match ID in other nodes
#                         G.add_edge(node_name, target_name)
#
#     # Debugging output
#     # print(f"Total Nodes in Graph: {len(G.nodes)}")
#     # print(f"Total Edges in Graph: {len(G.edges)}")
#
#     # If no valid nodes remain, return None
#     if len(G.nodes) == 0:
#         print("No valid nodes remain. Returning None.")
#         return None
#
#     # Compute layout
#     # pos = nx.spring_layout(G, seed=42, k=0.5)
#
#     graph_data = []
#     for node, data in G.nodes(data=True):
#         graph_data.append(
#             {
#                 "name": data["name"],
#                 "type": data.get("node_type", "Unknown"),
#                 "colors": data.get("colors", "Unknown"),
#                 "mana_cost": data.get("mana_cost", "Unknown"),
#                 "retrievalCount": data.get("retrievalCount", 0),
#                 "associated_IDs_count": len(data.get("ids", [])),
#                 "connected_concepts_count": G.degree(
#                     node
#                 ),  # Number of connected concepts
#             }
#         )
#
#     # Convert to DataFrame
#     graph_df = pd.DataFrame(graph_data)
#     return graph_df


# def make_network_graph(df):
#     # Step 1: Parse `metadata.relatedCards` into a list
#     df["metadata.relatedCards"] = df["metadata.relatedCards"].apply(
#         lambda x: (
#             x
#             if isinstance(x, list)
#             else x.split("; ") if isinstance(x, str) and x else []
#         )
#     )
#
#     # Step 2: Build the graph
#     G = nx.DiGraph()
#     for _, row in df.iterrows():
#         source = row["id"]
#         targets = row["metadata.relatedCards"]
#         G.add_node(
#             source,
#             name=row["metadata.data.name"],
#             node_type=row["metadata.data.type"],
#             colors=row["metadata.data.colors"],
#             mana_cost=row["metadata.data.manaCost"],
#             botId=row["metadata.botId"],
#         )
#         for target in targets:
#             G.add_edge(source, target)
#             if target not in G.nodes:
#                 G.add_node(
#                     target, name=None, node_type=None, colors=None, mana_cost=None
#                 )  # Add node for related cards not in df
#
#     # Step 3: Remove irrelevant nodes (None, Unknown)
#     nodes_to_remove = [
#         node for node, data in G.nodes(data=True) if data.get("name") is None
#     ]
#     G.remove_nodes_from(nodes_to_remove)
#
#     # Step 4: Remove isolated nodes
#     isolated_nodes = list(nx.isolates(G))
#     G.remove_nodes_from(isolated_nodes)
#
#     # Step 5: Assign consistent colors based on name
#     def hash_color(value):
#         """Generate a consistent color from a hash of the input value."""
#         hash_val = int(hashlib.md5(value.encode()).hexdigest(), 16)  # Hash the value
#         return f"#{hash_val % 0xFFFFFF:06x}"  # Convert to hex color
#
#     unique_names = {data["name"] for _, data in G.nodes(data=True)}
#     name_color_map = {name: hash_color(name) for name in unique_names}
#     default_color = "#d62728"  # Default color for nodes without a name
#
#     node_colors = []
#     for node in G.nodes(data=True):
#         name = node[1].get("name")  # Get the node's name
#         node_colors.append(name_color_map.get(name, default_color))
#
#     # Recompute positions with increased spacing for better layout
#     pos = nx.spring_layout(G, seed=42, k=0.5)  # Adjust `k` for larger spacing
#
#     # Extract edge and node positions for Plotly
#     edge_x = []
#     edge_y = []
#     for edge in G.edges():
#         x0, y0 = pos[edge[0]]
#         x1, y1 = pos[edge[1]]
#         edge_x.append(x0)
#         edge_x.append(x1)
#         edge_x.append(None)
#         edge_y.append(y0)
#         edge_y.append(y1)
#         edge_y.append(None)
#
#     # Plotly edges
#     edge_trace = go.Scatter(
#         x=edge_x,
#         y=edge_y,
#         line=dict(width=1, color="#444"),  # Darker edge color
#         hoverinfo="none",
#         mode="lines",
#     )
#
#     # Plotly nodes with enriched hover info
#     node_x = []
#     node_y = []
#     node_text = []  # Visible text (e.g., name only)
#     node_hover_text = []  # Hover text with additional info
#     for node in G.nodes(data=True):
#         x, y = pos[node[0]]
#         node_x.append(x)
#         node_y.append(y)
#         # Visible text: only name
#         node_text.append(node[1].get("name", "Unknown"))
#         # Hover text: enriched with name, type, color, mana cost, and connections
#         node_hover_text.append(
#             f"Bot Name: {node[1].get('botId', 'Unknown')}<br>"
#             f"Card Name: {node[1].get('name', 'Unknown')}<br>"
#             f"Type: {node[1].get('node_type', 'Unknown')}<br>"
#             f"Colors: {node[1].get('colors', 'Unknown')}<br>"
#             f"Mana Cost: {node[1].get('mana_cost', 'Unknown')}<br>"
#             f"Connections: {G.degree(node[0])}"  # Include node's degree (connections)
#         )
#
#     node_trace = go.Scatter(
#         x=node_x,
#         y=node_y,
#         mode="markers+text",
#         # text=node_text,  # Visible text: name only
#         textposition="top center",  # Dynamic label position adjustment
#         textfont=dict(size=10, color="white"),  # White text for better readability
#         hoverinfo="text",
#         hovertext=node_hover_text,  # Full hover text
#         marker=dict(color=node_colors, size=15, line_width=2),
#     )
#
#     # Step 6: Create the Plotly figure with dark mode
#     fig = go.Figure(
#         data=[edge_trace, node_trace],
#         layout=go.Layout(
#             title="AI Thought Network (Colored by Name)",
#             titlefont_size=16,
#             showlegend=False,
#             hovermode="closest",
#             paper_bgcolor="black",  # Set background to black
#             plot_bgcolor="black",  # Set plot area background to black
#             margin=dict(b=0, l=0, r=0, t=40),
#             xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
#             yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
#         ),
#     )
#
#     return fig

# def make_agg_network_graph(df):
#     """Builds a high-level network graph where aggregated card names are nodes,
#     and edges exist if their relatedCards contain an ID present in another node."""
#
#     G = nx.DiGraph()
#     valid_nodes = {}  # Stores nodes with valid aggregated IDs
#
#     # Step 1: Create nodes indexed by name but store ID references
#     for _, row in df.iterrows():
#         node_name = row.get("metadata.data.name", "Unknown")
#         if not node_name:
#             continue  # Skip rows with no name
#
#         if row["retrievalCount"] == 0:
#             continue
#
#         ids = row["id"] if isinstance(row["id"], list) else [row["id"]]
#         if len(ids) == 0:
#             continue  # Skip nodes with no associated IDs
#
#         valid_nodes[node_name] = {
#             "name": node_name,
#             "node_type": row.get("metadata.data.type", "Unknown"),
#             "colors": row.get("metadata.data.colors", "Unknown"),
#             "mana_cost": row.get("metadata.data.manaCost", "Unknown"),
#             "retrievalCount": row.get("retrievalCount", "Unknown"),
#             "ids": set(ids),  # Store as a set for quick lookup
#         }
#
#     # Add nodes to the graph
#     for node_name, attributes in valid_nodes.items():
#         G.add_node(node_name, **attributes)
#
#     # Step 2: Add edges only if relatedCards match valid IDs in other nodes
#     for node_name, attributes in valid_nodes.items():
#         related_ids = df.loc[
#             df["metadata.data.name"] == node_name, "metadata.relatedCards"
#         ].values[0]
#
#         if isinstance(related_ids, list):
#             for related_id in related_ids:
#                 for target_name, target_attrs in valid_nodes.items():
#                     if related_id in target_attrs["ids"]:  # Match ID in other nodes
#                         G.add_edge(node_name, target_name)
#
#     # Debugging output
#     # print(f"Total Nodes in Graph: {len(G.nodes)}")
#     # print(f"Total Edges in Graph: {len(G.edges)}")
#
#     # If no valid nodes remain, return None
#     if len(G.nodes) == 0:
#         print("No valid nodes remain. Returning None.")
#         return None
#
#     # Assign colors
#     def hash_color(value):
#         hash_val = int(hashlib.md5(value.encode()).hexdigest(), 16)
#         return f"#{hash_val % 0xFFFFFF:06x}"
#
#     unique_names = {
#         data.get("name", "Unknown") for _, data in G.nodes(data=True)if "name" in data
#     }
#     name_color_map = {name: hash_color(name) for name in unique_names}
#     default_color = "#d62728"
#
#     node_colors = [
#         name_color_map.get(data.get("name", "Unknown"), default_color)
#         for _, data in G.nodes(data=True)
#     ]
#
#     # Compute layout
#     if len(G.nodes) > 0:
#         pos = nx.spring_layout(G, seed=42, k=0.5)
#     else:
#         return None
#
#     # Extract edge positions
#     edge_x, edge_y = [], []
#     for edge in G.edges():
#         x0, y0 = pos[edge[0]]
#         x1, y1 = pos[edge[1]]
#         edge_x.extend([x0, x1, None])
#         edge_y.extend([y0, y1, None])
#
#     edge_trace = go.Scatter(
#         x=edge_x,
#         y=edge_y,
#         line=dict(width=1, color="#444"),
#         hoverinfo="none",
#         mode="lines",
#     )
#
#     node_x, node_y, node_text, node_hover_text = [], [], [], []
#     for node, data in G.nodes(data=True):
#         x, y = pos[node]
#         node_x.append(x)
#         node_y.append(y)
#         concept_count = G.degree(node)
#         node_text.append(data["name"])
#         node_hover_text.append(
#             f"Name: {data['name']}<br>"
#             f"Type: {data.get('node_type', 'Unknown')}<br>"
#             f"Colors: {data.get('colors', 'Unknown')}<br>"
#             f"Mana Cost: {data.get('mana_cost', 'Unknown')}<br>"
#             f"Connecting Concepts: {concept_count}<br>"
#             f"Total Retrievals: {data.get('retrievalCount', 'Unknown')}<br>"
#             f"Total Associated Cards: {len(data.get('ids', []))}"
#         )
#
#     node_trace = go.Scatter(
#         x=node_x,
#         y=node_y,
#         mode="markers+text",
#         # text=node_text,
#         textposition="top center",
#         textfont=dict(size=10, color="white"),
#         hoverinfo="text",
#         hovertext=node_hover_text,
#         marker=dict(color=node_colors, size=15, line_width=2),
#     )
#
#     fig = go.Figure(
#         data=[edge_trace, node_trace],
#         layout=go.Layout(
#             title="AI Concept Network (Colored by Name)",
#             titlefont_size=16,
#             showlegend=False,
#             hovermode="closest",
#             paper_bgcolor="black",
#             plot_bgcolor="black",
#             margin=dict(b=0, l=0, r=0, t=40),
#             xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
#             yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
#         ),
#     )
#     return fig
