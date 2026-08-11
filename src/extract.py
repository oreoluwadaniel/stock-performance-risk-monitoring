"""
extract.py  (STEP 1 of the pipeline)
Pulls full OHLCV history for all tickers from Yahoo Finance and saves an
immutable, date-stamped raw CSV in data/raw/.

Full re-pull every run (not incremental) because Adjusted Close is
retroactive: dividends and splits change historical values.

Run from the PROJECT ROOT:
    python src/extract.py
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
from pathlib import Path

from config import TICKERS, START_DATE, RAW_DIR


def extract_prices() -> pd.DataFrame:
    print(f"Downloading {len(TICKERS)} tickers from {START_DATE}...")

    df = yf.download(
        tickers=TICKERS,
        start=START_DATE,
        auto_adjust=False,   # keep BOTH Close and Adj Close
        group_by="ticker",   # columns come back as (Ticker, Field)
        threads=True,
    )

    # Reshape WIDE MultiIndex columns -> LONG format:
    # one row per (Date, Ticker), columns = Open/High/Low/Close/Adj Close/Volume
    try:
        long_df = df.stack(level=0, future_stack=True)   # pandas >= 2.1
    except TypeError:
        long_df = df.stack(level=0)                      # older pandas

    long_df = long_df.rename_axis(["Date", "Ticker"]).reset_index()

    # Drop rows where every price is missing (non-trading artefacts)
    price_cols = ["Open", "High", "Low", "Close", "Adj Close"]
    long_df = long_df.dropna(subset=price_cols, how="all")

    # Save date-stamped raw file (cheap versioning)
    Path(RAW_DIR).mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d")
    out_path = f"{RAW_DIR}/prices_raw_{stamp}.csv"
    long_df.to_csv(out_path, index=False)

    print(f"Saved {len(long_df):,} rows "
          f"({long_df['Ticker'].nunique()} tickers) -> {out_path}")
    return long_df


if __name__ == "__main__":
    extract_prices()
