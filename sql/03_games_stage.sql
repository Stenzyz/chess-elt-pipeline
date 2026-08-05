CREATE TABLE IF NOT EXISTS stage.games (
    id BIGSERIAL PRIMARY KEY,
    uuid VARCHAR(50) UNIQUE NOT NULL,
    game_url TEXT NOT NULL,
    rated BOOLEAN NOT NULL,
    rules VARCHAR(30) NOT NULL,
    time_class VARCHAR(30) NOT NULL,
    time_control VARCHAR(15) NOT NULL,
    white_username VARCHAR(25) NOT NULL,
    black_username VARCHAR(25) NOT NULL,
    white_result VARCHAR(20) NOT NULL,
    black_result VARCHAR(20) NOT NULL,
    white_rating INTEGER NOT NULL,
    black_rating INTEGER NOT NULL,
    white_accuracies REAL,
    black_accuracies REAL,
    eco TEXT,
    end_time BIGINT NOT NULL
)
