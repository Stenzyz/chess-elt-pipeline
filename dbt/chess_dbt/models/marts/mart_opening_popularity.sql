{{ config(materialized='table', schema='marts') }}

SELECT
    date_trunc('month', end_date) AS month,
    eco,
    COUNT(*) AS games_count,
    count(*)::numeric
        / sum(count(*)) OVER (PARTITION BY date_trunc('month', end_date)) AS share_of_month,
    count(*) FILTER (WHERE outcome = 'white')::numeric
        / NULLIF(count(*), 0) AS white_win_rate
FROM {{ ref('fct_games') }}
GROUP BY date_trunc('month', end_date), eco