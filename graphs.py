"""
Graphing functions for the AI Thought Network.

"""


import networkx as nx
import pandas as pd
import plotly.express as px

# Define a color map for MTG colors
MTG_COLOR_MAP = {
    "B": "#000000",  # Black
    "BGU": "#2E8B57",  # Sultai
    "BR": "#8B0000",  # Rakdos
    "BGR": "#556B2F",  # Jund (was BRG)
    "BRW": "#CD5C5C",  # Mardu
    "C": "#D3D3D3",  # Colorless
    "G": "#008000",  # Green
    "R": "#FF0000",  # Red
    "GR": "#32CD32",  # Gruul (was RG)
    "GRW": "#FFD700",  # Naya (was RGW)
    "GRU": "#20B2AA",  # Temur (was RUG)
    "U": "#1E90FF",  # Blue
    "BU": "#4682B4",  # Dimir (was UB)
    "BRU": "#8A2BE2",  # Grixis (was UBR)
    "RU": "#FF6347",  # Izzet (was UR)
    "RUW": "#FF4500",  # Jeskai (was URW)
    "W": "#FFFFFF",  # White
    "BW": "#A9A9A9",  # Orzhov (was WB)
    "BGW": "#9ACD32",  # Abzan (was WBG)
    "GW": "#98FB98",  # Selesnya (was WG)
    "RW": "#FFA07A",  # Boros (was WR)
    "UW": "#ADD8E6",  # Azorius (was WU)
    "BUW": "#87CEEB",  # Esper (was WUB)
    "GUW": "#90EE90",  # Bant (was WUG)
    "BGRUW": "#DAA520",  # Rainbow (was WUBRG)
}

def make_bar_chart(data,orientation=None, column=None):
    if isinstance(data, pd.DataFrame):
        bar_counts = data[column].value_counts().reset_index()
        bar_counts.columns = [column, 'count']
    elif isinstance(data, dict):
        bar_counts = pd.DataFrame(list(data.items()), columns=['key', 'count'])
        bar_counts = bar_counts.sort_values('count', ascending=False)
    else:
        raise ValueError("Unsupported data type for bar chart")

    if orientation == 'h':
        fig = px.bar(bar_counts, y=bar_counts.columns[0], x='count', color=bar_counts.columns[0],
                 color_discrete_map=MTG_COLOR_MAP, orientation=orientation)
    else:
        fig = px.bar(bar_counts, x=bar_counts.columns[0], y='count', color=bar_counts.columns[0],
                 color_discrete_map=MTG_COLOR_MAP, orientation=orientation)

    fig.update_traces(marker_line_color='white', marker_line_width=2)
    if orientation == 'h':
        fig.update_layout(
            height=len(bar_counts) * 25,  # Adjust height based on number of bars
            margin=dict(l=200),  # Increase left margin for labels
            bargap=0.15,  # Increase spacing between bars
            showlegend=False
        )
    else:
        fig.update_layout(
            showlegend=False
        )
    return fig

def make_pie_chart(df, column):
    # Ensure color combinations are in the same order as MTG_COLOR_MAP
    df[column] = df[column].apply(lambda x: ''.join(sorted(x)) if isinstance(x, list) else x)
    
    pie_counts = df[column].value_counts().reset_index()
    pie_counts.columns = [column, 'count']
    
    fig = px.pie(pie_counts, names=column, values='count', color=column, 
                 color_discrete_map=MTG_COLOR_MAP)

    fig.update_traces(textinfo='percent+label', insidetextorientation='auto')

    return fig


def make_network_dataframe(df):
    #     # Prepare the analytical DataFrame from the graph

    G = nx.DiGraph()
    valid_nodes = {}  # Stores nodes with valid aggregated IDs

    # Step 1: Create nodes indexed by name but store ID references
    for _, row in df.iterrows():
        node_name = row.get("metadata.data.name", "Unknown")
        if not node_name:
            continue  # Skip rows with no name

        if row["retrievalCount"] == 0:
            continue

        ids = row["id"] if isinstance(row["id"], list) else [row["id"]]
        if len(ids) == 0:
            continue  # Skip nodes with no associated IDs

        valid_nodes[node_name] = {
            "name": node_name,
            "node_type": row.get("metadata.data.type", "Unknown"),
            "colors": row.get("metadata.data.colors", "Unknown"),
            "mana_cost": row.get("metadata.data.manaCost", "Unknown"),
            "retrievalCount": row.get("retrievalCount", "Unknown"),
            "ids": set(ids),  # Store as a set for quick lookup
        }

    # Add nodes to the graph
    for node_name, attributes in valid_nodes.items():
        G.add_node(node_name, **attributes)

    # Step 2: Add edges only if relatedCards match valid IDs in other nodes
    for node_name, attributes in valid_nodes.items():
        related_ids = df.loc[
            df["metadata.data.name"] == node_name, "metadata.relatedCards"
        ].values[0]

        if isinstance(related_ids, list):
            for related_id in related_ids:
                for target_name, target_attrs in valid_nodes.items():
                    if related_id in target_attrs["ids"]:  # Match ID in other nodes
                        G.add_edge(node_name, target_name)

    # Debugging output
    # print(f"Total Nodes in Graph: {len(G.nodes)}")
    # print(f"Total Edges in Graph: {len(G.edges)}")

    # If no valid nodes remain, return None
    if len(G.nodes) == 0:
        print("No valid nodes remain. Returning None.")
        return None

    # Compute layout
    # pos = nx.spring_layout(G, seed=42, k=0.5)

    graph_data = []
    for node, data in G.nodes(data=True):
        graph_data.append(
            {
                "name": data["name"],
                "type": data.get("node_type", "Unknown"),
                "colors": data.get("colors", "Unknown"),
                "mana_cost": data.get("mana_cost", "Unknown"),
                "retrievalCount": data.get("retrievalCount", 0),
                "associated_IDs_count": len(data.get("ids", [])),
                "connected_concepts_count": G.degree(
                    node
                ),  # Number of connected concepts
            }
        )

    # Convert to DataFrame
    graph_df = pd.DataFrame(graph_data)
    return graph_df


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
#         data.get("name", "Unknown") for _, data in G.nodes(data=True) if "name" in data
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
#             f"Connecting Concepts: {concept_count}<br>"  # Include node's degree (connections)
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
