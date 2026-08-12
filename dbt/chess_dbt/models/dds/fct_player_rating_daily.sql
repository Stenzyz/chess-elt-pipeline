{{ config(materialized='table', schema='dds') }}

SELECT
    username,
    time_class,
    snapshot_date,
    rating,
    rating - LAG(rating) OVER (
        PARTITION BY username, time_class ORDER BY snapshot_date
    ) AS rating_change,
    win,
    loss,
    draw,
    (win + loss + draw) AS total_games,
    (win + loss + draw) - LAG(win + loss + draw) OVER (
        PARTITION BY username, time_class ORDER BY snapshot_date
    ) AS games_since_prev_snapshot,
    last_game_date,
    (last_game_date::date = snapshot_date) AS played_today
FROM {{ ref('stg_player_stats') }}