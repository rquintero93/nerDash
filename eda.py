import pandas as pd
import plotly.express as px

pd.set_option("display.max_columns", None)

df = pd.read_csv("full_table_240125.csv")

df = df.reset_index()

df["metadata.timestamp"] = df["metadata.timestamp"].astype(int)

df["metadata.timestamp"] = pd.to_datetime(df["metadata.timestamp"], unit="ms")

describe = df.describe(include="all")

retrievalCount = df.sort_values("retrievalCount", ascending=False)

# # Create scatter plot
# fig = px.line(
#     df,
#     x="metadata.timestamp",  # X-axis data
#     y="retrievalCount",  # Y-axis data
#     # color="",  # Color based on a column
#     title="Scatter Plot Example",  # Title of the plot
#     labels={"x": "X-Axis", "y": "Y-Axis"},  # Axis labels
# )
#
# # Show plot
# fig.show()

retrievalCount = (
    retrievalCount.groupby("metadata.data.name")["retrievalCount"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

fig = px.bar(
    retrievalCount,
    y="metadata.data.name",  # X-axis data
    x="retrievalCount",  # Y-axis data
    title="Bar Chart Example",  # Title of the chart
    labels={"metadata.data.name": "Name", "retrievalCount": "Count"},  # Axis labels
    color="metadata.data.name",  # Optional: Different colors for bars
    text="retrievalCount",  # Optional: Show values on bars
    orientation="h",
)

# Update layout for better visuals
fig.update_traces(textposition="outside")  # Position text outside bars
fig.update_layout(
    yaxis_title="Name",  # Custom X-axis title
    xaxis_title="Count",  # Custom Y-axis title
    uniformtext_minsize=8,  # Minimum font size for bar text
    uniformtext_mode="hide",  # Hide overlapping text
)

# Show plot
fig.show()
