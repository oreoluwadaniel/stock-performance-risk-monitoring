import pandas as pd
from sqlalchemy import create_engine, text

from config import DB_URL, SECTORS, CLEAN_FILE

engine = create_engine(DB_URL)


def load_dim_ticker() -> None:
    existing = pd.read_sql("SELECT COUNT(*) AS n FROM dim_ticker", engine)["n"][0]
    if existing > 0:
        print(f"dim_ticker already has {existing} rows, skipping.")
        return
    df = pd.DataFrame(
        [(t, name, sector) for t, (name, sector) in SECTORS.items()],
        columns=["ticker", "company_name", "sector"],
    )
    df.to_sql("dim_ticker", engine, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into dim_ticker.")


def load_fact_prices() -> None:
    df = pd.read_csv(CLEAN_FILE, parse_dates=["date"])

    # Attach surrogate keys. The fact table never sees the string 'AAPL'.
    keys = pd.read_sql("SELECT ticker_key, ticker FROM dim_ticker", engine)
    df = df.merge(keys, on="ticker", how="inner")
    df["date_key"] = df["date"].dt.strftime("%Y%m%d").astype(int)

    cols = ["date_key", "ticker_key", "open", "high", "low",
            "close", "adj_close", "volume", "daily_return"]

    # One transaction: if the insert fails, the truncate rolls back too.
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE fact_daily_prices"))
        df[cols].to_sql("fact_daily_prices", conn, if_exists="append",
                        index=False, method="multi", chunksize=5000)
        # Flag real trading days on the calendar
        conn.execute(text("""
            UPDATE dim_date d
               SET is_trading_day = TRUE
             WHERE EXISTS (SELECT 1 FROM fact_daily_prices f
                            WHERE f.date_key = d.date_key)
        """))

    print(f"Loaded {len(df):,} rows into fact_daily_prices "
          f"and updated is_trading_day flags.")


if __name__ == "__main__":
    load_dim_ticker()
    load_fact_prices()
