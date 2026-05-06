# Profile Service

Микросервис управления профилями пользователей LoreLounge.

## Назначение

- Создание и редактирование профилей пользователей.
- Загрузка и хранение аватаров и фоновых изображений (через MinIO).
- Управление списком игнорируемых пользователей.
- Просмотр публичных профилей.

## Технологический стек

- **Ядро**: FastAPI + Pydantic Settings.
- **Хранилище**: PostgreSQL (данные профилей), MinIO (медиа-файлы).
- **Брокер**: RabbitMQ (для будущих событий обновления профиля).

## Структура папок

```text
profile/
├── src/
│   ├── api/                   # Маршруты, схемы, зависимости и обработчики
│   │   ├── routers/           # profile.py, ignore_list.py
│   │   ├── schemas/           # profile.py, ignore_list.py, pagination.py
│   │   ├── dependencies/      # auth.py, service.py, session.py
│   │   └── handlers/          # error_profile.py, error_ignore_list.py
│   ├── config/                # settings.py, database.py, minio.py, prefixes.py
│   ├── domain/                # Бизнес-логика
│   │   ├── services/          # profile.py, media.py, ignore_list.py
│   │   └── exceptions/        # profile.py, ignore_list.py, base.py
│   ├── infrastructure/        # Внешние реализации
│   │   ├── db/                # SQLAlchemy (session, asyncpg)
│   │   │   ├── migrations/    # alembic.ini, env.py, versions/
│   │   │   ├── models/        # base.py, ignore_list.py, profile.py
│   │   │   ├── repositories/  # base.py, ignore_list.py, profile.py
│   │   │   ├── types.py       # mixins.py, model_type.py
│   │   │   ├── db_helper.py   # helper for db and session
│   │   │   └── alembic.ini    # configuration Alembic
│   │   └── storage/           # minio_client.py
│   └── main.py                # Точка входа FastAPI
├── Dockerfile                 # Инструкции для сборки
├── prestart.sh                # скрипт для запуска alembic  
├── Makefile                   # Makefile для удобной работы
└── requirements.txt           # Зависимости Python
```

## Основные endpoints (под `/api/profile`)

| Метод | Путь | Доступ | Описание |
|-------|------|:------:|---------|
| GET | `/{name}` | public | Публичный профиль пользователя |
| GET | `/me` | 🔒 JWT | Мой профиль |
| PUT | `/me` | 🔒 JWT | Создать/Заменить профиль |
| PATCH | `/me` | 🔒 JWT | Обновить профиль |
| POST | `/me/upload` | 🔒 JWT | Загрузить аватар/фон (MinIO) |
| GET | `/me/ignored` | 🔒 JWT | Список игнорируемых |
| POST | `/me/ignored/{id}` | 🔒 JWT | Добавить в игнор |
| DELETE | `/me/ignored/{id}` | 🔒 JWT | Убрать из игнора |

## Работа с медиа (MinIO)

Файлы загружаются по следующей структуре:
- Аватары: `lorelounge-media/profile/avatar/{user_id}/{filename}`
- Фоны: `lorelounge-media/profile/background/{user_id}/{filename}`

### Поток загрузки медиа

1. Фронтенд вызывает `POST /api/profile/me/upload` с `multipart/form-data`.
2. Получает JSON с `avatar_url` и `background_url`.
3. Фронтенд вызывает `PUT /api/profile/me` (или `PATCH`), передавая полученные URL в теле запроса.

## Конфигурация (.env)

| Переменная | Описание |
|------------|---------|
| `PROFILE_CONFIG__DB__POSTGRES_USER` | Пользователь БД |
| `PROFILE_CONFIG__DB__POSTGRES_PASSWORD` | Пароль БД |
| `PROFILE_CONFIG__DB__POSTGRES_SERVER` | Хост БД |
| `PROFILE_CONFIG__DB__POSTGRES_DB` | Имя БД |
| `PROFILE_CONFIG__MINIO__ENDPOINT` | Адрес MinIO |
| `PROFILE_CONFIG__MINIO__ACCESS_KEY` | Access Key |
| `PROFILE_CONFIG__MINIO__SECRET_KEY` | Secret Key |
| `PROFILE_CONFIG__MINIO__BUCKET_NAME` | Имя бакета |

## Запуск (Docker)

```bash
# из корня проекта
make up
```

Сервис доступен через Nginx и KrakenD:
- `http://localhost/api/profile/*`
