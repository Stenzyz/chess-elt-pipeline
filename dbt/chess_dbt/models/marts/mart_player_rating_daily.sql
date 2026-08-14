{{ config(materialized='table', schema='marts') }}

SELECT
    f.username,
    f.time_class,
    f.snapshot_date,

    p.title,
    p.country,
    p.status,

    f.rating,
    f.win,
    f.loss,
    f.draw

FROM {{ ref('fct_player_rating_daily') }} f
LEFT JOIN {{ ref('dim_player') }} p
    ON f.username = p.username