"""
Constants used in the project

"""

import os

from dotenv import load_dotenv

# Mognodb connection string
# Load environment variables
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(ENV_PATH)
MONGO_URI = os.getenv("MONGO_URI")

# Fall back to environment variables if .env file is not found
if not MONGO_URI:
    MONGO_URI = os.environ.get("MONGO_URI")
    if not MONGO_URI:
        raise EnvironmentError("MONGO_URI environment variable not set")

# Define color maps from MTG colors
COLOR_TO_HEX_MAP = {
    "B": "#000000",  # Black
    "BGU": "#2E8B57",  # Sultai
    "BR": "#8B0000",  # Rakdos
    "BGR": "#556B2F",  # Jund (was BRG)
    "BRW": "#CD5C5C",  # Mardu
    "C": "#D3D3D3",  # Colorless
    "G": "#008000",  # Green
    "R": "#FF0000",  # Red
    "GR": "#32CD32",  # Gruul (was RG)
    "GRW": "#FFD700",  # Naya (was RGW)
    "GRU": "#20B2AA",  # Temur (was RUG)
    "U": "#1E90FF",  # Blue
    "BU": "#4682B4",  # Dimir (was UB)
    "BRU": "#8A2BE2",  # Grixis (was UBR)
    "RU": "#FF6347",  # Izzet (was UR)
    "RUW": "#FF4500",  # Jeskai (was URW)
    "W": "#FFFFFF",  # White
    "BW": "#A9A9A9",  # Orzhov (was WB)
    "BGW": "#9ACD32",  # Abzan (was WBG)
    "GW": "#98FB98",  # Selesnya (was WG)
    "RW": "#FFA07A",  # Boros (was WR)
    "UW": "#ADD8E6",  # Azorius (was WU)
    "BUW": "#87CEEB",  # Esper (was WUB)
    "GUW": "#90EE90",  # Bant (was WUG)
    "BGRUW": "#DAA520",  # Rainbow (was WUBRG)
}

COLOR_TO_LABEL_MAP = {
    "White": "W",
    "Blue": "U",
    "Black": "B",
    "Red": "R",
    "Green": "G",
    "Colorless": "C",
    "Azorius": "WU",
    "Orzhov": "WB",
    "Boros": "WR",
    "Selesnya": "WG",
    "Dimir": "UB",
    "Izzet": "UR",
    "Rakdos": "BR",
    "Gruul": "RG",
    "Bant": "WUG",
    "Esper": "WUB",
    "Grixis": "UBR",
    "Jund": "BRG",
    "Naya": "RGW",
    "Abzan": "WBG",
    "Jeskai": "URW",
    "Sultai": "BGU",
    "Mardu": "BRW",
    "Temur": "RUG",
    "Rainbow": "WUBRG",
}

ERROR_MESSAGE_DATA_NONE = "Data cannot be None."
ERROR_MESSAGE_DATA_NOT_DF_OR_DICT = "Data must be a pandas DataFrame or a dictionary"
ERROR_MESSAGE_COLUMN_NOT_IN_DF = "column argument is not in the DataFrame data."
