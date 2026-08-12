# Risk Monitoring Architecture

```text
Market data
    |
    v
Python ingestion and cleaning
    |
    +--> trading-calendar checks
    +--> missing-data checks
    +--> return calculations
    |
    v
PostgreSQL analytical tables
    |
    +--> returns
    +--> volatility
    +--> drawdown
    +--> VaR inputs
    |
    v
Risk and forecast analysis
    |
    +--> naive baseline
    +--> ARIMA
    +--> walk-forward evaluation
    |
    v
Power BI monitoring
```

## Model rule

Forecast performance is judged against the naive baseline. The repository records that ARIMA did not materially improve on that baseline rather than presenting the model as successful by default.

## Data rule

Market prices are not forward-filled across non-trading periods. Trading-calendar logic is used to keep the time series aligned with actual market observations.
