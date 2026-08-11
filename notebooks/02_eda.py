# %% [markdown]
# # 02 - EDA and Time Series Analysis (Milestone 6)
# Run with "Run Cell" above each # %% marker (Jupyter extension),
# OR run the whole file: python notebooks/02_eda.py
# Do NOT use the Code Runner extension on this file.
# Requires: pip install matplotlib seaborn statsmodels

# %%
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

pd.set_option("display.width", 120)

# Find the processed file no matter where VS Code runs this from.
def find_processed() -> Path:
    for base in [Path.cwd(), *Path.cwd().parents]:
        candidate = base / "data" / "processed" / "prices_clean.csv"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        "prices_clean.csv not found. Run transform.py first, and open the "
        "stock-analytics folder in VS Code."
    )

clean_path = find_processed()
print("Loading:", clean_path)
df = pd.read_csv(clean_path, parse_dates=["date"])

# Long -> wide reshape for analysis math
prices  = df.pivot(index="date", columns="ticker", values="adj_close")
returns = df.pivot(index="date", columns="ticker", values="daily_return")
print(prices.tail())

# %% [markdown]
# ## 6.1 Rebased prices: growth of 100 invested
# Raw prices are not comparable (UNH ~$500 flattens PG ~$150).
# Rebasing to 100 shows pure relative performance.

# %%
rebased = prices / prices.iloc[0] * 100
rebased.plot(figsize=(12, 6), title="Growth of 100 invested (2018 = 100)")
plt.ylabel("Index (start = 100)")
plt.show()

# %% [markdown]
# ## 6.2 Return distributions: fat tails
# Excess kurtosis of 0 = normal bell curve. Stocks show 5 to 15+,
# meaning extreme days happen far more often than a bell curve predicts.

# %%
returns["AAPL"].hist(bins=100, figsize=(10, 5))
plt.title("AAPL daily log returns")
plt.show()

print("Excess kurtosis per ticker:")
print(returns.kurtosis().sort_values(ascending=False))

# %% [markdown]
# ## 6.3 Decomposition: trend + seasonality + residual
# period=252 (one trading year), multiplicative because swings scale
# with price level. EXPECT weak/noisy seasonality. That IS the finding:
# stocks trend, they do not have reliable calendar seasonality.

# %%
from statsmodels.tsa.seasonal import seasonal_decompose

aapl = prices["AAPL"].dropna()
decomp = seasonal_decompose(aapl, model="multiplicative", period=252)
fig = decomp.plot()
fig.set_size_inches(12, 8)
plt.show()

# %% [markdown]
# ## 6.4 Stationarity: the ADF test
# Null hypothesis: series is NON-stationary. Small p = stationary.
# Prices should FAIL (p ~ 0.9), returns should PASS (p ~ 0.0000).
# This proves d=1 for ARIMA and justifies modeling returns.

# %%
from statsmodels.tsa.stattools import adfuller

p_price  = adfuller(prices["AAPL"].dropna())[1]
p_return = adfuller(returns["AAPL"].dropna())[1]

verdict_price  = "non-stationary" if p_price  > 0.05 else "stationary"
verdict_return = "stationary"     if p_return < 0.05 else "non-stationary"
print(f"AAPL price  ADF p-value: {p_price:.4f}   -> {verdict_price}")
print(f"AAPL return ADF p-value: {p_return:.6f} -> {verdict_return}")

# %% Run ADF across ALL tickers (senior habit: test everything, not one example)
adf_summary = pd.DataFrame({
    "price_p":  {t: adfuller(prices[t].dropna())[1]  for t in prices.columns},
    "return_p": {t: adfuller(returns[t].dropna())[1] for t in returns.columns},
}).round(4)
print(adf_summary)

# %% [markdown]
# ## 6.5 Rolling volatility: the risk lens
# Daily std * sqrt(252) annualizes. Look for: March 2020 spike everywhere,
# PG structurally calmest, energy hot in 2020 and 2022,
# calm/turbulent periods clustering together (volatility clustering).

# %%
vol30 = returns.rolling(30).std() * np.sqrt(252)
vol30[["AAPL", "XOM", "PG", "JPM"]].plot(
    figsize=(12, 5), title="30-day annualized volatility")
plt.ylabel("Annualized volatility")
plt.show()

# %% [markdown]
# ## 6.6 Correlation of RETURNS (never prices: trending prices fake ~0.9)
# Expect: AAPL-MSFT high, XOM-CVX very high (~0.85, same oil price),
# defensives (PG, JNJ) lowest vs tech. Answers Business Question 3.

# %%
plt.figure(figsize=(10, 8))
sns.heatmap(returns.corr(), annot=True, fmt=".2f",
            cmap="RdYlGn_r", center=0.5, vmin=0, vmax=1)
plt.title("Correlation of daily returns")
plt.show()

# %% [markdown]
# ## 6.7 Drawdown: how bad did it get?
# drawdown = price / running_peak - 1. Cross-check against the SQL view
# vw_price_analytics (running_peak column). Same logic, two tools.

# %%
running_peak = prices.cummax()
drawdown = prices / running_peak - 1

print("Maximum drawdown per ticker:")
print((drawdown.min() * 100).round(1).sort_values().astype(str) + "%")

drawdown["XOM"].plot(figsize=(12, 4), title="XOM drawdown from peak")
plt.ylabel("Drawdown")
plt.show()

# %% [markdown]
# ## EDA Conclusions Memo (edit with YOUR numbers, one line each)
# 1. Prices are non-stationary (ADF p = ___); returns are stationary
#    (ADF p = ___). We model returns / difference once (d = 1).
# 2. Seasonality is negligible: no seasonal model component needed.
# 3. Returns have fat tails (kurtosis = ___): naive models understate risk.
# 4. Volatility clusters: risk monitoring matters as much as forecasting.
# 5. Correlations follow sectors (XOM-CVX = ___): holding both is weak
#    diversification. Genuine portfolio recommendation.
#
# Every model choice in Milestone 8 cites one of these five lines.