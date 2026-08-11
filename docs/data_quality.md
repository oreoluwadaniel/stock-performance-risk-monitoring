# Data Quality Audit

## Supplied snapshot

- Rows: **21,380**
- Securities: **10**
- Date range: **2018-01-02 to 2026-07-07**
- Rows per ticker: **2,138**

## Validation results

| Check | Result |
|---|---:|
| Duplicate `(date, ticker)` rows | 0 |
| Missing raw fields | 0 |
| Non-positive adjusted prices | 0 |
| Tickers present | 10 |
| Maximum absolute daily log return | 25.33% |
| Zero-volume rows in processed file | 0 |

## Cleaning policy

The original project said isolated null prices were forward-filled.

That rule has been corrected.

For market OHLC data, forward-filling an actual price can manufacture observations and distort the high/low/open/close fields. The corrected pipeline therefore:

- keeps the raw extract immutable,
- removes duplicate fact-grain rows,
- excludes rows with missing essential price fields from the analytical fact,
- leaves weekends and exchange holidays absent,
- retains genuine extreme market returns.

## Important interpretation correction

The original insights memo contained language such as:

> "sector choice, not stock-picking within a sector, drove loss depth."

That is too strong for the supplied evidence.

The actual maximum drawdowns range from **-23.8% for PG** to **-61.4% for UNH**. This shows that both sector exposure and security-specific behaviour matter.

## Forecast dates

The original forecast code used generic business days.

That has been corrected to use the **NYSE trading calendar**, because US market holidays are not equivalent to a Monday-Friday business-day calendar.

## Security

The original configuration contained a hard-coded PostgreSQL password placeholder.

That has been removed. Database credentials now come from `DATABASE_URL`.

## Third-party visual metadata

The PBIX contains the author metadata of the third-party HTML Content custom visual:

**Daniel Marsh-Patrick / coacervo.co**

This is not the project author's information and should not be removed. It is software attribution embedded in the visual package.
