import pandas as pd

from controllers.functions import clean_colors, clean_timestamp
# from chromadb import get_chroma
from models.mongo import get_mongo_cards
from views.graphs import make_bar_chart, make_pie_chart

pd.set_option("display.max_columns", None)

ragdb_cards = get_mongo_cards(db="ragDB", target_collection="kengrams")
nerdb_cards = get_mongo_cards(db="nerDB",target_collection="kengrams")
df_cards = pd.concat([ragdb_cards, nerdb_cards], ignore_index=True)

df_cards['colors'] = df_cards['colors'].apply(lambda x: clean_colors(x))
# botid_pie_chart = make_pie_chart(df_ragdb_gs_cards,'botId')
#
# botid_pie_chart.show()

# color_counter = count_colors(df_cards)
# print(color_counter)

df_cards['updatedAt'] = df_cards['updatedAt'].apply(lambda x: clean_timestamp(x))
df_cards['createdAt'] = df_cards['createdAt'].apply(lambda x: clean_timestamp(x))
type_pie_chart = make_pie_chart(data=df_cards,column='type')


action_bar_chart = make_bar_chart(data=df_cards,column='action')

action_bar_chart.show()
