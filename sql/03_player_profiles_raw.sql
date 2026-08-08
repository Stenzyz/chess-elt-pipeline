CREATE TABLE IF NOT EXISTS raw.player_profiles_raw (
	id			   BIGSERIAL PRIMARY KEY,
	username       VARCHAR(25) NOT NULL,
	payload        jsonb NOT NULL,
	loaded_at	   timestamptz NOT NULL,
	batch_id	   VARCHAR NOT NULL,
	UNIQUE (username)
)