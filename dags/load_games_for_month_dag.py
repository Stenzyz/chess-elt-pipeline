from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from client import ApiClient
from loader import load_player_month

chunk_size = 100


def build_kwargs_list(**kwargs):
    data = kwargs["ti"].xcom_pull(task_ids="get_titled_players")
    data_chunked = [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]
    return [{"usernames": chunk} for chunk in data_chunked]


def get_titled_players(**kwargs):
    client = ApiClient()
    data = client.get_titled("GM")
    return data["players"]


def load_games_for_month(usernames, **kwargs):
    hook = PostgresHook(postgres_conn_id="postgres_dwh")
    interval_start = kwargs["data_interval_start"]
    year = interval_start.year
    month = interval_start.month
    batch_id = kwargs["run_id"]
    client = ApiClient()
    with hook.get_conn() as conn:
        for username in usernames:
            load_player_month(client, conn, username, year, month, batch_id)


with DAG(
    dag_id="monthly_games_load",
    schedule="@monthly",
    start_date=datetime(2024, 8, 1),
    catchup=True,
    max_active_runs=1,
) as dag:
    task_get_players = PythonOperator(
        task_id="get_titled_players", python_callable=get_titled_players
    )
    task_build_kwargs = PythonOperator(
        task_id="build_kwargs_list", python_callable=build_kwargs_list
    )
    task_load_games = PythonOperator.partial(
        task_id="load_games_for_month",
        python_callable=load_games_for_month,
        pool="chess_pool",
    ).expand(op_kwargs=task_build_kwargs.output)
    task_get_players >> task_build_kwargs >> task_load_games
