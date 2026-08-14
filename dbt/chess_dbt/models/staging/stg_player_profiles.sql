{{ config(materialized='view') }}

SELECT
    username,
    split_part(payload ->> 'country', '/country/', 2) AS country,
    payload ->> 'status' AS status,
    payload ->> 'title' AS title,
    loaded_at
FROM {{ source('raw', 'player_profiles_raw') }}