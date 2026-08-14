{{ config(materialized='table', schema='marts') }}

SELECT
    time_class,
    date_trunc('month', end_date) AS month,
    outcome,
    COUNT(*) AS games_count
FROM {{ ref('fct_games') }}
GROUP BY time_class, date_trunc('month', end_date), outcome