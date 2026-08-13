

INSERT INTO dim_date (date_key, full_date, year, quarter, month,
                      month_name, day_of_week, is_month_end)
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INT,                          -- smart key
    d::DATE,
    EXTRACT(YEAR    FROM d)::INT,
    EXTRACT(QUARTER FROM d)::INT,
    EXTRACT(MONTH   FROM d)::INT,
    TRIM(TO_CHAR(d, 'Month')),
    TRIM(TO_CHAR(d, 'Day')),
    -- month-end test: first of month + 1 month - 1 day = last day of month
    d::DATE = (DATE_TRUNC('month', d) + INTERVAL '1 month - 1 day')::DATE
FROM GENERATE_SERIES('2018-01-01'::DATE,
                     '2027-12-31'::DATE,
                     '1 day') AS d;

SELECT COUNT(*) AS calendar_rows FROM dim_date;
