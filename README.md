# Stock Performance, Risk & Forecast Monitoring - Daniel Olatunji

A Python and SQL pipeline that pulls ten years of daily price history for ten large-cap US stocks, cleans and validates it, models it in PostgreSQL, calculates performance and risk indicators, and backtests an ARIMA forecast against a naive baseline. Power BI sits on top as the decision layer.

I'm a data analyst based in Lagos, Nigeria, working across Python, SQL, and Power BI. This one started as a simple "which stocks in my watchlist are doing well" question and turned into a proper test of whether a forecasting model actually earns its place in the dashboard, or whether it's just adding noise. The honest answer turned out to be more interesting than a clean success story.

**Contact:** oluwafikayore@gmail.com

---

## The business problem

A watchlist full of price charts looks informative and answers almost nothing. Three questions actually matter:

1. **Performance** - which of these ten stocks have created the most value, and over what period?
2. **Risk** - where is the drawdown and volatility concentrated, and which names move together closely enough that holding both isn't real diversification?
3. **Forward monitoring** - what range does a statistical model expect next, and is that model actually better than just assuming tomorrow looks like today?

This project treats the Power BI dashboard as the decision layer and the Python/SQL pipeline underneath it as the part that has to be right before anything gets displayed.

**Watchlist:** AAPL, MSFT (Technology) · JPM, V (Financials) · XOM, CVX (Energy) · PG, MCD (Consumer) · JNJ, UNH (Healthcare)
**Coverage:** 2018-01-02 to 2026-07-07 · **Grain:** one row per ticker per trading day

---

## What's in here

| Folder | Contents |
|---|---|
| [`src/`](src/) | Extract, transform, feature engineering, ARIMA forecast, walk-forward evaluation, database load, one-command pipeline runner |
| [`sql/`](sql/) | Star-schema DDL and analytical views |
| [`notebooks/`](notebooks/) | Profiling and exploratory analysis scripts |
| [`data/`](data/) | Raw extract and processed/feature files |
| [`dashboard/`](dashboard/) | The Power BI file, a custom dark theme, and the supporting charts below |
| [`docs/`](docs/) | Business case, methodology, data-quality audit, model evaluation, data dictionary |

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
Power BI executive dashboard
```

`dim_ticker` and `dim_date` are the two dimensions. `fact_daily_prices` grains at one ticker × one trading date. `fact_forecasts` grains at one ticker × one forecast date × one model × one run date, with a uniqueness constraint enforcing that grain.

---

## What the data actually says

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

AAPL and MSFT pulled well ahead of the rest of the watchlist over this period. That's a historical fact about this specific window, not a signal about what happens next.

### Risk and diversification

![Risk matrix: 30-day annualized volatility vs. maximum drawdown, colored by sector](dashboard/risk_matrix.png)

Maximum drawdown ranges from **-23.8% (PG)** to **-61.4% (UNH)**, and it doesn't sort cleanly by sector - XOM and CVX (Energy) sit near the bottom of the drawdown table, but so does UNH (Healthcare), while JNJ (also Healthcare) holds up much better. Sector alone doesn't explain drawdown depth here; the security itself matters just as much.

![Daily-return correlation matrix across the ten-stock watchlist](dashboard/correlation_heatmap.png)

The correlation matrix is where the concentration risk shows up. XOM and CVX move together at **0.843**, which is high enough that holding both isn't really two independent energy bets, it's one bet with extra steps. AAPL and MSFT sit at **0.669**, still meaningfully correlated. The lowest pairing in the set, PG and XOM at **0.204**, is what actual diversification looks like by comparison.

All ten names had their latest 30-day annualized volatility sitting above their own historical median as of the snapshot date. That's a monitoring signal worth flagging on the dashboard, not a prediction that volatility keeps climbing.

### Forecast evaluation

The pipeline fits ARIMA per ticker on log adjusted prices and forecasts 30 NYSE trading sessions out, then checks that forecast against reality across five walk-forward folds per ticker (50 evaluation runs total) and compares it to a naive last-value baseline.

| Metric | ARIMA | Naive |
|---|---:|---:|
| Average MAPE | 5.732% | 5.716% |
| Average RMSE | 17.665 | 17.591 |
| Average skill vs. naive | -0.33% | baseline |

ARIMA came out essentially tied with the naive model, and slightly behind on average. Per ticker it's a mixed bag: it beat naive on PG (+1.29%) and JNJ (+1.07%), and lost to it on MSFT (-2.40%) and MCD (-1.70%). That's not a result I'd want to hide behind a nicer-looking chart.

What that tells me is the model isn't earning its keep as a price predictor, but the forecast range and the backtest itself are still useful as a **monitoring layer** - a way to flag when the model's own error is drifting, and a reasonable statistical range to sanity-check against, rather than a trading signal.

---

## Corrections I made to my own analysis

An earlier pass at this project made three claims the data didn't actually support. Leaving them in would have been the easier path, so here's what I fixed instead:

**"Sector drove drawdown depth."** The first draft argued that sector exposure alone explained how deep each stock's drawdown went. It doesn't hold up - UNH and JNJ are both Healthcare, and their maximum drawdowns are 61.4% and 27.4% apart. Security-specific events matter as much as sector.

**"ARIMA beats the naive baseline."** The original write-up leaned on ARIMA's forecast as a differentiator. The walk-forward backtest says otherwise: -0.33% average skill versus naive, which is a tie at best. I rewrote the forecast section to say what the backtest actually shows instead of what I wanted it to show.

**Forward-filled prices.** The first version forward-filled missing OHLC values to keep the series continuous. For real market prices, that manufactures observations that never happened and distorts the high/low/close fields. The corrected pipeline leaves genuine market closures absent instead of inventing a price for them.

I'd rather publish the version that's right than the version that reads better.

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

No forward-filling of prices, no synthetic rows, no rows dropped just because a return looked extreme - a 25% single-day move is a real market event, not a data error, so it stays in.

Forecast horizon dates are generated against the **NYSE trading calendar**, not a generic Monday-to-Friday business-day calendar, which matters for anything that touches US market holidays.

---

## Reproducing this

```bash
pip install -r requirements.txt
# Create a local .env with DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/stock_analytics
psql -f sql/01_create_schema.sql
psql -f sql/02_populate_dim_date.sql
python src/run_pipeline.py   # extract -> transform/validate -> load
```

`run_pipeline.py` is a one-command refresh: it re-pulls prices from Yahoo Finance, re-validates and re-derives features, and reloads PostgreSQL. Nothing in `src/` reads a database password directly; `config.py` requires `DATABASE_URL` from the environment and fails loudly if it isn't set, instead of falling back to a default.

---

## Limitations

- Historical performance is not evidence of future performance.
- ARIMA's model intervals are statistical estimates, not guaranteed price ranges, and the backtest shows the model roughly ties a naive baseline.
- Five folds over a 30-session horizon is a reasonable first backtest, not a large one. A stronger version would add more folds, directional accuracy, interval coverage, and a couple of benchmark models like drift and exponential smoothing.
- MAPE isn't ideal for every financial series; it's reported alongside RMSE for that reason.
- Yahoo Finance is an external, free data source and should be refreshed before treating any of these numbers as current.
- This is an analytics and monitoring project, not a trading system, an automated strategy, or investment advice.

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

Analytical views (`sql/03_views.sql`) sit between the fact tables and Power BI: `vw_prices` for a flat, human-readable price fact, `vw_price_analytics` adding previous close, moving average, rolling volatility and running peak, and `vw_forecasts` joining forecast output to the ticker and calendar dimensions.

---

## Tools

Python (pandas, NumPy, statsmodels, yfinance, SQLAlchemy), PostgreSQL, Power BI, DAX, walk-forward time-series evaluation, dimensional modelling.

---

## About the Power BI file

`dashboard/dash.pbix` is the interactive executive dashboard - watchlist prioritization, risk review, concentration monitoring, and forecast/model-quality tracking in one place, built on `dark-executive.json`, a custom dark theme. It includes a third-party **HTML Content** custom visual; that visual's embedded author metadata (Daniel Marsh-Patrick / coacervo.co) belongs to the visual's developer, not to this project, and I've left it untouched since it's third-party software attribution rather than project authorship.

---

## About me

I'm Daniel Olatunji, a data analyst working across Python, SQL, Power BI, Excel, and Power Query, with a focus on data quality and building analytics people can actually trust. If you're hiring for a data analyst, BI developer, or analytics engineering role and want to talk through this build, including the three claims I had to walk back, reach me at **oluwafikayore@gmail.com**.

More of my work:
- [Everdale Retail Analytics](https://github.com/oreoluwadaniel/everdale-retail-analytics) - Excel/Power Query retail intelligence build, 194K order lines
- [Kavora CRM Migration & Data Governance](https://github.com/oreoluwadaniel/kavora-crm-migration-data-governance) - CRM data migration and governance case study
- [Data Analytics & ETL Portfolio](https://github.com/oreoluwadaniel/data-analytics-etl-portfolio) - four Excel/Power Query case studies across CRM, HR, inventory, and sales
