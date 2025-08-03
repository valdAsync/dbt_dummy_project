from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.dummy import DummyOperator

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2023, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "dummy_test_dag",
    default_args=default_args,
    description="A simple dummy DAG to test Airflow",
    schedule="@daily",
    catchup=False,
) as dag:
    start = DummyOperator(task_id="start")
    end = DummyOperator(task_id="end")

    start >> end
