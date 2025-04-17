"""
Nothing to see here, just some exploratory data analysis.
not connected to the main project

"""

import pandas as pd

from controllers import get_cards_df
from controllers.nlp import compute_embeddings

pd.set_option("display.max_columns", None)

df_cards = get_cards_df()

descriptions = df_cards["flavorText"].tolist()

embeddings, st_model = compute_embeddings(descriptions)

print(embeddings)
