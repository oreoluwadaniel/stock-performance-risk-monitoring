"""
config.py
All project settings live here. Change things ONCE, in this file only.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ---------------- Watchlist ----------------
TICKERS = ["AAPL", "MSFT", "JPM", "V", "XOM", "CVX", "PG", "MCD", "JNJ", "UNH"]

# Company name + sector for dim_ticker
SECTORS = {
    "AAPL": ("Apple Inc.", "Technology"),
    "MSFT": ("Microsoft Corp.", "Technology"),
    "JPM":  ("JPMorgan Chase", "Financials"),
    "V":    ("Visa Inc.", "Financials"),
    "XOM":  ("Exxon Mobil", "Energy"),
    "CVX":  ("Chevron", "Energy"),
    "PG":   ("Procter & Gamble", "Consumer"),
    "MCD":  ("McDonald's", "Consumer"),
    "JNJ":  ("Johnson & Johnson", "Healthcare"),
    "UNH":  ("UnitedHealth", "Healthcare"),
}

# ---------------- Dates ----------------
START_DATE = "2018-01-01"

# ---------------- Paths ----------------
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
CLEAN_FILE = f"{PROCESSED_DIR}/prices_clean.csv"

# ---------------- Database ----------------
# Set DATABASE_URL in a local .env file (see .env.example). Never hard-code
# credentials here.
DB_URL = os.environ["DATABASE_URL"]
