{{ config(materialized='table', schema='dds') }}

WITH all_players AS (
    SELECT white_username AS username FROM {{ ref('fct_games') }}
    UNION
    SELECT black_username FROM {{ ref('fct_games') }}
    UNION
    SELECT username FROM {{ ref('fct_player_rating_daily') }}
)

SELECT
    all_players.username,
    profiles.title,
    profiles.location,
    profiles.status
FROM all_players
LEFT JOIN {{ ref('snap_player_profiles') }} AS profiles
    ON all_players.username = profiles.username
    AND profiles.dbt_valid_to IS NULL