from uuid import UUID
import io

from miniopy_async.api import Minio
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


def build_object_name(user_id: UUID, file_type: str) -> str:
    return f"{settings.minio.base_path}/{file_type}/{user_id}/{file_type}"

async def upload_file_to_minio(
    user_id: UUID,
    upload: UploadFile,
    file_type: str = "avatar",
) -> str:
    # Загружаем файл в оперативную память (ОК для аватарок до 5-10 МБ)
    data = await upload.read()

    object_name = build_object_name(user_id, file_type)
    client = _get_minio_client()

    # Один и тот же object_name для каждого пользователя и типа изображения
    # означает, что новая загрузка перезаписывает старую без отдельного delete.
    await client.put_object(
        bucket_name=settings.minio.bucket_name,
        object_name=object_name,
        data=io.BytesIO(data),
        length=len(data),
        content_type=upload.content_type or "application/octet-stream",
    )

    scheme = "https" if settings.minio.use_ssl else "http"
    return f"{scheme}://{settings.minio.endpoint}/{settings.minio.bucket_name}/{object_name}"