"""
Initialization file for the views package.

- Re-exports graphing functions for easier access.
- Uses the centralized logger from utils.
"""

# Re-export graphing functions
from .graphs import (
                     make_bar_chart,
                     make_line_chart,
                     make_pie_chart,
                     make_sentiment_over_time,
                     visualize_topic_heatmap,
                     visualize_topic_hierarchy,
                     visualize_tsne,
                     visulize_topic_barchart,
)

__all__ = [
                     "make_bar_chart",
                     "make_line_chart",
                     "make_pie_chart",
                     "make_sentiment_over_time",
                     "visualize_topic_heatmap",
                     "visualize_topic_hierarchy",
                     "visualize_tsne",
                     "visulize_topic_barchart"
]
