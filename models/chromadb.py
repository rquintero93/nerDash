import json
import os

import pandas as pd
import requests
from dotenv import load_dotenv

pd.set_option("display.max_columns", None)

dotenv_path = os.path.expanduser("~/Documents/DeSciWorld/nerdBot/.env")
load_dotenv(dotenv_path)
API_KEY = os.getenv("API_KEY")

# # Check if the .env file exists at the specified path
# if not os.path.exists(dotenv_path):
#     print(f".env file not found at: {dotenv_path}")
# else:
#     # Load the .env file
#     success = load_dotenv(dotenv_path)
#     if not success:
#         print("Failed to load .env file")
#     else:
#         print(".env file loaded successfully")


def get_chroma(limit: int, offset: int) -> pd.DataFrame:
    response = requests.post(
        # " https://chroma.bot.fun/api/v2/tenants/default_tenant/databases/default_database/collections",
        "https://chroma.bot.fun/api/v2/tenants/default_tenant/databases/default_database/collections/9937882c-0661-4ff5-bc6f-f0aff3203bd4/get",
        headers={
            "x-api-key": API_KEY,
        },
        # json={
        #     "limit": f"{limit}",
        #     "offset": f"{offset}",
        #     "include": ["documents", "metadatas"],
        # },
    )

    # # Print the status code and response content for debugging
    # print(f"Status Code: {response.status_code}")
    # print(f"Response Content: {response.content}")

    # Decode and parse the JSON
    decoded_response = response.content.decode("utf-8")
    json_data = json.loads(decoded_response)

    # Combine the data into a list of rows
    rows = []
    for i in range(len(json_data["ids"])):
        row = {
            "id": json_data["ids"][i],
            "document": json_data["documents"][i],
            **json_data["metadatas"][i],  # Merge metadata fields into the row
        }
        rows.append(row)

    # Create a DataFrame
    df = pd.DataFrame(rows)

    # df = df[df["source"] == "MTG_Cards"]

    # Define regex to extract key-value pairs from the document column
    # pattern = (
    #     r"Name: (?P<Name>[^\n]*)\n"
    #     r"    Type: (?P<Type>[^\n]*)\n"
    #     r"    Subtypes: (?P<Subtypes>[^\n]*)\n"
    #     r"    Supertypes: (?P<Supertypes>[^\n]*)\n"
    #     r"    Text: (?P<Text>.*?)\n"
    #     r"    Flavor Texts: (?P<FlavorTexts>[^\n]*)\n"
    #     r"    Mana Cost: (?P<ManaCost>[^\n]*)\n"
    #     r"    Mana Value: (?P<ManaValue>[^\n]*)\n"
    #     r"    Colors: (?P<Colors>[^\n]*)\n"
    #     r"    Color Identity: (?P<ColorIdentity>[^\n]*)\n"
    #     r"    Power/Toughness: (?P<PowerToughness>[^\n]*)\n"
    #     r"    Keywords: (?P<Keywords>[^\n]*)\n"
    #     r"    Sets: (?P<Sets>[^\n]*)"
    # )
    #
    # # Extract data from document column into new columns
    # expanded_columns = df["document"].str.extract(pattern)
    #
    # # Combine extracted columns with the original DataFrame (dropping the document column)
    # df = df.drop(columns=["document"]).join(expanded_columns)
    #
    # Display the DataFrame
    return df
