"""
Initialization file for the utils package.

- Re-exports utility functions for easier access.
- Sets up Loguru for structured logging.
- Imports constants for global use.
"""

from loguru import logger

from . import constants
# Re-export utility functions. This allows users to import them directly from the package.
from .functions import (clean_colors, clean_mana_cost, clean_timestamp,
                        is_row_valid, is_valid_chart_data, sort_strings)

# Configure Loguru
logger.remove()  # Remove default logger to customize settings
logger.add("utils.log", rotation="10MB", level="INFO", format="{time} {level} {message}")

# Define what should be imported when using `from utils import *`
__all__ = [
    "is_valid_chart_data",
    "clean_timestamp",
    "sort_strings",
    "is_row_valid",
    "clean_colors",
    "clean_mana_cost",
    "constants",
    "logger",
]
