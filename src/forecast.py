"""
STEP 5 of the pipeline
Fits ARIMA per ticker on log adjusted close, selects (p,q) by AIC,
forecasts 30 trading days with 95% intervals, and writes results
into fact_forecasts in PostgreSQL.
Run from inside src/:  python forecast.py
"""

import warnings
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from statsmodels.tsa.arima.model import ARIMA

from config import DB_URL, CLEAN_FILE

warnings.filterwarnings("ignore")   # statsmodels is chatty during grid search

HORIZON = 30          # trading days ahead
MODEL_NAME = "ARIMA"
engine = create_engine(DB_URL)


def best_arima(log_prices: pd.Series):
    """Grid search p,q in 0..2 with d=1 (justified by ADF). Lowest AIC wins."""
    best_aic, best_fit, best_order = np.inf, None, None
    for p in range(3):
        for q in range(3):
            try:
                fit = ARIMA(log_prices, order=(p, 1, q)).fit()
                if fit.aic < best_aic:
                    best_aic, best_fit, best_order = fit.aic, fit, (p, 1, q)
            except Exception:
                continue   # some combos fail to converge; skip them
    return best_fit, best_order


def forecast_ticker(ticker: str, series: pd.Series) -> pd.DataFrame:
    log_p = np.log(series)
    fit, order = best_arima(log_p)

    fc = fit.get_forecast(steps=HORIZON)
    mean = np.exp(fc.predicted_mean)            # back to price space
    ci = np.exp(fc.conf_int(alpha=0.05))        # 95% interval

    # Future TRADING dates: business days after the last observed date
    last_date = series.index[-1]
    future_dates = pd.bdate_range(start=last_date + pd.Timedelta(days=1),
                                  periods=HORIZON)

    print(f"{ticker}: ARIMA{order}, AIC={fit.aic:.1f}")
    return pd.DataFrame({
        "date": future_dates,
        "ticker": ticker,
        "forecast_value": mean.values,
        "lower_bound": ci.iloc[:, 0].values,
        "upper_bound": ci.iloc[:, 1].values,
    })


def run():
    df = pd.read_csv(CLEAN_FILE, parse_dates=["date"])
    results = []
    for ticker, sub in df.groupby("ticker"):
        series = sub.set_index("date")["adj_close"].asfreq("B").ffill()
        results.append(forecast_ticker(ticker, series))
    out = pd.concat(results, ignore_index=True)

    # Attach surrogate keys, exactly like load_db.py
    keys = pd.read_sql("SELECT ticker_key, ticker FROM dim_ticker", engine)
    out = out.merge(keys, on="ticker")
    out["date_key"] = out["date"].dt.strftime("%Y%m%d").astype(int)
    out["model_name"] = MODEL_NAME
    out["run_date"] = pd.Timestamp.today().date()

    cols = ["date_key", "ticker_key", "model_name",
            "forecast_value", "lower_bound", "upper_bound", "run_date"]
    with engine.begin() as conn:
        # Replace previous forecasts from this model (idempotent reruns)
        conn.execute(text("DELETE FROM fact_forecasts WHERE model_name = :m"),
                     {"m": MODEL_NAME})
        out[cols].to_sql("fact_forecasts", conn, if_exists="append",
                         index=False, method="multi")
    print(f"Wrote {len(out)} forecast rows to fact_forecasts.")


if __name__ == "__main__":
    run()
