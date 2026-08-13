{{ config(materialized='table', schema='marts') }}

SELECT
    time_class,
    termination,
    count(*) AS games_count,
    count(*)::numeric / sum(count(*)) OVER (PARTITION BY time_class) AS share
FROM {{ ref('fct_games') }}
GROUP BY time_class, termination