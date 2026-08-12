from airflow.sdk import Asset

GAMES_LOADED = Asset("games_raw_loaded")
STATS_LOADED = Asset("stats_snapshot_loaded")
