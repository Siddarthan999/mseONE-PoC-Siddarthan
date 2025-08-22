from minio import Minio
import os

minio_client = Minio(
    os.getenv("MINIO_ENDPOINT", "minio:9000"),
    access_key=os.getenv("MINIO_ROOT_USER", "minio"),
    secret_key=os.getenv("MINIO_ROOT_PASSWORD", "miniopassword"),
    secure=False
)

BUCKET_NAME = os.getenv("MINIO_BUCKET", "poc-bucket")

# Ensure bucket exists
found = minio_client.bucket_exists(BUCKET_NAME)
if not found:
    minio_client.make_bucket(BUCKET_NAME)
