'''
Constants used in the project

'''

import os

from dotenv import load_dotenv

#Mognodb connection string
dotenv_path = os.path.expanduser("~/Documents/DeSciWorld/nerdBot/.env")
load_dotenv(dotenv_path)
MONGO_URI = os.getenv("MONGO_URI")

# Define a color map for MTG colors
MTG_COLOR_MAP = {
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
