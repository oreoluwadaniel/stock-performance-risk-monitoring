-- ============================================================
-- 03_views.sql
-- Run THIRD (any time after 01). Power BI connects to VIEWS, never raw tables.
-- The view is the contract between the database and the dashboard.
-- ============================================================

-- Flat, human-readable price view
CREATE OR REPLACE VIEW vw_prices AS
SELECT
    d.full_date, d.year, d.month_name, d.quarter,
    t.ticker, t.company_name, t.sector,
    f.open, f.high, f.low, f.close, f.adj_close,
    f.volume, f.daily_return
FROM fact_daily_prices f
JOIN dim_date   d ON d.date_key   = f.date_key
JOIN dim_ticker t ON t.ticker_key = f.ticker_key;


-- Window function analytics: per-ticker time series calculations
CREATE OR REPLACE VIEW vw_price_analytics AS
SELECT
    d.full_date,
    t.ticker,
    t.sector,
    f.adj_close,
    f.daily_return,

    -- previous day's price (per ticker, in date order)
    LAG(f.adj_close) OVER w                                        AS prev_close,

    -- 30-observation moving average
    AVG(f.adj_close)     OVER (w ROWS BETWEEN 29 PRECEDING
                                 AND CURRENT ROW)                  AS ma_30,

    -- 30-observation rolling volatility (std dev of returns)
    STDDEV(f.daily_return) OVER (w ROWS BETWEEN 29 PRECEDING
                                 AND CURRENT ROW)                  AS vol_30,

    -- running peak, for drawdown = adj_close / running_peak - 1
    MAX(f.adj_close)     OVER (w ROWS BETWEEN UNBOUNDED PRECEDING
                                 AND CURRENT ROW)                  AS running_peak
FROM fact_daily_prices f
JOIN dim_date   d ON d.date_key   = f.date_key
JOIN dim_ticker t ON t.ticker_key = f.ticker_key
WINDOW w AS (PARTITION BY t.ticker ORDER BY d.full_date);


-- Forecast view for the dashboard (fills in Milestone 8)
CREATE OR REPLACE VIEW vw_forecasts AS
SELECT
    d.full_date,
    t.ticker,
    fc.model_name,
    fc.forecast_value,
    fc.lower_bound,
    fc.upper_bound,
    fc.run_date
FROM fact_forecasts fc
JOIN dim_date   d ON d.date_key   = fc.date_key
JOIN dim_ticker t ON t.ticker_key = fc.ticker_key;
