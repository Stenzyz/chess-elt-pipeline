from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from shared_tasks import (
    build_username_kwargs_list,
    default_args,
    get_titled_players,
    load_profile_for_player,
)

with DAG(
    dag_id="weekly_profile_load",
    default_args=default_args,
    schedule="@weekly",
    start_date=datetime(2024, 8, 1),
    catchup=False,
    max_active_runs=1,
) as dag:
    task_get_players = PythonOperator(
        task_id="get_titled_players", python_callable=get_titled_players
    )
    task_build_kwargs = PythonOperator(
        task_id="build_username_kwargs_list",
        python_callable=build_username_kwargs_list,
    )
    task_load_profiles = PythonOperator.partial(
        task_id="load_profiles_for_week",
        python_callable=load_profile_for_player,
        pool="chess_pool",
    ).expand(op_kwargs=task_build_kwargs.output)
    task_get_players >> task_build_kwargs >> task_load_profiles
