-- ============================================================
-- 01_create_schema.sql
-- Run FIRST, once, in pgAdmin Query Tool on database: stock_analytics
-- Star schema: 2 dimensions, 2 fact tables.
-- ============================================================

CREATE TABLE dim_ticker (
    ticker_key     SERIAL PRIMARY KEY,          -- surrogate key, auto-increment
    ticker         VARCHAR(10) NOT NULL UNIQUE,
    company_name   VARCHAR(100),
    sector         VARCHAR(50),
    industry       VARCHAR(80)
);

CREATE TABLE dim_date (
    date_key       INT PRIMARY KEY,             -- smart key, e.g. 20200831
    full_date      DATE NOT NULL UNIQUE,
    year           INT NOT NULL,
    quarter        INT NOT NULL,
    month          INT NOT NULL,
    month_name     VARCHAR(10) NOT NULL,
    day_of_week    VARCHAR(10) NOT NULL,
    is_trading_day BOOLEAN DEFAULT FALSE,
    is_month_end   BOOLEAN DEFAULT FALSE
);

-- Grain: one row = one ticker on one trading date.
-- Composite PK enforces the grain physically.
CREATE TABLE fact_daily_prices (
    date_key     INT NOT NULL REFERENCES dim_date(date_key),
    ticker_key   INT NOT NULL REFERENCES dim_ticker(ticker_key),
    open         NUMERIC(12,4),
    high         NUMERIC(12,4),
    low          NUMERIC(12,4),
    close        NUMERIC(12,4),
    adj_close    NUMERIC(12,4),                 -- returns come from THIS column
    volume       BIGINT,
    daily_return NUMERIC(10,6),                 -- log return
    PRIMARY KEY (date_key, ticker_key)
);

-- Separate fact table: forecasts have a different grain
-- (future dates exist, regenerated every model run).
CREATE TABLE fact_forecasts (
    forecast_id    SERIAL PRIMARY KEY,
    date_key       INT NOT NULL REFERENCES dim_date(date_key),
    ticker_key     INT NOT NULL REFERENCES dim_ticker(ticker_key),
    model_name     VARCHAR(50) NOT NULL,
    forecast_value NUMERIC(12,4),
    lower_bound    NUMERIC(12,4),
    upper_bound    NUMERIC(12,4),
    run_date       DATE NOT NULL
);
