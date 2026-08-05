from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from shared_tasks import (
    build_kwargs_list,
    default_args,
    get_titled_players,
    load_games_for_player,
)

with DAG(
    dag_id="monthly_games_load",
    default_args=default_args,
    schedule="@monthly",
    start_date=datetime(2024, 8, 1),
    catchup=True,
    max_active_runs=1,
) as dag:
    task_get_players = PythonOperator(
        task_id="get_titled_players", python_callable=get_titled_players
    )
    task_build_kwargs = PythonOperator(
        task_id="build_kwargs_list",
        python_callable=build_kwargs_list,
        op_kwargs={"schedule": "month"},
    )
    task_load_games = PythonOperator.partial(
        task_id="load_games_for_month",
        python_callable=load_games_for_player,
        pool="chess_pool",
    ).expand(op_kwargs=task_build_kwargs.output)
    task_get_players >> task_build_kwargs >> task_load_games
