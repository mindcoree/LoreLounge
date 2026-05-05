# Auth Service

Микросервис аутентификации и авторизации LoreLounge.

## Назначение

- Регистрация пользователей.
- Вход и выдача `access`/`refresh` JWT в http-only cookies.
- Обновление `access` по `refresh`.
- Выход (logout) с отзывом refresh-токена через Redis.
- Выдача JWKS для KrakenD.
- Сброс пароля (request/confirm) с отправкой email через RabbitMQ.

## Архитектура

- Ядро: FastAPI + Pydantic Settings.
- JWT: RS256, публичный ключ отдаётся через `/.well-known/jwks.json`.
- Хранилище: PostgreSQL (основные сущности), Redis (revoked refresh tokens).
- Брокер: RabbitMQ (уведомления о сбросе пароля).

## Основные endpoints (под `/api/auth`)

- `POST /register` — регистрация.
- `POST /login` — вход, выдаёт cookies с access/refresh.
- `POST /refresh` — обновляет access по refresh cookie.
- `POST /logout` — удаляет cookies и отзывает refresh.
- `GET /me` — данные пользователя из payload (через KrakenD).
- `POST /password-reset-request` — запрос на сброс пароля.
- `POST /password-reset-confirm` — подтверждение сброса.
- `GET /.well-known/jwks.json` — публичный ключ (JWKS).

## Реальный logout (refresh revoke)

- При logout refresh-токен сохраняется в Redis в виде `revoked:refresh:{jti}`.
- TTL равен оставшемуся времени жизни refresh-токена.
- При `POST /refresh` проверяется Redis: если `jti` отозван, возвращается 401.
- Access-токен живёт до своего TTL (короткий срок).

## JWT и cookies

- Cookies: `access_token`, `refresh_token`.
- Access TTL задаётся `CONFIG__AUTH__ACCESS_EXPIRE_MIN`.
- Refresh TTL:
  - если `CONFIG__AUTH__REFRESH_EXPIRE_MIN` задан, используется он;
  - иначе `CONFIG__AUTH__REFRESH_EXPIRE_DAYS`.

## Конфигурация (.env)

Примеры (см. `.env.example`):

- `CONFIG__DB__URL` — PostgreSQL URL.
- `CONFIG__AUTH__ACCESS_EXPIRE_MIN` — TTL access.
- `CONFIG__AUTH__REFRESH_EXPIRE_MIN` — TTL refresh в минутах (опционально).
- `CONFIG__AUTH__REFRESH_EXPIRE_DAYS` — TTL refresh в днях (fallback).
- `CONFIG__REDIS__URL` — Redis URL (revoked refresh tokens).
- `CONFIG__FRONTEND_URL` — URL фронтенда для reset-ссылок.
- `CONFIG__RUN__SHOW_DOCS=True` — включить Swagger.

## Swagger

- URL: `http://localhost/api/auth/docs`

## Запуск (Docker)

```bash
# из корня проекта
make up
```

Сервис доступен через Nginx и KrakenD:

- `http://localhost/api/auth/*`

## Замечания

- Endpoint `/me` возвращает данные из payload, без обращения к БД.
- Для SSR на фронте нужно пробрасывать cookie в запросы.
