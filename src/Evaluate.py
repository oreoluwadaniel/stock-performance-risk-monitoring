import warnings
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

from config import CLEAN_FILE, PROCESSED_DIR
from forecast import best_arima          # reuse the same model selection

warnings.filterwarnings("ignore")

HORIZON = 30
N_FOLDS = 5
RESULTS_FILE = f"{PROCESSED_DIR}/backtest_results.csv"


def metrics(actual: np.ndarray, pred: np.ndarray) -> dict:
    err = actual - pred
    return {
        "mae":  np.mean(np.abs(err)),
        "rmse": np.sqrt(np.mean(err ** 2)),
        "mape": np.mean(np.abs(err / actual)) * 100,
    }


def backtest_ticker(ticker: str, series: pd.Series) -> pd.DataFrame:
    n = len(series)
    # 5 cutoffs spread across the final 2 years of history
    cutoffs = [n - HORIZON - i * 100 for i in range(N_FOLDS)]
    rows = []
    for cut in cutoffs:
        train = series.iloc[:cut]
        actual = series.iloc[cut:cut + HORIZON].values

        # Model forecast
        fit, order = best_arima(np.log(train))
        pred = np.exp(fit.forecast(steps=HORIZON)).values

        # Naive baseline: last known price, carried flat
        naive = np.full(HORIZON, train.iloc[-1])

        m_model = metrics(actual, pred)
        m_naive = metrics(actual, naive)
        rows.append({
            "ticker": ticker,
            "cutoff_date": series.index[cut - 1].date(),
            "order": str(order),
            "model_rmse": m_model["rmse"],
            "naive_rmse": m_naive["rmse"],
            "model_mape": m_model["mape"],
            "naive_mape": m_naive["mape"],
            "skill_vs_naive": 1 - m_model["rmse"] / m_naive["rmse"],
        })
    return pd.DataFrame(rows)


def run():
    df = pd.read_csv(CLEAN_FILE, parse_dates=["date"])
    results = []
    for ticker, sub in df.groupby("ticker"):
        series = sub.set_index("date")["adj_close"].asfreq("B").ffill()
        print(f"Backtesting {ticker}...")
        results.append(backtest_ticker(ticker, series))
    out = pd.concat(results, ignore_index=True)
    out.to_csv(RESULTS_FILE, index=False)

    summary = (out.groupby("ticker")
                  [["model_rmse", "naive_rmse", "model_mape", "skill_vs_naive"]]
                  .mean().round(3)
                  .sort_values("skill_vs_naive", ascending=False))
    print("\n=== Average across folds ===")
    print(summary)
    print(f"\nSaved fold-level results -> {RESULTS_FILE}")


if __name__ == "__main__":
    run()
