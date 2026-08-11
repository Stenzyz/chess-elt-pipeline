{{ config(materialized='table', schema='dds') }}

SELECT
    time_class,
    MIN(base_time) AS min_base_time,
    MAX(base_time) AS max_base_time,
    ROUND(AVG(base_time)) AS avg_base_time,
    CASE
        WHEN time_class = 'bullet' THEN 'Bullet (до 3 мин)'
        WHEN time_class = 'blitz' THEN 'Blitz (3-10 мин)'
        WHEN time_class = 'rapid' THEN 'Rapid (10-60 мин)'
    END AS label
FROM {{ ref('stg_games') }}
GROUP BY time_class