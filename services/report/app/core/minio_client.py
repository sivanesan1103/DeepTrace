import os
from minio import Minio
from typing import Optional
import tempfile
import os

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = "reports"

storage_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False,
)


async def ensure_bucket():
    if not storage_client.bucket_exists(MINIO_BUCKET):
        storage_client.make_bucket(MINIO_BUCKET)


async def upload_report(task_id: str, file_path: str, format: str = "pdf") -> str:
    await ensure_bucket()
    
    object_name = f"{task_id}/report.{format}"
    
    storage_client.fput_object(
        bucket_name=MINIO_BUCKET,
        object_name=object_name,
        file_path=file_path,
        content_type=f"application/{format}",
    )
    
    return f"/reports/{object_name}"


async def get_report(task_id: str) -> Optional[str]:
    object_name = f"{task_id}/report.pdf"
    
    try:
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f"{task_id}_report.pdf")
        
        storage_client.fget_object(
            bucket_name=MINIO_BUCKET,
            object_name=object_name,
            file_path=temp_file,
        )
        return temp_file
    except Exception:
        return None


async def download_report_to_file(task_id: str, format: str = "pdf") -> Optional[str]:
    object_name = f"{task_id}/report.{format}"
    
    try:
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f"{task_id}_report.{format}")
        
        storage_client.fget_object(
            bucket_name=MINIO_BUCKET,
            object_name=object_name,
            file_path=temp_file,
        )
        return temp_file
    except Exception:
        return None