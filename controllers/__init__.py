"""
Initialization file for the controllers package.

- Re-exports controller functions for easier access.
- Uses the centralized logger from utils.
- Ensures `get_mongo_cards` is accessible within controllers.
"""

from models.mongo import get_mongo_cards

# Re-export controller functions
from .functions import (count_card_names, count_primary_colors, get_bar_df,
                        get_cards_df, get_pie_df)

__all__ = [
    "get_cards_df",
    "get_pie_df",
    "get_bar_df",
    "count_primary_colors",
    "count_card_names",
    "get_mongo_cards",
]
