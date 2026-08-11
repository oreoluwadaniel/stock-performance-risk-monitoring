# Model Evaluation

## Supplied backtest

The supplied `backtest_results.csv` contains:

- 10 securities
- 5 historical folds per security
- 30-session forecast horizon
- 50 evaluation rows

## Average performance

| Metric | ARIMA | Naive |
|---|---:|---:|
| MAPE | 5.732% | 5.716% |
| RMSE | 17.665 | 17.591 |
| Skill vs naive | -0.328% | baseline |

The negative average skill means ARIMA did **not** beat the naive baseline on average.

## Per-security skill

| Ticker | Average skill vs naive |
|---|---:|
| PG | +1.29% |
| JNJ | +1.07% |
| JPM | +0.37% |
| AAPL | -0.01% |
| XOM | ~0.00% |
| V | -0.06% |
| CVX | -0.69% |
| UNH | -1.16% |
| MCD | -1.70% |
| MSFT | -2.40% |

The result is mixed rather than universally positive.

## Correct portfolio interpretation

The evidence supports:

> "The ARIMA model is a reasonable monitoring benchmark, but the supplied backtest does not demonstrate consistent predictive superiority over a naive baseline."

It does **not** support:

> "The model predicts stock prices accurately."

or:

> "The model provides trading alpha."

## Recommended next validation step

For a stronger forecasting claim, add:

- more rolling folds,
- a longer untouched test period,
- directional accuracy,
- forecast interval coverage,
- benchmark models such as drift and exponential smoothing,
- evaluation of returns as well as price levels,
- a clearly specified economic/trading objective if a strategy is ever introduced.
