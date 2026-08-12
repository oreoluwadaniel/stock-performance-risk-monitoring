# Stock Performance, Risk & Forecast Monitoring - Daniel Olatunji

A Python and SQL pipeline that pulls ten years of daily prices for ten large-cap US stocks, checks the data, stores it in PostgreSQL, calculates performance and risk measures, and tests an ARIMA forecast against a simple baseline. Power BI is used for the final dashboard.

I'm a data analyst based in Lagos, Nigeria, working across Python, SQL, and Power BI. This started with a simple question: which stocks in my watchlist are doing well? It became a test of whether a forecasting model actually improves the analysis or just adds another chart. The backtest gave a more useful answer than a clean success story.

**Contact:** danolatunji25@gmail.com

---

## The business problem

A watchlist full of price charts can look useful without answering much. I wanted the analysis to answer three questions:

1. **Performance:** which stocks created the most value over the period?
2. **Risk:** where are volatility and drawdown concentrated, and which stocks move closely enough that holding both adds little diversification?
3. **Forecast monitoring:** does the statistical model do better than simply assuming the next value will be close to the current one?

The Power BI report is the final view. The Python and SQL work underneath it has to be right before the numbers reach the dashboard.

**Watchlist:** AAPL, MSFT (Technology) · JPM, V (Financials) · XOM, CVX (Energy) · PG, MCD (Consumer) · JNJ, UNH (Healthcare)
**Coverage:** 2018-01-02 to 2026-07-07 · **Grain:** one row per ticker per trading day

---

## What's in here

| Folder | Contents |
|---|---|
| [`src/`](src/) | Extraction, transformation, feature engineering, ARIMA forecast, walk-forward testing, database load, and pipeline runner |
| [`sql/`](sql/) | Star-schema DDL and analytical views |
| [`notebooks/`](notebooks/) | Profiling and exploratory analysis scripts |
| [`data/`](data/) | Raw and processed files |
| [`dashboard/`](dashboard/) | Power BI file, theme, and supporting charts |
| [`docs/`](docs/) | Business case, method, data-quality audit, model evaluation, and data dictionary |

---

## Architecture

```text
Yahoo Finance
     |
     v
Extract -> immutable raw CSV
     |
     v
Transform + validation
     |
     +--> Feature engineering (RSI, MACD, Bollinger, rolling volatility...)
     |
     +--> Walk-forward backtest (5 folds, 30-session horizon)
     |
     v
PostgreSQL star schema (dim_ticker, dim_date, fact_daily_prices, fact_forecasts)
     |
     v
Analytical SQL views
     |
     v
Power BI dashboard
```

`dim_ticker` and `dim_date` are the two dimensions. `fact_daily_prices` has one row per ticker and trading date. `fact_forecasts` has one row per ticker, forecast date, model, and run date, with a uniqueness constraint enforcing that grain.

---

## What the data says

### Performance

Cumulative adjusted-price growth over the full window, indexed to 100 at the start:

![Cumulative growth of 100 invested per ticker, 2018 to 2026](dashboard/Figure_1.png)

| Rank | Ticker | Cumulative return |
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

AAPL and MSFT were well ahead of the rest of this watchlist during this period. That describes the period tested. It does not say what happens next.

### Risk and diversification

![Risk matrix: 30-day annualized volatility vs. maximum drawdown, colored by sector](dashboard/risk_matrix.png)

Maximum drawdown ranges from **-23.8% (PG)** to **-61.4% (UNH)**. Sector does not explain all of the difference. XOM and CVX are both Energy, while JNJ and UNH are both Healthcare, but their drawdowns are very different.

![Daily-return correlation matrix across the ten-stock watchlist](dashboard/correlation_heatmap.png)

XOM and CVX have a **0.843** return correlation. Holding both does not give you two independent Energy positions. AAPL and MSFT are also fairly close at **0.669**. PG and XOM are the least correlated pair in this set at **0.204**.

All ten stocks had 30-day annualized volatility above their own historical median at the snapshot date. That is a monitoring signal, not a prediction that volatility will keep rising.

### Forecast evaluation

The pipeline fits ARIMA to log adjusted prices and forecasts 30 NYSE trading sessions ahead. I then test those forecasts across five walk-forward folds per ticker and compare them with a naive last-value baseline.

| Metric | ARIMA | Naive |
|---|---:|---:|
| Average MAPE | 5.732% | 5.716% |
| Average RMSE | 17.665 | 17.591 |
| Average skill vs. naive | -0.33% | baseline |

ARIMA was basically tied with the naive model and slightly worse on average. It did better on PG and JNJ and worse on MSFT and MCD. I kept that result in the README instead of presenting the forecast as a success.

The forecast is still useful as a monitoring layer. It gives the dashboard a model range to compare with the actual price and lets the analysis track when forecast error starts moving away from the backtest results. It is not a trading signal.

---

## Corrections I made to my own analysis

An earlier version made three claims the data did not support.

**"Sector drove drawdown depth."** It didn't. UNH and JNJ are both Healthcare, but their maximum drawdowns are very different. Company-specific events matter too.

**"ARIMA beats the naive baseline."** The walk-forward test does not support that. Average skill is -0.33%, which is effectively a tie and slightly worse for ARIMA.

**Forward-filled prices.** The first version filled missing OHLC values to keep the series continuous. That creates prices for days when the market did not report one. The corrected pipeline leaves genuine market closures absent.

I'd rather publish the version that is right than the version that reads better.

---

## Data quality

| Check | Result |
|---|---:|
| Price rows | 21,380 |
| Securities | 10 |
| Rows per ticker | 2,138 |
| Duplicate `(date, ticker)` rows | 0 |
| Missing raw fields | 0 |
| Non-positive adjusted prices | 0 |
| Maximum absolute daily log return | 25.33% |

There is no forward-filling of prices and no synthetic market rows. A 25% single-day move is not automatically a data error, so it stays in the data.

Forecast dates use the **NYSE trading calendar**, not a generic Monday-to-Friday calendar, so US market holidays are handled correctly.

---

## Reproducing this

```bash
pip install -r requirements.txt
# Create a local .env with DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/stock_analytics
psql -f sql/01_create_schema.sql
psql -f sql/02_populate_dim_date.sql
python src/run_pipeline.py   # extract -> transform/validate -> load
```

`run_pipeline.py` refreshes the prices, validates the data, recalculates the features, and reloads PostgreSQL. `config.py` reads `DATABASE_URL` from the environment and stops if it is missing.

---

## Limitations

- Historical performance is not evidence of future performance.
- ARIMA intervals are statistical estimates, not guaranteed price ranges. The backtest shows that the model roughly ties the naive baseline.
- Five folds over a 30-session horizon is a reasonable first test, not a large one. A stronger version would add more folds, directional accuracy, interval coverage, and other baseline models.
- MAPE is not ideal for every financial series, so RMSE is reported alongside it.
- Yahoo Finance is an external free data source and should be refreshed before treating these figures as current.
- This is an analytics and monitoring project, not a trading system or investment advice.

---

## Data model

```text
dim_date ───────┐
                ├── fact_daily_prices   (grain: ticker × trading date)
dim_ticker ─────┘

dim_date ───────┐
                ├── fact_forecasts      (grain: ticker × forecast date × model × run date)
dim_ticker ─────┘
```

Analytical views (`sql/03_views.sql`) sit between the fact tables and Power BI: `vw_prices` for the price fact, `vw_price_analytics` for previous close, moving averages, rolling volatility and running peak, and `vw_forecasts` for forecast output joined to ticker and calendar information.

---

## Tools

Python (pandas, NumPy, statsmodels, yfinance, SQLAlchemy), PostgreSQL, Power BI, DAX, walk-forward time-series testing, dimensional modelling.

---

## About the Power BI file

`dashboard/dash.pbix` is the interactive dashboard for watchlist review, risk, concentration, and forecast monitoring. It uses `dark-executive.json` as the theme and includes a third-party **HTML Content** custom visual. The visual's author metadata belongs to its developer, not to this project, so it has been left unchanged.

---

## About me

I'm Daniel Olatunji, a data analyst working across Python, SQL, Power BI, Excel, and Power Query, with a focus on data quality and reporting people can trust. If you're hiring for a data analyst, BI developer, or analytics engineering role and want to talk through this build, including the claims I had to walk back, reach me at **danolatunji25@gmail.com**.

More of my work:
- [Everdale Retail Analytics](https://github.com/oreoluwadaniel/everdale-retail-analytics)
- [Kavora CRM Migration & Data Governance](https://github.com/oreoluwadaniel/kavora-crm-migration-data-governance)
- [Data Analytics & ETL Portfolio](https://github.com/oreoluwadaniel/data-analytics-etl-portfolio)
