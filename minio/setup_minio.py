import os
import time

from minio import Minio
from minio.error import S3Error

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "raw")


def wait_for_minio(client):
    print("Waiting for MinIO...")
    for _ in range(30):
        try:
            client.bucket_exists("non-existent-bucket-for-health-check")
            print("MinIO is up!")
            return True
        except Exception:
            time.sleep(2)
    print("MinIO did not become available in time.")
    return False


def main():
    """Connects to MinIO and creates a bucket if it doesn't already exist."""
    client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False,
    )

    if not wait_for_minio(client):
        return

    try:
        found = client.bucket_exists(BUCKET_NAME)
        if not found:
            client.make_bucket(BUCKET_NAME)
            print(f"Bucket '{BUCKET_NAME}' created successfully.")
        else:
            print(f"Bucket '{BUCKET_NAME}' already exists.")

    except S3Error as exc:
        print("Error occurred:", exc)


if __name__ == "__main__":
    main()
