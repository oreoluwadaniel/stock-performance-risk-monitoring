# Stock Performance, Risk & Forecast Monitoring

**A Python, SQL, and Power BI investment analytics pipeline that compares stock performance, measures portfolio risk, tests diversification, and evaluates whether forecasting adds value over a simple baseline.**

**Coverage:** 10 US large-cap stocks | 2018-01-02 to 2026-07-07  
**Data:** 21,380 daily price records  
**Stack:** Python, PostgreSQL, SQL, ARIMA, Power BI

---

## The business problem

A stock dashboard can tell you what prices did. It does not necessarily tell you whether a portfolio is taking too much risk, whether two holdings are giving you the same exposure, or whether a forecast model is actually better than a simple baseline.

This project answers four practical questions:

- Which holdings created the most value over the period?
- Where is downside risk concentrated?
- Which stocks move together and reduce diversification?
- Does ARIMA produce forecasts better than simply using the latest price?

The aim is not to produce a trading signal. It is to build a repeatable monitoring layer for performance, risk, concentration, and forecast quality.

---

## How it works

```text
Yahoo Finance
      ↓
Raw Price Data
      ↓
Validation + Feature Engineering
      ↓
PostgreSQL Star Schema
      ↓
Risk + Performance Analysis
      ↓
Walk-Forward Forecast Testing
      ↓
Power BI Monitoring
