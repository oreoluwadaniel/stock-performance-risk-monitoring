"""
transform.py  (STEP 2 of the pipeline)
Cleans the latest raw file, computes log returns, validates, and writes
data/processed/prices_clean.csv.

Cleaning decisions (documented, with reasons):
- Duplicates on (date, ticker): dropped. Violates the fact table grain.
- Isolated null prices: forward-filled WITHIN each ticker. Finance
  convention: no trade means the price stands. Never interpolate.
- Leading nulls (nothing to fill from): rows dropped.
- Missing weekends/holidays: left alone. Markets were closed. Not missing data.
- Extreme returns (e.g. March 2020): KEPT. In finance, outliers are the story.

Run from the PROJECT ROOT:
    python src/transform.py
"""

import glob
import pandas as pd
import numpy as np
from pathlib import Path

from config import RAW_DIR, PROCESSED_DIR, CLEAN_FILE


def latest_raw_file() -> str:
    files = sorted(glob.glob(f"{RAW_DIR}/prices_raw_*.csv"))
    if not files:
        raise FileNotFoundError("No raw file found. Run extract.py first.")
    return files[-1]   # date-stamped names sort chronologically


def clean_prices(raw_path: str) -> pd.DataFrame:
    df = pd.read_csv(raw_path, parse_dates=["Date"])

    # snake_case column names: 'Adj Close' -> 'adj_close'
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]

    # 1. Duplicates (grain guard)
    before = len(df)
    df = df.drop_duplicates(subset=["date", "ticker"], keep="first")
    print(f"Duplicates dropped: {before - len(df)}")

    # 2. Sort BEFORE any fill/shift. Order is everything in time series.
    df = df.sort_values(["ticker", "date"]).reset_index(drop=True)

    # 3. Forward-fill prices WITHIN each ticker.
    #    groupby fences tickers off so AAPL never fills from another stock.
    price_cols = ["open", "high", "low", "close", "adj_close"]
    df[price_cols] = df.groupby("ticker")[price_cols].ffill()

    # 4. Drop leading nulls (nothing to fill from)
    df = df.dropna(subset=["adj_close"])

    # 5. Volume nulls -> 0, flag zero-volume rows (kept, they are information)
    df["volume"] = df["volume"].fillna(0).astype("int64")
    zero_vol = (df["volume"] == 0).sum()
    if zero_vol:
        print(f"Note: {zero_vol} zero-volume rows kept (flagged, not dropped)")

    # 6. Log returns per ticker: ln(P_t / P_{t-1}).
    #    shift(1) inside the groupby so day 1 of each ticker is NaN (correct).
    df["daily_return"] = (
        df.groupby("ticker")["adj_close"]
          .transform(lambda s: np.log(s / s.shift(1)))
    )

    return df


def validate(df: pd.DataFrame) -> None:
    """Hard gates. Pipeline crashes loudly if any assumption breaks."""
    assert df.duplicated(subset=["date", "ticker"]).sum() == 0, "dupes remain"
    assert df["adj_close"].isna().sum() == 0, "null prices remain"
    assert (df["adj_close"] <= 0).sum() == 0, "non-positive prices found"
    assert df["ticker"].nunique() == 10, "expected 10 tickers"
    r = df["daily_return"].dropna()
    assert r.abs().max() < 0.5, "a >50% daily return exists, investigate"
    print("All validation checks passed.")


def run() -> pd.DataFrame:
    raw = latest_raw_file()
    print(f"Cleaning: {raw}")
    df = clean_prices(raw)
    validate(df)
    Path(PROCESSED_DIR).mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_FILE, index=False)
    print(f"Saved {len(df):,} clean rows -> {CLEAN_FILE}")
    return df


if __name__ == "__main__":
    run()
