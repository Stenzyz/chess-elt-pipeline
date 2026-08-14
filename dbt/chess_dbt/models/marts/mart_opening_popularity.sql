{{ config(materialized='table', schema='marts') }}

SELECT
    date_trunc('month', fg.end_date) AS month,
    fg.eco,
    do_.opening_family,
    COUNT(*) AS games_count,
    COUNT(*) FILTER (WHERE fg.outcome = 'white') AS white_wins_count,
    COUNT(*) FILTER (WHERE fg.outcome = 'black') AS black_wins_count,
    COUNT(*) FILTER (WHERE fg.outcome = 'draw') AS draws_count
FROM {{ ref('fct_games') }} fg
JOIN {{ ref('dim_opening') }} do_ ON fg.eco = do_.eco
GROUP BY date_trunc('month', fg.end_date), fg.eco, do_.opening_family