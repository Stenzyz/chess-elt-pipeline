create table raw.games_raw (
	id            BIGSERIAL PRIMARY key,
	username      VARCHAR(25) not NULL,
	archive_month DATE NOT NULL,
	payload       jsonb NOT NULL,
	loaded_at     timestamptz NOT NULL,
	batch_id      VARCHAR NOT null,
	UNIQUE (username, archive_month)
	)
