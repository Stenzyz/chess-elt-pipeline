INSERT INTO stage.games (
    uuid, game_url, rated, rules, time_class, time_control,
    white_username, black_username, white_result, black_result,
    white_rating, black_rating, white_accuracies, black_accuracies,
    eco, end_time
)
SELECT DISTINCT ON (game ->> 'uuid')
    game ->> 'uuid',
    game ->> 'url',
    (game ->> 'rated')::boolean,
    game ->> 'rules',
    game ->> 'time_class',
    game ->> 'time_control',
    game -> 'white' ->> 'username',
    game -> 'black' ->> 'username',
    game -> 'white' ->> 'result',
    game -> 'black' ->> 'result',
    (game -> 'white' ->> 'rating')::integer,
    (game -> 'black' ->> 'rating')::integer,
    (game -> 'accuracies' ->> 'white')::real,
    (game -> 'accuracies' ->> 'black')::real,
    game ->> 'eco',
    (game ->> 'end_time')::bigint
FROM raw.games_raw,
     jsonb_array_elements(payload -> 'games') AS game
ORDER BY game ->> 'uuid', loaded_at DESC;