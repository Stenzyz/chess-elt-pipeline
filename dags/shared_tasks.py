from datetime import datetime, timezone

from airflow.providers.postgres.hooks.postgres import PostgresHook
from client import ApiClient
from loader import load_player_month, load_player_stats

chunk_size = 100


def build_kwargs_list(schedule, **kwargs):
    data = kwargs["ti"].xcom_pull(task_ids="get_titled_players")
    data_chunked = [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]
    return [{"usernames": chunk, "schedule": schedule} for chunk in data_chunked]


def build_stats_kwargs_list(**kwargs):
    data = kwargs["ti"].xcom_pull(task_ids="get_titled_players")
    data_chunked = [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]
    return [{"usernames": chunk} for chunk in data_chunked]


def get_titled_players(**kwargs):
    client = ApiClient()
    data = client.get_titled("GM")
    return data["players"]


def load_games_for_player(usernames, schedule, **kwargs):
    hook = PostgresHook(postgres_conn_id="postgres_dwh")
    if schedule == "month":
        interval_start = kwargs["data_interval_start"]
        year = interval_start.year
        month = interval_start.month
    elif schedule == "day":
        now = datetime.now(timezone.utc)
        year = now.year
        month = now.month
    else:
        raise ValueError(f"Unknown schedule: {schedule}")
    batch_id = kwargs["run_id"]
    client = ApiClient()
    with hook.get_conn() as conn:
        for username in usernames:
            load_player_month(client, conn, username, year, month, batch_id)


def load_stats_for_player(usernames, **kwargs):
    hook = PostgresHook(postgres_conn_id="postgres_dwh")
    batch_id = kwargs["run_id"]
    client = ApiClient()
    snapshot_date = datetime.now(timezone.utc).date()
    with hook.get_conn() as conn:
        for username in usernames:
            load_player_stats(client, conn, username, snapshot_date, batch_id)
