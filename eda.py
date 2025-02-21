import pandas as pd

from graphs import make_bar_chart, make_pie_chart
# from chromadb import get_chroma
from mongo import get_mongo_cards

pd.set_option("display.max_columns", None)

df_ragdb_gs_cards = get_mongo_cards(db="ragDB",target_collection="kengrams")

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
            # if isinstance(color, list):
            #     for color in color:
            if color is None or len(color) == 0:
                normalized_colors.append("Colorless")
                continue
            else:
                if color == "White":
                    normalized_colors.append("W")
                    continue
                if color == "Blue":
                    normalized_colors.append("U")
                    continue
                if color == "Black":
                    normalized_colors.append("B")
                    continue
                if color == "Red":
                    normalized_colors.append("R")
                    continue
                if color == "Green":
                    normalized_colors.append("G")
                    continue
                if color == "Colorless":
                    normalized_colors.append("C")
                    continue
                if color == "Azorius":
                    normalized_colors.append("WU")
                    continue
                if color == "Orzhov":
                    normalized_colors.append("WB")
                    continue
                if color == "Boros":
                    normalized_colors.append("WR")
                    continue
                if color == "Selesnya":
                    normalized_colors.append("WG")
                    continue
                if color == "Dimir":
                    normalized_colors.append("UB")
                    continue
                if color == "Izzet":
                    normalized_colors.append("UR")
                    continue
                if color == "Rakdos":
                    normalized_colors.append("BR")
                    continue
                if color == "Orzhov":
                    normalized_colors.append("BW")
                    continue
                if color == "Gruul":
                    normalized_colors.append("RG")
                    continue
                if color == "Orzhov":
                    normalized_colors.append("WB")
                    continue
                if color == "Azorius":
                    normalized_colors.append("WU")
                    continue
                if color == "Selesnya":
                    normalized_colors.append("WG")
                    continue
                if color == "Dimir":
                    normalized_colors.append("UB")
                    continue
                if color == "Izzet":
                    normalized_colors.append("UR")
                    continue
                if color == "Rakdos":
                    normalized_colors.append("BR")
                    continue
                if color == "Gruul":
                    normalized_colors.append("RG")
                    continue
                if color == "Bant":
                    normalized_colors.append("WUG")
                    continue
                if color == "Esper":
                    normalized_colors.append("WUB")
                    continue
                if color == "Grixis":
                    normalized_colors.append("UBR")
                    continue
                if color == "Jund":
                    normalized_colors.append("BRG")
                    continue
                if color == "Naya":
                    normalized_colors.append("RGW")
                    continue
                if color == "Abzan":
                    normalized_colors.append("WBG")
                    continue
                if color == "Jeskai":
                    normalized_colors.append("URW")
                    continue
                if color == "Sultai":
                    normalized_colors.append("BGU")
                    continue
                if color == "Mardu":
                    normalized_colors.append("BRW")
                    continue
                if color == "Temur":
                    normalized_colors.append("RUG")
                    continue
                if color == "Rainbow":
                    normalized_colors.append("WUBRG")
                    continue
                else:
                    if len(color) == 1:
                        normalized_colors.append(color)
                        continue
                    else:
                        normalized_colors.append("Colorless")
                        continue

    def sort_strings(strings):
        if strings is None:
            return None
        # Filter out None values from the list
        strings = [s for s in strings if s is not None]
        print(sorted(strings), type(strings))
        return sorted(list( set( strings ) ))

    return sort_strings( normalized_colors )


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



# botid_pie_chart = make_pie_chart(df_ragdb_gs_cards,'botId')
#
# botid_pie_chart.show()

type_pie_chart = make_pie_chart(df_ragdb_gs_cards,'type')
#
# type_pie_chart.show()


action_bar_chart = make_bar_chart(df_ragdb_gs_cards,'action')

action_bar_chart.show()
