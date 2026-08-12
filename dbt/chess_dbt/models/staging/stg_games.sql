{{ config(materialized='table') }}

SELECT DISTINCT ON (game ->> 'uuid')
    game ->> 'uuid' AS uuid,
    game ->> 'url' AS game_url,
    game ->> 'time_class' AS time_class,
    split_part((game ->> 'time_control'),'+', 1)::integer AS base_time,
    NULLIF(split_part((game ->> 'time_control'), '+', 2), '')::REAL AS increment_time,
    LOWER(game -> 'white' ->> 'username') AS white_username,
    LOWER(game -> 'black' ->> 'username') AS black_username,
    game -> 'white' ->> 'result' AS white_result,
    game -> 'black' ->> 'result' AS black_result,
    CASE
        WHEN game -> 'white' ->> 'result' = 'win' THEN 'white'
        WHEN game -> 'black' ->> 'result' = 'win' THEN 'black'
        ELSE 'draw'
    END AS outcome,
    CASE
        WHEN game -> 'white' ->> 'result' = 'win' THEN game -> 'black' ->> 'result'
        WHEN game -> 'black' ->> 'result' = 'win' THEN game -> 'white' ->> 'result'
        ELSE game -> 'white' ->> 'result'
    END AS termination,
    (game -> 'white' ->> 'rating')::integer AS white_rating,
    (game -> 'black' ->> 'rating')::integer AS black_rating,
    (game -> 'accuracies' ->> 'white')::real AS white_accuracies,
    (game -> 'accuracies' ->> 'black')::real AS black_accuracies,
    trim(
        regexp_replace(
            replace(split_part(split_part((game ->> 'eco'), '/openings/', 2), '...', 1), '-', ' '),
        '\s*\d.*$', ''
        )
    ) AS eco,
    to_timestamp((game ->> 'end_time')::bigint) AS end_time
FROM {{ source('raw', 'games_raw') }},
     jsonb_array_elements(payload -> 'games') AS game
WHERE (game ->> 'rated')::boolean = true
  AND game ->> 'rules' = 'chess'
  AND game ->> 'time_class' != 'daily'
ORDER BY game ->> 'uuid', loaded_at DESC