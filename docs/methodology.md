# Methodology

## Price series

Adjusted close is used for return and long-run performance analysis because it incorporates the vendor's historical treatment of distributions and corporate actions.

Raw OHLC values remain available for reference.

## Returns

Daily log return:

`ln(AdjustedClose_t / AdjustedClose_(t-1))`

Log returns are calculated independently within each ticker.

## Performance

The rebased performance index is:

`AdjustedClose_t / AdjustedClose_first × 100`

A final index of 675.55 means approximately +575.55% cumulative growth from the first observed adjusted price, not +675.55% return.

## Volatility

30-observation rolling standard deviation of daily log returns, annualized:

`rolling_std × sqrt(252)`

## Drawdown

`Price / RunningPeak - 1`

The minimum value over the supplied history is maximum drawdown.

## Correlation

Pearson correlation is calculated on **daily returns**, not raw prices. Correlating trending price levels would create misleadingly high relationships.

## Technical features

The feature table contains:

- lagged returns,
- 10/30-day moving averages,
- distance from 30-day moving average,
- 30-day annualized volatility,
- RSI-14,
- MACD and signal,
- Bollinger position,
- running peak,
- drawdown,
- calendar fields.

`target_next_return` is a label, not an input feature.

## Forecast model

ARIMA is fitted separately per ticker to log adjusted prices.

The model searches:

`p ∈ (0, 1, 2)`

`q ∈ (0, 1, 2)`

with `d = 1`, selecting the lowest AIC among converged specifications.

The forecast horizon is 30 **NYSE sessions**, not generic Monday-Friday business days.

## Evaluation

Five walk-forward cutoffs are used.

At each cutoff:

1. train only on historical data available at that cutoff,
2. select the ARIMA specification,
3. forecast 30 sessions,
4. compare with actual prices,
5. compare against a naive last-value baseline.

This prevents using future observations in model fitting.

## Interpretation

A model that fails to beat the naive baseline should not be presented as predictive edge. The supplied evaluation shows that the ARIMA model is essentially tied with and slightly worse than the naive baseline on average.

Therefore the forecast component is best framed as **scenario/range monitoring**, not a trading signal.
