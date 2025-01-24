import pandas as pd

# from chromadb import get_chroma
from mongo import get_globalstates_cards, get_globalstates_retrievalCount

# from mongo import get_history


def main():
    # define main tables
    df_gs_cards = get_globalstates_cards()
    df_gs_retrievalCount = get_globalstates_retrievalCount()
    # df_chroma = get_chroma(limit=20000)
    # df_history = get_history()
    merged_df = pd.merge(df_gs_cards, df_gs_retrievalCount, on="id", how="left")

    return merged_df


if __name__ == "__main__":
    df = main()
