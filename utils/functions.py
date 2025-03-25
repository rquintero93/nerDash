"""
Utility functions.

"""
from typing import Union

import pandas as pd
from loguru import logger

from utils import constants

# Configure Loguru
logger.remove()  # Remove default logger to customize settings
logger.add("utils/function_logs.log", rotation="10MB", level="INFO", format="{time} {level} {message}")

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

    if isinstance(data, pd.DataFrame) and (column is None or column not in data.columns):
        return (False, constants.ERROR_MESSAGE_COLUMN_NOT_IN_DF)
    
    else:
        return (True, None)

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
    if len(str( row )) == 0:
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

