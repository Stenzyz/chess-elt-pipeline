{{ config(materialized='view') }}

SELECT
    username,
    payload ->> 'location' AS location,
    payload ->> 'status' AS status,
    payload ->> 'title' AS title,
    loaded_at
FROM {{ source('raw', 'player_profiles_raw') }}