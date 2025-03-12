"""
Utility functions for processing data.

"""


from collections import Counter

import pandas as pd


def count_colors(data : pd.DataFrame,concept : str) -> dict:
    '''
    Count the number of times each color appears in the data.

    Args:
        data (pd.DataFrame): The data to count colors from.
        concept (str): The column name containing the colors.
    '''

    concept_counter = Counter()
    for concept in data[concept]:
        if concept:
            concept_counter.update(concept)

    return dict(concept_counter)


def count_concept(df : pd.DataFrame, concept : str) -> dict:
    '''
    Count the number of times each concept appears in the data.

    Args:
        df (pd.DataFrame): The data to count concepts from.
        concept (str): The column name containing the concepts.
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
    '''

    if strings is None:
        return None
    strings = [s for s in strings if s is not None]

    return sorted(list(set(strings)))

def clean_colors(row: pd.Series) -> list:
    '''
    Normalize the colors in a row to MTG defaults.

    Args:
        row (pd.Series): The row containing the colors.
    '''

    #input validation
    if row is None:
        return None
    normalized_colors = []
    row = row if isinstance(row, list) else [row]
    if len(row) == 0:
        return None

    for color in row:
        color = str(color).title().strip()
        if color is None or len(color) == 0:
            normalized_colors.append("Colorless")
            continue
        else:
            if color == "White":
                normalized_colors.append("W")
            elif color == "Blue":
                normalized_colors.append("U")
            elif color == "Black":
                normalized_colors.append("B")
            elif color == "Red":
                normalized_colors.append("R")
            elif color == "Green":
                normalized_colors.append("G")
            elif color == "Colorless":
                normalized_colors.append("C")
            elif color == "Azorius":
                normalized_colors.append("WU")
            elif color == "Orzhov":
                normalized_colors.append("WB")
            elif color == "Boros":
                normalized_colors.append("WR")
            elif color == "Selesnya":
                normalized_colors.append("WG")
            elif color == "Dimir":
                normalized_colors.append("UB")
            elif color == "Izzet":
                normalized_colors.append("UR")
            elif color == "Rakdos":
                normalized_colors.append("BR")
            elif color == "Gruul":
                normalized_colors.append("RG")
            elif color == "Bant":
                normalized_colors.append("WUG")
            elif color == "Esper":
                normalized_colors.append("WUB")
            elif color == "Grixis":
                normalized_colors.append("UBR")
            elif color == "Jund":
                normalized_colors.append("BRG")
            elif color == "Naya":
                normalized_colors.append("RGW")
            elif color == "Abzan":
                normalized_colors.append("WBG")
            elif color == "Jeskai":
                normalized_colors.append("URW")
            elif color == "Sultai":
                normalized_colors.append("BGU")
            elif color == "Mardu":
                normalized_colors.append("BRW")
            elif color == "Temur":
                normalized_colors.append("RUG")
            elif color == "Rainbow":
                normalized_colors.append("WUBRG")
            else:
                if len(color) == 1:
                    normalized_colors.append(color)
                else:
                    normalized_colors.append("Colorless")


    return sort_strings(normalized_colors)

def clean_mana_cost(row : pd.Series) -> set:
    '''
    Normalize the mana cost in a row.

    Args:
        row (pd.Series): The row containing the mana cost.
    '''

    #input validation
    if row is None:
        return None
    normalized_mana_cost = []
    row = row if isinstance(row, list) else [row]
    if len(row) == 0:
        return None

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
