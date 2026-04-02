from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile, HTTPException, status
from app.config import get_settings
import uuid

settings = get_settings()

class MinioService:
    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT.replace("http://", "").replace("https://", ""),
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME

    async def upload_avatar(self, file: UploadFile, task_id: str) -> str:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only image files are allowed"
            )

        file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        object_name = f"tasks/{task_id}/avatar_{uuid.uuid4()}.{file_ext}"

        try:
            file_data = await file.read()
            
            self.client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_name,
                data=file_data,
                length=len(file_data),
                content_type=file.content_type
            )

            
            base_url = settings.MINIO_ENDPOINT.replace("minio:9000", "localhost:9000")
            return f"{base_url}/{self.bucket_name}/{object_name}"

        except S3Error as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload to MinIO: {str(e)}"
            )