import io
from datetime import datetime, timedelta

from utils.data_generator import generate_dataframes

from airflow.decorators import dag, task
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    "etl_load_dummy_data_to_minio",
    default_args=default_args,
    description="Generate dummy data and load it to MinIO as CSV files, partitioned by date.",
    schedule="@daily",
    catchup=False,
    tags=["etl", "minio"],
)
def etl_load_dummy_data_to_minio():
    @task
    def generate_and_upload_data(ds_nodash=None):
        dataframes = generate_dataframes()
        s3_hook = S3Hook(aws_conn_id="minio_default")

        for name, df in dataframes.items():
            with io.BytesIO() as buffer:
                df.write_csv(buffer)
                buffer.seek(0)
                file_path = f"{name}_{ds_nodash}.csv"
                s3_hook.load_bytes(
                    buffer.getvalue(),
                    key=file_path,
                    bucket_name="raw",
                    replace=True,
                )
            print(f"Successfully uploaded {file_path} to MinIO bucket 'raw'.")

    generate_and_upload_data()


etl_load_dummy_data_to_minio()
