import os

import pandas as pd
import requests
from dotenv import load_dotenv

pd.set_option("display.max_columns", None)

dotenv_path = os.path.expanduser("~/Documents/DeSciWorld/nerdBot/.env")
load_dotenv(dotenv_path)
API_KEY = os.getenv("API_KEY")

if not os.path.exists(dotenv_path):
    print(f".env file not found at: {dotenv_path}")
else:
    success = load_dotenv(dotenv_path)
    if not success:
        print("Failed to load .env file")
    else:
        print(".env file loaded successfully")

response = requests.get(
    " https://chroma.bot.fun/api/v2/tenants/default_tenant/databases/default_database/collections",
    headers={
        "x-api-key": API_KEY,
    },
    json={
        # "name": "Brain_thought_store",
        "limit": "100",
        "offset": "0",
        "include": ["embeddings", "documents", "metadatas"],
    },
)

# # Print the status code and response content for debugging
# print(f"Status Code: {response.status_code}")
# print(f"Response Content: {response.content}")

json_string = response.content.decode("utf-8")

data = pd.read_json(json_string)
print(data)
