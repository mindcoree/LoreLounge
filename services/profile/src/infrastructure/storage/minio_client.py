from uuid import UUID
import io
from typing import Optional

from miniopy_async import Minio 
from fastapi import UploadFile

from config.settings import settings

def _get_minio_client() -> Minio:
    s = settings.minio
    return Minio(
        endpoint=s.endpoint,
        access_key=s.access_key,
        secret_key=s.secret_key,
        secure=bool(s.use_ssl),
    )

async def upload_file_to_minio(
    user_id: UUID,
    upload: UploadFile,
    file_type: str = "avatar",
    filename: Optional[str] = None,
) -> str:
    # Загружаем файл в оперативную память (ОК для аватарок до 5-10 МБ)
    data = await upload.read() 
    
    if not filename:
        filename = upload.filename or "file"

    object_name = f"{settings.minio.base_path}/{file_type}/{user_id}/{filename}"
    client = _get_minio_client()

    # Теперь метод put_object нативный асинхронный! Никаких anyio и потоков.
    await client.put_object(
        bucket_name=settings.minio.bucket_name,
        object_name=object_name,
        data=io.BytesIO(data),
        length=len(data),
        content_type=upload.content_type,
    )

    scheme = "https" if settings.minio.use_ssl else "http"
    return f"{scheme}://{settings.minio.endpoint}/{settings.minio.bucket_name}/{object_name}"