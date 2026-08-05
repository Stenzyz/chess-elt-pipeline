CREATE TABLE IF NOT EXISTS raw.stats_snapshot_raw (
	id			   BIGSERIAL PRIMARY KEY,
	username       VARCHAR(25) NOT NULL,
	snapshot_date  DATE NOT NULL,
	payload        jsonb NOT NULL,
	loaded_at	   timestamptz NOT NULL,
	batch_id	   VARCHAR NOT NULL,
	UNIQUE (username, snapshot_date)
)