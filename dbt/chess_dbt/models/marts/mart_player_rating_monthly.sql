{{ config(materialized='table', schema='marts') }}

WITH month_end_snapshot AS (
    SELECT DISTINCT ON (username, time_class, date_trunc('month', snapshot_date))
        username,
        time_class,
        date_trunc('month', snapshot_date) AS month,
        AVG(rating) OVER w AS avg_rating_for_month,
        MAX(rating) OVER w AS max_rating_for_month,
        SUM(total_games) OVER w AS games_for_month,
        win,
        loss,
        draw
    FROM {{ ref('fct_player_rating_daily') }}
    WINDOW w AS (PARTITION BY username, time_class, date_trunc('month', snapshot_date))
    ORDER BY username, time_class, date_trunc('month', snapshot_date), snapshot_date DESC
)

SELECT
    username,
    time_class,
    month,
    avg_rating_for_month,
    max_rating_for_month,
    games_for_month,
    win - LAG(win) OVER w AS wins_this_month,
    loss - LAG(loss) OVER w AS losses_this_month,
    draw - LAG(draw) OVER w AS draws_this_month,
    (win - LAG(win) OVER w)::numeric
        / NULLIF(
            (win - LAG(win) OVER w) + (loss - LAG(loss) OVER w) + (draw - LAG(draw) OVER w),
            0
        ) AS win_rate_this_month
FROM month_end_snapshot
WINDOW w AS (PARTITION BY username, time_class ORDER BY month)