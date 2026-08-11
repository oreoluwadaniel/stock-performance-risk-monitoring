"""
features.py  (STEP 4 of the pipeline, runs after transform.py)
Builds the feature table from the clean data. Every feature at time t
uses ONLY information available at time t (no lookahead bias).
Run from inside src/:  python features.py
"""

import pandas as pd
import numpy as np
from config import CLEAN_FILE, PROCESSED_DIR

FEATURES_FILE = f"{PROCESSED_DIR}/prices_features.csv"


def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    """Relative Strength Index. Ratio of average up-moves to average
    down-moves over the window, scaled 0-100."""
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = (-delta.clip(upper=0)).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def build_features() -> pd.DataFrame:
    df = pd.read_csv(CLEAN_FILE, parse_dates=["date"])
    df = df.sort_values(["ticker", "date"]).reset_index(drop=True)
    g = df.groupby("ticker")   # the leakage fence between tickers

    # --- Lagged returns (backward-looking by definition) ---
    for lag in [1, 5, 10]:
        df[f"return_lag_{lag}"] = g["daily_return"].shift(lag)

    # --- Trend: trailing moving averages (NEVER center=True) ---
    df["ma_10"] = g["adj_close"].transform(lambda s: s.rolling(10).mean())
    df["ma_30"] = g["adj_close"].transform(lambda s: s.rolling(30).mean())
    df["dist_ma30_pct"] = df["adj_close"] / df["ma_30"] - 1

    # --- Risk: rolling volatility, annualized ---
    df["vol_30"] = g["daily_return"].transform(
        lambda s: s.rolling(30).std() * np.sqrt(252))

    # --- Momentum: RSI 14 ---
    df["rsi_14"] = g["adj_close"].transform(rsi)

    # --- MACD: 12-day EMA minus 26-day EMA, plus 9-day signal line ---
    ema12 = g["adj_close"].transform(lambda s: s.ewm(span=12, adjust=False).mean())
    ema26 = g["adj_close"].transform(lambda s: s.ewm(span=26, adjust=False).mean())
    df["macd"] = ema12 - ema26
    df["macd_signal"] = df.groupby("ticker")["macd"].transform(
        lambda s: s.ewm(span=9, adjust=False).mean())

    # --- Bollinger position: 0 = lower band, 1 = upper band ---
    std20 = g["adj_close"].transform(lambda s: s.rolling(20).std())
    ma20 = g["adj_close"].transform(lambda s: s.rolling(20).mean())
    df["boll_pos"] = (df["adj_close"] - (ma20 - 2 * std20)) / (4 * std20)

    # --- Drawdown: distance from running peak ---
    df["running_peak"] = g["adj_close"].cummax()
    df["drawdown"] = df["adj_close"] / df["running_peak"] - 1

    # --- Calendar features ---
    df["month"] = df["date"].dt.month
    df["day_of_week"] = df["date"].dt.dayofweek

    # --- THE TARGET: tomorrow's return. shift(-1) looks FORWARD.
    # This is the ONLY forward-looking column, and it is the label,
    # never a feature. Last row per ticker is NaN, which is correct:
    # tomorrow has not happened yet.
    df["target_next_return"] = g["daily_return"].shift(-1)

    df.to_csv(FEATURES_FILE, index=False)
    print(f"Saved {len(df):,} rows, {df.shape[1]} columns -> {FEATURES_FILE}")
    return df


if __name__ == "__main__":
    build_features()