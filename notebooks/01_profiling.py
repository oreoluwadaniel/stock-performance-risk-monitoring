# %% [markdown]
# # 01 - Data Profiling (Milestone 5, Step 1)
# Profile the RAW data before deciding how to clean it.
# Run with "Run Cell" above each # %% marker (Jupyter extension),
# OR run the whole file: python notebooks/01_profiling.py
# Do NOT use the Code Runner extension on this file.

# %%
import glob
from pathlib import Path
import pandas as pd

pd.set_option("display.width", 120)

# Find the data/raw folder no matter where VS Code runs this from.
# Walks upward from the current working directory until it finds it.
def find_raw_dir() -> Path:
    for base in [Path.cwd(), *Path.cwd().parents]:
        candidate = base / "data" / "raw"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "Could not find data/raw. Open the stock-analytics folder in VS Code "
        "and make sure extract.py has been run."
    )

raw_dir = find_raw_dir()
files = sorted(glob.glob(str(raw_dir / "prices_raw_*.csv")))
if not files:
    raise FileNotFoundError(f"No prices_raw_*.csv in {raw_dir}. Run extract.py first.")

raw_path = files[-1]   # date-stamped names sort chronologically, last = latest
print("Profiling:", raw_path)

df = pd.read_csv(raw_path, parse_dates=["Date"])
print(df.head())

# %% Types and non-null counts
df.info()

# %% Nulls per column
print(df.isna().sum())

# %% Grain check: duplicates on (Date, Ticker) should be 0
print("Duplicate (Date, Ticker) rows:", df.duplicated(subset=["Date", "Ticker"]).sum())

# %% Suspicious rows: zero volume with a price
print("Zero-volume rows:", (df["Volume"] == 0).sum())

# %% Coverage per ticker: same row count and date range for all 10?
# If one ticker has fewer rows, investigate BEFORE cleaning.
print(df.groupby("Ticker")["Date"].agg(["min", "max", "count"]))

# %% Basic stats sanity check: any negative or zero prices?
print(df[["Open", "High", "Low", "Close", "Adj Close"]].describe())

# %% Spot-check the AAPL 4-for-1 split (Aug 31, 2020):
# Close and Adj Close diverge before the split date.
aapl = df[df["Ticker"] == "AAPL"]
print(aapl[(aapl["Date"] >= "2020-08-25") & (aapl["Date"] <= "2020-09-04")][
    ["Date", "Close", "Adj Close"]
])

# %% [markdown]
# ## Profiling conclusions (edit with YOUR findings)
# - Duplicates: ___
# - Nulls: ___ (which columns, which tickers, isolated or leading?)
# - Zero-volume rows: ___
# - Coverage: all 10 tickers aligned? ___
# These findings justify every decision coded in src/transform.py.