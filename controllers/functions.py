"""
Controller functions for processing data.

"""


from collections import Counter
from typing import Union

import pandas as pd
from loguru import logger

from models import get_mongo_cards
from utils import clean_colors, clean_timestamp

# Configure Loguru
logger.remove()  # Remove default logger to customize settings
logger.add("controllers/function_logs.log", rotation="10MB", level="INFO", format="{time} {level} {message}")

def get_cards_df() -> pd.DataFrame:
    '''
    Builds the dataframe for viewing in dashboard. Merges all relevant collections.

    Returns:
        df_cards (pd.DataFrame): The dataframe containing all the cards.
    '''

    ragdb_cards = get_mongo_cards(db="ragDB", target_collection="kengrams")
    nerdb_cards = get_mongo_cards(db="nerDB",target_collection="kengrams")

    df_cards = pd.concat([ragdb_cards, nerdb_cards], ignore_index=True)
    df_cards['colors'] = df_cards['colors'].apply(lambda x: clean_colors(x))

    df_cards['updatedAt'] = df_cards['updatedAt'].apply(lambda x: clean_timestamp(x))
    df_cards['createdAt'] = df_cards['createdAt'].apply(lambda x: clean_timestamp(x))
    return df_cards


def get_pie_df(data: pd.DataFrame = None, column: str = None) -> pd.DataFrame:
    '''
    Prepares the data for a pie chart.

    Args:
        data (pd.DataFrame): The data to plot.
        column (str): The column to plot from the DataFrame.

    Returns:
        pie_counts (pd.DataFrame): The data to plot.

    '''
    data[column] = data[column].apply(lambda x: ''.join(sorted(x)) if isinstance(x, list) else x)
    
    pie_counts = data[column].value_counts().reset_index()
    pie_counts.columns = [column, 'count']
    
    # Truncate legend labels
    pie_counts[column] = pie_counts[column].str[:15]

    return pie_counts

def get_line_df(data: pd.DataFrame = None, x: str = None, y:str = None) -> pd.DataFrame:
    '''
    Prepares the data for a line chart.

    Args:
    data (pd.DataFrame): The data to plot.
    column (str): The column to plot from the DataFrame.

    Returns:
      line_counts (pd.DataFrame): The data to plot.
    '''
    
    data[y] = pd.to_datetime(data[y], errors='coerce')
    filtered = data.dropna(subset=[y])

    line_counts = filtered.groupby(filtered[y].dt.date)[x].count().reset_index(name='count')


    return line_counts

def get_bar_df(data: Union[pd.DataFrame, dict] = None,  column: str=None) -> pd.DataFrame:
    '''
    Prepares the data for a bar chart.

    Args:
    data (Union[pd.DataFrame, dict]): The data to plot. If a DataFrame, the column argument must be provided.
    column (str): The column to plot from the DataFrame.

    Returns:
       bar_counts (pd.DataFrame): The data to plot.
    '''

    if isinstance(data, pd.DataFrame):
        bar_counts = data[column].value_counts().reset_index()
        bar_counts.columns = [column, 'count']

    else:
        bar_counts = pd.DataFrame(list(data.items()), columns=['key', 'count'])
        bar_counts = bar_counts.sort_values('count', ascending=False)

    return bar_counts


def count_primary_colors(data : pd.DataFrame,concept : str) -> dict:
    '''
    Count the number of times each primary color appears in the data.

    Args:
        data (pd.DataFrame): The data to count colors from.
        concept (str): The column name containing the colors.

    Returns:
        dict: A dictionary containing the count of each color.
    '''

    color_counter = Counter()
    for concept in data[concept]:
        if concept:
            color_counter.update(concept)

    return dict(color_counter)


def count_card_names(df : pd.DataFrame, names : str) -> dict:
    '''
    Count the number of times each concept appears in the data.

    Args:
        df (pd.DataFrame): The data to count concepts from.
        concept (str): The column name containing the concepts.

    Returns:
        dict: A dictionary containing the count of each concept.
    '''

    name_counter = Counter()
    for name in df[names]:
        if name:
            # If it's a list, add each item as a single unit
            if isinstance(name, list):
                name_counter.update([tuple(name)])  # Convert list to tuple to make it hashable
            else:
                name_counter.update([name])  # Add the string as a single unit

    return dict(name_counter)


# def make_agg_df(mongo_merge_df):
#
#     def concat_unique(series):
#         """Ensure lists remain lists, and unique values are preserved."""
#         if series.apply(lambda x: isinstance(x, list)).any():
#             unique_items = set()
#             result = []
#             for sublist in series.dropna():
#                 for item in sublist:
#                     if item not in unique_items:
#                         unique_items.add(item)
#                         result.append(item)
#             return result  # Keep as a list
#
#         elif series.dtype == "object":
#             seen = set()
#             result = [
#                 item
#                 for sublist in series.dropna().astype(str)
#                 for item in sublist.split("; ")
#                 if not (item in seen or seen.add(item))
#             ]
#             return result  # Keep as list
#
#         else:
#             seen = set()
#             return [x for x in series.dropna() if not (x in seen or seen.add(x))]
#
#     # Convert timestamp to datetime and sort
#     mongo_merge_df["metadata.timestamp"] = pd.to_datetime(
#         mongo_merge_df["metadata.timestamp"]
#     )
#     mongo_merge_df = mongo_merge_df.sort_values("metadata.timestamp")
#
#     # Convert `id` column to string
#     mongo_merge_df["id"] = mongo_merge_df["id"].astype(str)
#     mongo_merge_df["metadata.timestamp"] = mongo_merge_df["metadata.timestamp"].astype(
#         str
#     )
#
#     # Define aggregation functions
#     agg_funcs = {
#         "retrievalCount": "sum",
#         "id": concat_unique,
#         "metadata.data.colors": concat_unique,
#         "metadata.data.manaCost": concat_unique,
#         "metadata.data.type": concat_unique,
#         "metadata.data.subtypes": concat_unique,
#         "metadata.data.text": concat_unique,
#         "metadata.data.flavorText": concat_unique,
#         "metadata.data.power": concat_unique,
#         "metadata.data.toughness": concat_unique,
#         "metadata.timestamp": concat_unique,
#         "metadata.chatId": concat_unique,
#         "metadata.userId": concat_unique,
#         "metadata.botId": concat_unique,
#         "metadata.relatedCards": concat_unique,
#         "metadata.relatedLore": concat_unique,
#     }
#
#     # Group by 'metadata.data.name' and aggregate
#     mongo_agg_df = mongo_merge_df.groupby("metadata.data.name", sort=False).agg(
#         agg_funcs
#     )
#
#     # Reset index if needed
#     mongo_agg_df = mongo_agg_df.reset_index()
#
#     return mongo_agg_df
