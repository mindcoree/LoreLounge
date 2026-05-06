# Auth Service

Микросервис аутентификации и авторизации LoreLounge.

## Назначение

- Регистрация пользователей.
- Вход и выдача `access`/`refresh` JWT в http-only cookies.
- Обновление `access` по `refresh`.
- Выход (logout) с отзывом refresh-токена через Redis.
- Выдача JWKS для KrakenD.
- Сброс пароля (request/confirm) с отправкой email через RabbitMQ.
- Управление ролями пользователей и заявками на изменение ролей.

## Технологический стек

- **Ядро**: FastAPI + Pydantic Settings.
- **JWT**: RS256, публичный ключ отдаётся через `/.well-known/jwks.json`.
- **Хранилище**: PostgreSQL (основные сущности), Redis (revoked refresh tokens).
- **Брокер**: RabbitMQ (уведомления о сбросе пароля).
- **Миграции**: Alembic.

## Структура папок

```text
auth/
├── certs/               # RSA ключи (private.pem, public.pem)
├── migrations/          # Alembic миграции
├── src/
│   ├── api/             # Маршруты и обработчики исключений
│   │   └── router/      # Группировка эндпоинтов
│   ├── core/            # Конфигурация, безопасность (JWT logic), типы
│   ├── domain/          # Бизнес-логика и сущности (Clean Architecture)
│   │   ├── common/      # Общие схемы и сущности
│   │   ├── entity/      # Модели БД и схемы Pydantic
│   │   └── role_requests/ # Логика заявок на роли
│   ├── infrastructure/  # Внешние зависимости
│   │   ├── broker/      # Интеграция с RabbitMQ
│   │   ├── cache/       # Работа с Redis
│   │   └── db/          # Сессии и настройки PostgreSQL
│   └── main.py          # Точка входа FastAPI
├── alembic.ini          # Конфиг Alembic
├── Dockerfile           # Инструкции для сборки контейнера
└── requirements.txt     # Зависимости Python
```

## Основные endpoints (под `/api/auth`)

| Метод | Путь | Доступ | Описание |
|-------|------|:------:|---------|
| POST | `/register` | public | Регистрация |
| POST | `/login` | public | Вход (выдаёт JWT cookies) |
| POST | `/logout` | public | Выход (отзывает refresh) |
| POST | `/refresh` | public | Обновление access-токена |
| POST | `/password-reset-request` | public | Запрос сброса пароля |
| POST | `/password-reset-confirm` | public | Подтверждение сброса пароля |
| GET | `/me` | 🔒 JWT | Данные текущего пользователя |
| POST | `/role-request` | 🔒 JWT | Заявка на изменение роли |
| GET | `/role-requests/` | 🔒 JWT | Список заявок на роль |
| POST | `/role-requests/{id}/approve` | 🔒 JWT | Одобрить заявку |
| POST | `/role-requests/{id}/reject` | 🔒 JWT | Отклонить заявку |
| GET | `/.well-known/jwks.json` | public | Публичный ключ (JWKS) |

## Реальный logout (refresh revoke)

- При logout refresh-токен сохраняется в Redis в виде `revoked:refresh:{jti}`.
- TTL равен оставшемуся времени жизни refresh-токена.
- При `POST /refresh` проверяется Redis: если `jti` отозван, возвращается 401.
- Access-токен живёт до своего TTL (короткий срок).

## JWT и cookies

- Cookies: `access_token`, `refresh_token`.
- Access TTL задаётся `CONFIG__AUTH__ACCESS_EXPIRE_MIN`.

## Конфигурация (.env)

Примеры (см. `.env.example`):

- `CONFIG__DB__URL` — PostgreSQL URL.
- `CONFIG__AUTH__ACCESS_EXPIRE_MIN` — TTL access (минуты).
- `CONFIG__AUTH__REFRESH_EXPIRE_DAYS` — TTL refresh (дни).
- `CONFIG__REDIS__URL` — Redis URL (revoked refresh tokens).
- `CONFIG__FRONTEND_URL` — URL фронтенда для reset-ссылок.
- `CONFIG__RUN__SHOW_DOCS=True` — включить Swagger.

## Запуск (Docker)

```bash
# из корня проекта
make up
```

Сервис доступен через Nginx и KrakenD:
- `http://localhost/api/auth/*`
