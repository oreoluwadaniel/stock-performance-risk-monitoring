# Data Dictionary

## Dimensions

### dim_ticker
One row per security.

- `ticker_key`: surrogate key
- `ticker`: security symbol
- `company_name`: company name
- `sector`: sector grouping
- `industry`: industry grouping

### dim_date
One row per calendar date.

- `date_key`
- `full_date`
- `year`
- `quarter`
- `month`
- `month_name`
- `day_of_week`
- `is_trading_day`
- `is_month_end`

## Facts

### fact_daily_prices

**Grain:** one ticker × one trading date.

Measures/fields:

- open
- high
- low
- close
- adjusted close
- volume
- daily log return

### fact_forecasts

**Grain:** one ticker × one forecast date × one model × one run date.

Fields:

- forecast value
- lower bound
- upper bound
- model name
- run date

## Analytical views

### vw_prices
Human-readable flat price fact joined to dimensions.

### vw_price_analytics
Adds:

- previous close
- 30-observation moving average
- rolling volatility
- running peak

### vw_forecasts
Joins forecast output to security and calendar dimensions.
