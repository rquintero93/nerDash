"""
Utility functions for processing data.

"""


from collections import Counter

import pandas as pd


def count_colors(df):
    color_counter = Counter()
    for colors in df['colors']:
        if colors:
            color_counter.update(colors)
    return dict(color_counter)

def clean_timestamp(row):
    try:
        cleaned_ts = pd.to_datetime(row, unit="ms")
    except Exception as e:
        print(f"Error converting timestamp: {e}")
        cleaned_ts = None
    return cleaned_ts

def clean_colors(row):
    if row is None:
        return None
    normalized_colors = []
    row = row if isinstance(row, list) else [row]
    if len(row) == 0:
        return None
    else:
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

    def sort_strings(strings):
        if strings is None:
            return None
        strings = [s for s in strings if s is not None]
        return sorted(list(set(strings)))

    return sort_strings(normalized_colors)

def clean_mana_cost(row):
    if row is None:
        return None
    normalized_mana_cost = []
    row = row if isinstance(row, list) else [row]
    if len(row) == 0:
        return None
    else:
        for mana_cost in row:
            mana = mana_cost.upper().replace("{", "").replace("}", "").replace("/", "")
            normalized_mana_cost.append(mana)
    return set(normalized_mana_cost) if normalized_mana_cost else None



def make_agg_df(mongo_merge_df):

    def concat_unique(series):
        """Ensure lists remain lists, and unique values are preserved."""
        if series.apply(lambda x: isinstance(x, list)).any():
            unique_items = set()
            result = []
            for sublist in series.dropna():
                for item in sublist:
                    if item not in unique_items:
                        unique_items.add(item)
                        result.append(item)
            return result  # Keep as a list

        elif series.dtype == "object":
            seen = set()
            result = [
                item
                for sublist in series.dropna().astype(str)
                for item in sublist.split("; ")
                if not (item in seen or seen.add(item))
            ]
            return result  # Keep as list

        else:
            seen = set()
            return [x for x in series.dropna() if not (x in seen or seen.add(x))]

    # Convert timestamp to datetime and sort
    mongo_merge_df["metadata.timestamp"] = pd.to_datetime(
        mongo_merge_df["metadata.timestamp"]
    )
    mongo_merge_df = mongo_merge_df.sort_values("metadata.timestamp")

    # Convert `id` column to string
    mongo_merge_df["id"] = mongo_merge_df["id"].astype(str)
    mongo_merge_df["metadata.timestamp"] = mongo_merge_df["metadata.timestamp"].astype(
        str
    )

    # Define aggregation functions
    agg_funcs = {
        "retrievalCount": "sum",
        "id": concat_unique,
        "metadata.data.colors": concat_unique,
        "metadata.data.manaCost": concat_unique,
        "metadata.data.type": concat_unique,
        "metadata.data.subtypes": concat_unique,
        "metadata.data.text": concat_unique,
        "metadata.data.flavorText": concat_unique,
        "metadata.data.power": concat_unique,
        "metadata.data.toughness": concat_unique,
        "metadata.timestamp": concat_unique,  # Ensures order from sorted dataframe
        "metadata.chatId": concat_unique,
        "metadata.userId": concat_unique,
        "metadata.botId": concat_unique,
        "metadata.relatedCards": concat_unique,
        "metadata.relatedLore": concat_unique,
    }

    # Group by 'metadata.data.name' and aggregate
    mongo_agg_df = mongo_merge_df.groupby("metadata.data.name", sort=False).agg(
        agg_funcs
    )

    # Reset index if needed
    mongo_agg_df = mongo_agg_df.reset_index()

    return mongo_agg_df
