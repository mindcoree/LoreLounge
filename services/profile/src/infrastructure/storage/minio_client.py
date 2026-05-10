from uuid import UUID
import io
import logging

from miniopy_async.api import Minio
from miniopy_async.error import S3Error
from fastapi import UploadFile

from config.settings import settings


logger = logging.getLogger(__name__)

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


async def _ensure_bucket_exists(client: Minio) -> None:
    bucket_name = settings.minio.bucket_name
    exists = await client.bucket_exists(bucket_name)
    if not exists:
        await client.make_bucket(bucket_name)

async def upload_file_to_minio(
    user_id: UUID,
    upload: UploadFile,
    file_type: str = "avatar",
) -> str:
    # Загружаем файл в оперативную память (ОК для аватарок до 5-10 МБ)
    data = await upload.read()

    object_name = build_object_name(user_id, file_type)
    client = _get_minio_client()
    await _ensure_bucket_exists(client)

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
    return f"/media/{settings.minio.bucket_name}/{object_name}"


async def delete_file_from_minio(user_id: UUID, file_type: str = "avatar") -> None:
    object_name = build_object_name(user_id, file_type)
    client = _get_minio_client()
    try:
        await client.remove_object(settings.minio.bucket_name, object_name)
    except S3Error as exc:
        # Deletion should be idempotent: if bucket/object is missing, treat as already deleted.
        if exc.code in {"NoSuchBucket", "NoSuchKey"}:
            logger.info(
                "Skip deleting %s media for user_id=%s: %s",
                file_type,
                user_id,
                exc.code,
            )
            return
        logger.exception("Failed to delete %s media for user_id=%s", file_type, user_id)
    except Exception:
        logger.exception("Failed to delete %s media for user_id=%s", file_type, user_id)


async def delete_user_media_from_minio(user_id: UUID) -> None:
    await delete_file_from_minio(user_id, file_type="avatar")
    await delete_file_from_minio(user_id, file_type="background")