"""
Graphing functions for the AI Thought Network.

"""

import hashlib

import networkx as nx
import plotly.graph_objs as go


def make_network_graph(df):
    # Step 1: Parse `metadata.relatedCards` into a list
    df["metadata.relatedCards"] = df["metadata.relatedCards"].apply(
        lambda x: (
            x
            if isinstance(x, list)
            else x.split("; ") if isinstance(x, str) and x else []
        )
    )

    # Step 2: Build the graph
    G = nx.DiGraph()
    for _, row in df.iterrows():
        source = row["id"]
        targets = row["metadata.relatedCards"]
        G.add_node(
            source,
            name=row["metadata.data.name"],
            node_type=row["metadata.data.type"],
            colors=row["metadata.data.colors"],
            mana_cost=row["metadata.data.manaCost"],
        )
        for target in targets:
            G.add_edge(source, target)
            if target not in G.nodes:
                G.add_node(
                    target, name=None, node_type=None, colors=None, mana_cost=None
                )  # Add node for related cards not in df

    # Step 3: Remove irrelevant nodes (None, Unknown)
    nodes_to_remove = [
        node for node, data in G.nodes(data=True) if data.get("name") is None
    ]
    G.remove_nodes_from(nodes_to_remove)

    # Step 4: Remove isolated nodes
    isolated_nodes = list(nx.isolates(G))
    G.remove_nodes_from(isolated_nodes)

    # Step 5: Assign consistent colors based on name
    def hash_color(value):
        """Generate a consistent color from a hash of the input value."""
        hash_val = int(hashlib.md5(value.encode()).hexdigest(), 16)  # Hash the value
        return f"#{hash_val % 0xFFFFFF:06x}"  # Convert to hex color

    unique_names = {data["name"] for _, data in G.nodes(data=True)}
    name_color_map = {name: hash_color(name) for name in unique_names}
    default_color = "#d62728"  # Default color for nodes without a name

    node_colors = []
    for node in G.nodes(data=True):
        name = node[1].get("name")  # Get the node's name
        node_colors.append(name_color_map.get(name, default_color))

    # Recompute positions with increased spacing for better layout
    pos = nx.spring_layout(G, seed=42, k=0.5)  # Adjust `k` for larger spacing

    # Extract edge and node positions for Plotly
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_x.append(x1)
        edge_x.append(None)
        edge_y.append(y0)
        edge_y.append(y1)
        edge_y.append(None)

    # Plotly edges
    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1, color="#444"),  # Darker edge color
        hoverinfo="none",
        mode="lines",
    )

    # Plotly nodes with enriched hover info
    node_x = []
    node_y = []
    node_text = []  # Visible text (e.g., name only)
    node_hover_text = []  # Hover text with additional info
    for node in G.nodes(data=True):
        x, y = pos[node[0]]
        node_x.append(x)
        node_y.append(y)
        # Visible text: only name
        node_text.append(node[1].get("name", "Unknown"))
        # Hover text: enriched with name, type, color, mana cost, and connections
        node_hover_text.append(
            f"Name: {node[1].get('name', 'Unknown')}<br>"
            f"Type: {node[1].get('node_type', 'Unknown')}<br>"
            f"Colors: {node[1].get('colors', 'Unknown')}<br>"
            f"Mana Cost: {node[1].get('mana_cost', 'Unknown')}<br>"
            f"Connections: {G.degree(node[0])}"  # Include node's degree (connections)
        )

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=node_text,  # Visible text: name only
        textposition="top center",  # Dynamic label position adjustment
        textfont=dict(size=10, color="white"),  # White text for better readability
        hoverinfo="text",
        hovertext=node_hover_text,  # Full hover text
        marker=dict(color=node_colors, size=15, line_width=2),
    )

    # Step 6: Create the Plotly figure with dark mode
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title="AI Thought Network (Colored by Name)",
            titlefont_size=16,
            showlegend=False,
            hovermode="closest",
            paper_bgcolor="black",  # Set background to black
            plot_bgcolor="black",  # Set plot area background to black
            margin=dict(b=0, l=0, r=0, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )

    return fig
