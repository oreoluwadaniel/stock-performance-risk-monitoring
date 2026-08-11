"""
run_pipeline.py
One command refreshes the entire project (a Milestone 1 success metric):
    extract -> transform (clean + validate) -> load to PostgreSQL

Run from the PROJECT ROOT:
    python src/run_pipeline.py
"""

import extract
import transform
import load_db


def main():
    print("=" * 60)
    print("STEP 1/3: EXTRACT")
    print("=" * 60)
    extract.extract_prices()

    print("=" * 60)
    print("STEP 2/3: TRANSFORM + VALIDATE")
    print("=" * 60)
    transform.run()

    print("=" * 60)
    print("STEP 3/3: LOAD TO POSTGRESQL")
    print("=" * 60)
    load_db.load_dim_ticker()
    load_db.load_fact_prices()

    print("=" * 60)
    print("Pipeline complete. Views in PostgreSQL are now fresh.")
    print("=" * 60)


if __name__ == "__main__":
    main()
