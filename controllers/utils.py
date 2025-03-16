"""
Utility functions for processing data.

"""


from collections import Counter
from typing import Union

import pandas as pd

import utils.constants as constants
from models.mongo import get_mongo_cards


def is_valid_chart_data(data: Union[pd.DataFrame, dict] = None, column : str = None) -> tuple[bool, str]:
    '''
    Validate the data for a bar chart. adds error_code for invalid data.

    Args:
        data (Union[pd.DataFrame, dict]): The data to plot. If a DataFrame, the column argument must be provided.
        column (str): The column to plot from the DataFrame.

    Returns:
        (bool): True if the data is valid, False otherwise.
        error_code (str): The error code if the data is invalid.
    '''

    if data is None:
        return (False, constants.ERROR_MESSAGE_DATA_NONE)

    if not isinstance(data, pd.DataFrame) and not isinstance(data, dict):
        return (False, constants.ERROR_MESSAGE_DATA_NOT_DF_OR_DICT)

    if isinstance(data, pd.DataFrame) and column not in data.columns:
        return (False, constants.ERROR_MESSAGE_COLUMN_NOT_IN_DF)
    
    else:
        return (True, None)


def get_pie_counts(data: pd.DataFrame = None, column: str = None) -> pd.DataFrame:
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


def get_bar_counts(data: Union[pd.DataFrame, dict] = None,  column: str=None) -> pd.DataFrame:
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


def count_concept(df : pd.DataFrame, concept : str) -> dict:
    '''
    Count the number of times each concept appears in the data.

    Args:
        df (pd.DataFrame): The data to count concepts from.
        concept (str): The column name containing the concepts.

    Returns:
        dict: A dictionary containing the count of each concept.
    '''

    concept_counter = Counter()
    for concept_value in df[concept]:
        if concept_value:
            # If it's a list, add each item as a single unit
            if isinstance(concept_value, list):
                concept_counter.update([tuple(concept_value)])  # Convert list to tuple to make it hashable
            else:
                concept_counter.update([concept_value])  # Add the string as a single unit

    return dict(concept_counter)


def clean_timestamp(row : pd.Series) -> pd.Timestamp:
    '''
    Convert a timestamp to a pandas Timestamp object.

    Args:
        row (pd.Series): The row containing the timestamp.

    Returns:
        pd.Timestamp: The cleaned timestamp.
    '''

    try:
        cleaned_ts = pd.to_datetime(row, unit="ms")
    except Exception as e:
        print(f"Error converting timestamp: {e}")
        cleaned_ts = None

    return cleaned_ts


def sort_strings(strings:list) -> list:
    '''
    Sort a list of strings and remove duplicates.

    Args:
        strings (list): The list of strings to sort.

    Returns:
    list: The sorted list of strings.
    '''

    if strings is None:
        return None
    strings = [s for s in strings if s is not None]

    return sorted(list(set(strings)))


def is_row_valid(row: pd.Series) -> bool:
    '''
    Check if a row is valid.

    Args:
        row (pd.Series): The row to check.

    Returns:
    bool: True if the row is valid, False otherwise.
    '''
    if row is None:
        return False
    if len(row) == 0:
        return False

    else:
        return True


def clean_colors(row: pd.Series) -> list:
    '''
    Normalize the colors in a row to MTG defaults.

    Args:
        row (pd.Series): The row containing the colors.

    Returns:
        list: The normalized colors.
    '''

    #input validation
    if not is_row_valid(row):
        return None

    row = row if isinstance(row, list) else [row]
    normalized_colors = []
    for color in row:
        color = str(color).title().strip()
        if not color:
            normalized_colors.append("Colorless")
        else:
            normalized_colors.append(constants.COLOR_TO_LABEL_MAP.get(color, color if len(color) == 1 else "Colorless"))

    return sort_strings(normalized_colors)


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

    return df_cards


def clean_mana_cost(row : pd.Series) -> set:
    '''
    Normalize the mana cost in a row.

    Args:
        row (pd.Series): The row containing the mana cost.

    Returns:
        set: The normalized mana cost.
    '''

    #input validation
    if not is_row_valid(row):
        return None

    row = row if isinstance(row, list) else [row]
    normalized_mana_cost = []
    for mana_cost in row:
        mana = mana_cost.upper().replace("{", "").replace("}", "").replace("/", "")
        normalized_mana_cost.append(mana)

    return set(normalized_mana_cost) if normalized_mana_cost else None



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
