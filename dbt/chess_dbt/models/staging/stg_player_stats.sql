{{ config(materialized='table') }}

SELECT
    username,
    'rapid' as time_class,
    snapshot_date,
    loaded_at,
    (payload -> 'chess_rapid' -> 'record' ->> 'win')::integer as win,
    (payload -> 'chess_rapid' -> 'record' ->> 'loss')::integer as loss,
    (payload -> 'chess_rapid' -> 'record' ->> 'draw')::integer as draw,
    (payload -> 'chess_rapid' -> 'last' ->> 'rating')::integer as rating,
    to_timestamp((payload -> 'chess_rapid' -> 'last' ->> 'date')::bigint) AS last_game_date
FROM {{ source('raw', 'stats_snapshot_raw') }}
WHERE payload ? 'chess_rapid'
UNION ALL
SELECT
    username,
    'bullet' as time_class,
    snapshot_date,
    loaded_at,
    (payload -> 'chess_bullet' -> 'record' ->> 'win')::integer as win,
    (payload -> 'chess_bullet' -> 'record' ->> 'loss')::integer as loss,
    (payload -> 'chess_bullet' -> 'record' ->> 'draw')::integer as draw,
    (payload -> 'chess_bullet' -> 'last' ->> 'rating')::integer as rating,
    to_timestamp((payload -> 'chess_bullet' -> 'last' ->> 'date')::bigint) AS last_game_date
FROM {{ source('raw', 'stats_snapshot_raw') }}
WHERE payload ? 'chess_bullet'
UNION ALL
SELECT
    username,
    'blitz' as time_class,
    snapshot_date,
    loaded_at,
    (payload -> 'chess_blitz' -> 'record' ->> 'win')::integer as win,
    (payload -> 'chess_blitz' -> 'record' ->> 'loss')::integer as loss,
    (payload -> 'chess_blitz' -> 'record' ->> 'draw')::integer as draw,
    (payload -> 'chess_blitz' -> 'last' ->> 'rating')::integer as rating,
    to_timestamp((payload -> 'chess_blitz' -> 'last' ->> 'date')::bigint) AS last_game_date
FROM {{ source('raw', 'stats_snapshot_raw') }}
WHERE payload ? 'chess_blitz'