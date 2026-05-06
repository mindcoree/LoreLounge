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
│   ├── api/             # Маршруты, схемы, зависимости и обработчики
│   │   ├── routers/     # Эндпоинты профиля
│   │   ├── schemas/     # Pydantic модели
│   │   └── dependencies/# Зависимости (DI)
│   ├── config/          # Настройки (DB, MinIO, RabbitMQ)
│   ├── domain/          # Бизнес-логика
│   │   ├── services/    # MediaService и др.
│   │   └── exceptions/  # Кастомные исключения
│   ├── infrastructure/  # Внешние реализации
│   │   ├── db/          # PostgreSQL (SQLAlchemy)
│   │   └── storage/     # Клиент MinIO
│   └── main.py          # Точка входа FastAPI
├── Dockerfile           # Инструкции для сборки
└── requirements.txt     # Зависимости Python
```

## Основные endpoints (под `/api/profile`)

| Метод | Путь | Доступ | Описание |
|-------|------|:------:|---------|
| GET | `/{name}` | public | Публичный профиль пользователя |
| GET | `/me` | 🔒 JWT | Мой профиль |
| POST | `/me` | 🔒 JWT | Создать профиль |
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
3. Фронтенд вызывает `POST /api/profile/me` (или `PATCH`), передавая полученные URL в теле запроса.

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
