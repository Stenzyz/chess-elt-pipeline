from datetime import datetime

from airflow.operators.bash import BashOperator
from airflow.sdk import DAG
from assets import GAMES_LOADED, STATS_LOADED
from shared_tasks import default_args

DBT_PROJECT_DIR = "/opt/airflow/dbt/chess_dbt"
DBT_PROFILES_DIR = "/opt/airflow/dbt/chess_dbt"

with DAG(
    dag_id="dbt_transform",
    default_args=default_args,
    schedule=[GAMES_LOADED, STATS_LOADED],
    start_date=datetime(2024, 8, 1),
    catchup=False,
    max_active_runs=1,
) as dag:
    task_dbt_build_staging = BashOperator(
        task_id="dbt_build_staging",
        bash_command=(
            f"dbt build --select staging --project-dir {DBT_PROJECT_DIR} "
            f"--profiles-dir {DBT_PROFILES_DIR}"
        ),
    )
    task_dbt_snapshot = BashOperator(
        task_id="dbt_snapshot",
        bash_command=(
            f"dbt snapshot --project-dir {DBT_PROJECT_DIR} "
            f"--profiles-dir {DBT_PROFILES_DIR}"
        ),
    )
    task_dbt_build_dds = BashOperator(
        task_id="dbt_build_dds",
        bash_command=(
            f"dbt build --select dds --project-dir {DBT_PROJECT_DIR} "
            f"--profiles-dir {DBT_PROFILES_DIR}"
        ),
    )

    task_dbt_build_staging >> task_dbt_snapshot >> task_dbt_build_dds
