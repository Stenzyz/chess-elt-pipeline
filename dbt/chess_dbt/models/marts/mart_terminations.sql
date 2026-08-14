{{ config(materialized='table', schema='marts') }}

SELECT
    time_class,
    termination,
    count(*) AS games_count
FROM {{ ref('fct_games') }}
GROUP BY time_class, termination