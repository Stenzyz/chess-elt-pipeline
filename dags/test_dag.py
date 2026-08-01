from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


def print_date():
    print(f"Текущая дата: {datetime.now()}")


with DAG(
    dag_id="test_dag",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:
    task_print_date = PythonOperator(
        task_id="print_date",
        python_callable=print_date,
    )
    task_select_1 = SQLExecuteQueryOperator(
        task_id="select_1",
        conn_id="postgres_dwh",
        sql="SELECT 1;",
    )
    task_print_date >> task_select_1
