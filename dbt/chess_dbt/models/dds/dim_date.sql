{{ config(materialized='table', schema='dds') }}

SELECT 
    date_day::date as date_day,
    EXTRACT(year FROM date_day)::integer as year,
    EXTRACT(month FROM date_day)::integer as month,
    trim(TO_CHAR(date_day, 'Month')) as month_name,
    EXTRACT(dow FROM date_day)::integer AS day_of_week,
    trim(TO_CHAR(date_day, 'Day')) AS day_name,
    CASE
        WHEN (EXTRACT(dow FROM date_day) IN (0, 6)) THEN true
        ELSE false
    END AS is_weekend
FROM generate_series('2024-01-01'::date, '2026-12-31'::date, interval '1 day') AS date_day
