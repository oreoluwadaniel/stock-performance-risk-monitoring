# Stock Watchlist Analytics — Insights Memo

**Snapshot:** 2026-07-07  
**Scope:** 10 US large-cap equities across five sectors  
**Data window:** 2018-01-02 to 2026-07-07

## 1. Executive summary

The watchlist produced very different long-run outcomes and materially different risk profiles.

Cumulative adjusted-price performance ranged from **+94.2% for CVX** to **+675.5% for AAPL** over the supplied period.

Maximum drawdown ranged from **-23.8% for PG** to **-61.4% for UNH**, showing that both sector exposure and security-specific events matter.

The strongest within-sector return relationships were **XOM-CVX at 0.843** and **AAPL-MSFT at 0.669**. Holding both XOM and CVX therefore creates substantial common energy exposure.

All 10 names had their latest 30-day annualized volatility above their own historical median in the supplied snapshot. This is a broad risk-monitoring signal, not a prediction of future returns.

The 30-session ARIMA forecast was evaluated against a naive last-value baseline. Average ARIMA MAPE was **5.732% versus 5.716% for the naive model**, with average skill of **-0.33%**. The correct conclusion is that the ARIMA model did not demonstrate consistent predictive superiority.

## 2. Performance

| Rank | Ticker | Cumulative adjusted-price return |
|---:|---|---:|
| 1 | AAPL | +675.5% |
| 2 | MSFT | +399.0% |
| 3 | JPM | +295.4% |
| 4 | V | +224.2% |
| 5 | JNJ | +141.3% |
| 6 | XOM | +140.6% |
| 7 | UNH | +122.0% |
| 8 | PG | +108.7% |
| 9 | MCD | +97.5% |
| 10 | CVX | +94.2% |

**Important:** these are cumulative returns calculated as final rebased index minus 100.

## 3. Risk

### Maximum drawdown

| Ticker | Maximum drawdown |
|---|---:|
| UNH | -61.4% |
| XOM | -61.0% |
| CVX | -55.8% |
| JPM | -43.6% |
| AAPL | -38.5% |
| MSFT | -37.1% |
| MCD | -36.9% |
| V | -36.4% |
| JNJ | -27.4% |
| PG | -23.8% |

The original claim that sector choice alone drove drawdown depth has been removed. The data shows meaningful security-level variation.

## 4. Diversification

Return correlations:

- XOM-CVX: **0.843**
- AAPL-MSFT: **0.669**
- JPM-V: **0.587**
- PG-XOM: **0.204**

The XOM/CVX pair behaves as a highly correlated energy exposure. Treating them as fully independent diversification would understate concentration.

## 5. Volatility

Latest 30-day annualized volatility is above each security's own historical median for **10 of 10 securities**.

This suggests the snapshot sits in a relatively elevated volatility regime across the watchlist.

That statement is descriptive; it does not predict whether volatility will rise or fall next.

## 6. Forecast evaluation

Five walk-forward folds per ticker were evaluated over a 30-session horizon.

| Metric | ARIMA | Naive |
|---|---:|---:|
| Average MAPE | 5.732% | 5.716% |
| Average RMSE | 17.665 | 17.591 |
| Average skill | -0.33% | 0% |

The model therefore should not be marketed as a proven forecasting advantage.

The stronger business use is:

**forecast range + risk monitoring + model-quality monitoring.**

## 7. Business recommendations

1. **Monitor XOM/CVX as a concentration pair.** Their 0.843 return correlation creates substantial shared exposure.
2. **Use per-security volatility thresholds.** A single global threshold would ignore different historical volatility regimes.
3. **Prioritize drawdown monitoring for UNH, XOM and CVX.** Their historical maximum drawdowns were the deepest in this watchlist.
4. **Do not overstate ARIMA.** The supplied evaluation does not show consistent superiority over a naive baseline.
5. **Use the dashboard as a monitoring system.** The decision value comes from combining performance, risk, concentration and forecast diagnostics.
