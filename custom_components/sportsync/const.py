"""Constants for SportSync integration."""
from __future__ import annotations

from typing import Final

DOMAIN: Final = "sportsync"

# Config keys
CONF_FAVORITE_SPORTS: Final = "favorite_sports"
CONF_FAVORITE_TEAMS: Final = "favorite_teams"
CONF_FAVORITE_LEAGUES: Final = "favorite_leagues"
CONF_SCAN_INTERVAL: Final = "scan_interval"

# Defaults
DEFAULT_SCAN_INTERVAL: Final = 1800  # 30 minutes

# Sport types with metadata
SPORT_TYPES: Final[dict[str, dict[str, str]]] = {
    "football": {"name": "Fotboll", "icon": "mdi:soccer", "emoji": "⚽"},
    "hockey": {"name": "Ishockey", "icon": "mdi:hockey-puck", "emoji": "🏒"},
    "basketball": {"name": "Basket", "icon": "mdi:basketball", "emoji": "🏀"},
    "tennis": {"name": "Tennis", "icon": "mdi:tennis", "emoji": "🎾"},
    "golf": {"name": "Golf", "icon": "mdi:golf", "emoji": "⛳"},
    "handball": {"name": "Handboll", "icon": "mdi:handball", "emoji": "🤾"},
    "motorsport": {"name": "Motorsport", "icon": "mdi:racing-helmet", "emoji": "🏎️"},
    "cycling": {"name": "Cykling", "icon": "mdi:bike", "emoji": "🚴"},
    "skiing": {"name": "Skidor", "icon": "mdi:ski", "emoji": "⛷️"},
    "biathlon": {"name": "Skidskytte", "icon": "mdi:target", "emoji": "🎯"},
    "alpine": {"name": "Alpint", "icon": "mdi:ski", "emoji": "⛷️"},
    "athletics": {"name": "Friidrott", "icon": "mdi:run", "emoji": "🏃"},
    "swimming": {"name": "Simning", "icon": "mdi:swim", "emoji": "🏊"},
    "boxing": {"name": "Boxning", "icon": "mdi:boxing-glove", "emoji": "🥊"},
    "mma": {"name": "MMA", "icon": "mdi:karate", "emoji": "🥋"},
    "american_football": {"name": "Amerikansk fotboll", "icon": "mdi:football", "emoji": "🏈"},
    "baseball": {"name": "Baseball", "icon": "mdi:baseball", "emoji": "⚾"},
    "volleyball": {"name": "Volleyboll", "icon": "mdi:volleyball", "emoji": "🏐"},
    "table_tennis": {"name": "Bordtennis", "icon": "mdi:table-tennis", "emoji": "🏓"},
    "badminton": {"name": "Badminton", "icon": "mdi:badminton", "emoji": "🏸"},
    "rugby": {"name": "Rugby", "icon": "mdi:rugby", "emoji": "🏉"},
    "horse_racing": {"name": "Trav/Galopp", "icon": "mdi:horse", "emoji": "🏇"},
    "snooker": {"name": "Snooker/Biljard", "icon": "mdi:billiards", "emoji": "🎱"},
    "darts": {"name": "Dart", "icon": "mdi:bullseye-arrow", "emoji": "🎯"},
    "padel": {"name": "Padel", "icon": "mdi:tennis", "emoji": "🎾"},
    "floorball": {"name": "Innebandy", "icon": "mdi:hockey-sticks", "emoji": "🏑"},
    "bandy": {"name": "Bandy", "icon": "mdi:hockey-sticks", "emoji": "🏑"},
    "curling": {"name": "Curling", "icon": "mdi:curling", "emoji": "🥌"},
    "esports": {"name": "E-sport", "icon": "mdi:controller", "emoji": "🎮"},
    "sailing": {"name": "Segling", "icon": "mdi:sail-boat", "emoji": "⛵"},
    "winter_sports": {"name": "Vintersport", "icon": "mdi:snowflake", "emoji": "❄️"},
    "other": {"name": "Övrigt", "icon": "mdi:trophy", "emoji": "🏆"},
}

# Sport keyword mappings for auto-detection
SPORT_KEYWORDS: Final[dict[str, str]] = {
    # Football
    "fotboll": "football",
    "soccer": "football",
    "premier league": "football",
    "la liga": "football",
    "serie a": "football",
    "bundesliga": "football",
    "allsvenskan": "football",
    "superettan": "football",
    "champions league": "football",
    "europa league": "football",
    "conference league": "football",
    "fotbolls-vm": "football",
    "fotbolls-em": "football",
    "vm-kval fotboll": "football",
    "em-kval fotboll": "football",
    "nations league": "football",
    "vm i fotboll": "football",
    "em i fotboll": "football",
    # Hockey
    "ishockey": "hockey",
    "hockey": "hockey",
    "nhl": "hockey",
    "shl": "hockey",
    "hockeyallsvenskan": "hockey",
    "hockeyettan": "hockey",
    "tre kronor": "hockey",
    "khl": "hockey",
    # Basketball
    "basket": "basketball",
    "nba": "basketball",
    "euroleague": "basketball",
    # Tennis
    "tennis": "tennis",
    "wimbledon": "tennis",
    "us open tennis": "tennis",
    "australian open": "tennis",
    "roland garros": "tennis",
    "atp": "tennis",
    "wta": "tennis",
    # Golf
    "golf": "golf",
    "pga": "golf",
    "lpga": "golf",
    "ryder cup": "golf",
    # Handball
    "handboll": "handball",
    # Motorsport
    "formel 1": "motorsport",
    "formel 2": "motorsport",
    "formel 3": "motorsport",
    "f1": "motorsport",
    "motogp": "motorsport",
    "moto2": "motorsport",
    "moto3": "motorsport",
    "rally": "motorsport",
    "rallycross": "motorsport",
    "nascar": "motorsport",
    "indycar": "motorsport",
    "dtm": "motorsport",
    "formel e": "motorsport",
    "wrc": "motorsport",
    # Cycling
    "cykling": "cycling",
    "tour de france": "cycling",
    "giro": "cycling",
    "vuelta": "cycling",
    # Winter sports
    "skidor": "skiing",
    "längdskidor": "skiing",
    "längdskidåkning": "skiing",
    "world cup skidor": "skiing",
    "skidskytte": "biathlon",
    "biathlon": "biathlon",
    "alpint": "alpine",
    "slalom": "alpine",
    "störtlopp": "alpine",
    "super-g": "alpine",
    "storslalom": "alpine",
    "utför": "alpine",
    "curling": "curling",
    "vintersport": "winter_sports",
    # Athletics
    "friidrott": "athletics",
    "friidrotts": "athletics",
    "maraton": "athletics",
    "diamond league": "athletics",
    # Swimming
    "simning": "swimming",
    "sim-": "swimming",
    # Combat
    "boxning": "boxing",
    "tungviktsboxning": "boxing",
    "mma": "mma",
    "ufc": "mma",
    # American sports
    "nfl": "american_football",
    "super bowl": "american_football",
    "mlb": "baseball",
    "baseball": "baseball",
    # Other
    "volleyboll": "volleyball",
    "bordtennis": "table_tennis",
    "badminton": "badminton",
    "rugby": "rugby",
    "trav": "horse_racing",
    "galopp": "horse_racing",
    "snooker": "snooker",
    "biljard": "snooker",
    "dart": "darts",
    "padel": "padel",
    "innebandy": "floorball",
    "bandy": "bandy",
    "e-sport": "esports",
    "esport": "esports",
    "counter-strike": "esports",
    "league of legends": "esports",
    "segling": "sailing",
}
