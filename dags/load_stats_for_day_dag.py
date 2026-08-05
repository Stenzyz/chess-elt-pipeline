from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from shared_tasks import (
    build_stats_kwargs_list,
    get_titled_players,
    load_stats_for_player,
)

with DAG(
    dag_id="daily_stats_load",
    schedule="@daily",
    start_date=datetime(2024, 8, 1),
    catchup=False,
    max_active_runs=1,
) as dag:
    task_get_players = PythonOperator(
        task_id="get_titled_players", python_callable=get_titled_players
    )
    task_build_kwargs = PythonOperator(
        task_id="build_stats_kwargs_list",
        python_callable=build_stats_kwargs_list,
    )
    task_load_stats = PythonOperator.partial(
        task_id="load_stats_for_day",
        python_callable=load_stats_for_player,
        pool="chess_pool",
    ).expand(op_kwargs=task_build_kwargs.output)
    task_get_players >> task_build_kwargs >> task_load_stats
