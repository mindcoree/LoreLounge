# Profile service — примечания по MinIO и загрузке медиа

Этот документ описывает, как работает загрузка аватаров/фонов в сервисе `profile` и как фронтенд должен взаимодействовать с API.

Файлы и места, которые важно знать:
- Роутер загрузки: [src/api/routers/profile.py](src/api/routers/profile.py) — `POST /api/profile/me/upload`
- Сервис загрузки: [src/domain/services/media.py](src/domain/services/media.py) — `MediaService.upload_media()`
- MinIO клиент: [src/infrastructure/storage/minio_client.py](src/infrastructure/storage/minio_client.py)
- Схема ответа загрузки: [src/api/schemas/profile.py](src/api/schemas/profile.py) — `UploadURLs`

Ключевая идея
- Фронтенд должен сначала вызвать один endpoint для загрузки медиа (если есть файлы), получить URL-ы, а затем вызвать `POST /api/profile/me` чтобы создать профиль, передав полученные URL-ы в тело (поля `avatar_url` и `background_url`).
- KrakenD проксирует JWT и ставит заголовок `X-User-ID`, поэтому сервис получает `guard` (UUID пользователя) и размещает файлы в MinIO по структуре:

  `lorelounge-media/profile/avatar/{user_id}/{filename}`

  `lorelounge-media/profile/background/{user_id}/{filename}`

. Т.е. файлы группируются по типу и по пользователю.

Переменные окружения (см. `.env` в корне сервиса):
```
PROFILE_CONFIG__MINIO__ENDPOINT=localhost:9000
PROFILE_CONFIG__MINIO__ACCESS_KEY=admin
PROFILE_CONFIG__MINIO__SECRET_KEY=SuperSecret123!
PROFILE_CONFIG__MINIO__USE_SSL=false
PROFILE_CONFIG__MINIO__BUCKET_NAME=lorelounge-media
PROFILE_CONFIG__MINIO__BASE_PATH=profile
```

Примеры HTTP-запросов

1) Загрузить файлы (multipart). Возвращает JSON с `avatar_url` и `background_url` (может быть `null`):

```bash
curl -v -X POST 'http://localhost:8000/api/profile/me/upload' \
  -H 'Cookie: access_token=<token>' \
  -F 'avatar=@/path/to/avatar.jpg' \
  -F 'background=@/path/to/background.jpg'
```

Ответ (пример):
```json
{
  "avatar_url": "http://localhost:9000/lorelounge-media/profile/avatar/550e8400-e29b-41d4-a716-446655440000/avatar.jpg",
  "background_url": "http://localhost:9000/lorelounge-media/profile/background/550e8400-e29b-41d4-a716-446655440000/background.jpg"
}
```

2) Создать профиль, если у фронтенда уже есть URL-ы (по результату шага 1):

```bash
curl -v -X POST 'http://localhost:8000/api/profile/me' \
  -H 'Content-Type: application/json' \
  -H 'Cookie: access_token=<token>' \
  -d '{"name":"myname","bio":"hi","avatar_url":"<avatar_url>","background_url":"<background_url>"}'
```

Замечания и рекомендации
- Если фронтенд не передаёт файлы, он может сразу вызвать `POST /api/profile/me` без шага загрузки.
- Размеры файлов: текущая реализация читает файл в память; это нормально для аватаров/фонов (~до нескольких мегабайт). Для больших файлов нужно изменить потоковую передачу в `minio_client.put_object()`.
- После изменения Krakend-конфигурации, перезапустите контейнеры gateway:

```bash
docker compose up -d --force-recreate krakend nginx
```

Если хотите, могу добавить пример интеграционного теста или curl-скрипт с переменными окружения и автоматизированной проверкой.
