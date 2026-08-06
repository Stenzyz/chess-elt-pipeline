INSERT INTO stage.games (
    uuid, game_url, time_class, base_time, increment_time,
    white_username, black_username, white_result, black_result,
    outcome, termination,
    white_rating, black_rating, white_accuracies, black_accuracies,
    eco, end_time
)
SELECT DISTINCT ON (game ->> 'uuid')
    game ->> 'uuid',
    game ->> 'url',
    game ->> 'time_class',
    split_part((game ->> 'time_control'),'+', 1)::integer,
    NULLIF(split_part((game ->> 'time_control'), '+', 2), '')::REAL,
    game -> 'white' ->> 'username',
    game -> 'black' ->> 'username',
    game -> 'white' ->> 'result',
    game -> 'black' ->> 'result',
    CASE
        WHEN game -> 'white' ->> 'result' = 'win' THEN 'white'
        WHEN game -> 'black' ->> 'result' = 'win' THEN 'black'
        ELSE 'draw'
    END,
    CASE
        WHEN game -> 'white' ->> 'result' = 'win' THEN game -> 'black' ->> 'result'
        WHEN game -> 'black' ->> 'result' = 'win' THEN game -> 'white' ->> 'result'
        ELSE game -> 'white' ->> 'result'
    END,
    (game -> 'white' ->> 'rating')::integer,
    (game -> 'black' ->> 'rating')::integer,
    (game -> 'accuracies' ->> 'white')::real,
    (game -> 'accuracies' ->> 'black')::real,
    trim(
        regexp_replace(
            replace(split_part(split_part((game ->> 'eco'), '/openings/', 2), '...', 1), '-', ' '),
        '\s*\d.*$', ''
        )
    ),
    to_timestamp((game ->> 'end_time')::bigint)
FROM raw.games_raw,
     jsonb_array_elements(payload -> 'games') AS game
WHERE (game ->> 'rated')::boolean = true
  AND game ->> 'rules' = 'chess'
  AND game ->> 'time_class' != 'daily'
ORDER BY game ->> 'uuid', loaded_at DESC;