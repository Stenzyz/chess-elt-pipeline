{{ config(materialized='table', schema='marts') }}

SELECT
    time_class,
    date_trunc('month', end_date) AS month,
    count(*) FILTER (WHERE outcome = 'white')::numeric / count(*) AS white_share,
    count(*) FILTER (WHERE outcome = 'black')::numeric / count(*) AS black_share,
    count(*) FILTER (WHERE outcome = 'draw')::numeric / count(*) AS draw_share
FROM {{ ref('fct_games') }}
GROUP BY time_class, date_trunc('month', end_date)