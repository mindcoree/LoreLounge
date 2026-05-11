# LoreLounge

**LoreLounge** — платформа для чтения и каталогизации веб-новелл.

> Единственная публичная точка входа — **Nginx :80**. Все остальные порты открыты только для локальной отладки.

---

## Содержание

- [Стек технологий](#стек-технологий)
- [Архитектура](#архитектура)
- [Сетевая изоляция](#сетевая-изоляция)
- [Структура проекта](#структура-проекта)
- [Микросервисы](#микросервисы)
- [Быстрый старт](#быстрый-старт)
- [Маршрутизация](#маршрутизация)
- [Лицензия](#лицензия)

---

## Стек технологий

| Слой | Технологии |
|------|-----------|
| **Frontend** | Next.js 15, React 19, Tailwind CSS 4 |
| **Reverse Proxy** | Nginx |
| **API Gateway** | KrakenD 2.5 (Flexible Configuration) |
| **Микросервисы** | FastAPI (auth, profile), FastStream (notification) |
| **Базы данных** | PostgreSQL 15 (per-service), Redis 7 |
| **Хранилище файлов** | MinIO |
| **Брокер сообщений** | RabbitMQ 3 |
| **Инфраструктура** | Docker, Docker Compose, Make |

---

## Архитектура

```mermaid
---
config:
  flowchart:
    defaultRenderer: elk
  layout: dagre
---
flowchart LR
    %% --- Legend / Layout ---
    classDef gateway stroke:#818cf8,fill:#1e1b4b,color:#fff;
    classDef frontend stroke:#38bdf8,fill:#0c4a6e,color:#fff;
    classDef services stroke:#2dd4bf,fill:#134e4a,color:#fff;
    classDef storage stroke:#a3e635,fill:#365314,color:#fff;
    classDef broker stroke:#f87171,fill:#450a0a,color:#fff;
    classDef external stroke:#a78bfa,fill:#2e1065,color:#fff;

    Browser["Браузер<br/><small>Пользовательский интерфейс, который обращается к приложению</small>"]
    class Browser external

    subgraph gateway_layer["gateway_layer"]
        Nginx["Nginx<br/><small>HTTP маршрутизация и отдача статических файлов</small>"]
        KrakenD["KrakenD API Gateway<br/><small>Агрегация и передача запросов к микросервисам</small>"]
    end

    subgraph frontend_layer["frontend_layer"]
        Frontend["Next.js<br/><small>SSR/SPA клиентская часть приложения</small>"]
    end

    subgraph services_layer["services_layer"]
        Auth["Auth (FastAPI)<br/><small>Регистрация, вход, JWT токены</small>"]
        Profile["Profile (FastAPI)<br/><small>Хранение информации о пользователе</small>"]
        Notification["Notification (FastStream)<br/><small>Обработка и рассылка событий</small>"]
    end

    subgraph storage_layer["storage_layer"]
        PGAuth["Postgres Auth<br/><small>База данных авторизации</small>"]
        PGProfile["Postgres Profile<br/><small>База данных профилей</small>"]
        RedisAuth["Redis Auth<br/><small>Кэш и список аннулированных токенов</small>"]
        MinIO["MinIO<br/><small>Хранение медиа и аватаров</small>"]
    end

    subgraph broker_layer["broker_layer"]
        RabbitMQ["RabbitMQ<br/><small>Обмен событиями между сервисами</small>"]
    end

    class Nginx,KrakenD gateway
    class Frontend frontend
    class Auth,Profile,Notification services
    class PGAuth,RedisAuth,PGProfile,MinIO storage
    class RabbitMQ broker

    Browser -->|"HTTP :80"| Nginx
    Nginx -->|"/*"| Frontend
    Nginx -->|"/api/*"| KrakenD

    KrakenD -->|"JWT → headers"| Auth
    KrakenD -->|"JWT → headers"| Profile

    Auth -->|"SELECT / INSERT"| PGAuth
    Auth -->|"revoked tokens"| RedisAuth
    Auth -->|"publish event"| RabbitMQ

    Profile -->|"SELECT / INSERT"| PGProfile
    Profile -->|"avatars / media"| MinIO
    Profile -->|"publish event"| RabbitMQ

    Auth -.->|"ACCOUNT_DELETED"| RabbitMQ
    RabbitMQ -.->|"cleanup data"| Profile

    RabbitMQ -->|"subscribe"| Notification
```

![Архитектура системы](./docs/img/architecture.png)

---

## Сетевая изоляция

Каждый сервис видит только те соседей, которые ему нужны.

```mermaid
flowchart LR
    subgraph lorelounge_net["lorelounge_net (bridge)"]
        Nginx["nginx"]
        KrakenD["krakend"]
        Frontend["frontend"]
        Auth["auth"]
        Profile["profile"]
        Notification["notification"]
        MinIO["minio"]
    end

    subgraph auth_db_net["auth_db_net (bridge)"]
        Auth2["auth"]
        PGAuth["postgres_auth"]
        RedisAuth["redis_auth"]
    end

    subgraph profile_db_net["profile_db_net (bridge)"]
        Profile2["profile"]
        PGProfile["postgres_profile"]
    end

    subgraph broker_net["broker_net (internal)"]
        Auth3["auth"]
        Profile3["profile"]
        Notification2["notification"]
        RMQ["rabbitmq"]
    end
```

| Сеть | Участники | Примечание |
|------|-----------|-----------|
| `lorelounge_net` | nginx, krakend, frontend, auth, profile, notification, minio | Основная сервисная сеть |
| `auth_db_net` | auth, postgres_auth, redis_auth | Изолирована: только auth видит свою БД |
| `profile_db_net` | profile, postgres_profile | Изолирована: только profile видит свою БД |
| `broker_net` | auth, profile, notification, rabbitmq | `internal: true` — без выхода наружу |

### Открытые порты

| Сервис | Внешний порт | Назначение |
|--------|:------------:|-----------|
| nginx | **80** | Единственная публичная точка входа |
| auth | 8000 | Прямой доступ для отладки |
| profile | 8001 | Прямой доступ для отладки |
| postgres_auth | 5432 | DataGrip / миграции |
| postgres_profile | 5433 | DataGrip |
| rabbitmq mgmt | 15672 | RabbitMQ Web UI |
| minio api | 127.0.0.1:9000 | S3 API (loopback) |
| minio console | 127.0.0.1:9001 | MinIO Console (loopback) |

---

## Основные потоки данных (Event-Driven)

### Удаление аккаунта (Account Deletion)

Процесс удаления данных пользователя реализован асинхронно через брокер сообщений для обеспечения консистентности между микросервисами.

```mermaid
sequenceDiagram
    participant User as Пользователь
    participant Auth as Auth Service
    participant RMQ as RabbitMQ
    participant Profile as Profile Service
    participant PG as PostgreSQL
    participant MinIO as MinIO (Storage)

    User->>Auth: DELETE /api/auth/me
    Auth->>Auth: Удаляет учетную запись в DB
    Auth->>RMQ: Публикует AccountDeletedEvent (user_id)
    Auth-->>User: 200 OK (Аккаунт удален)
    
    Note over RMQ, Profile: Асинхронная обработка события
    
    RMQ->>Profile: Доставляет событие AccountDeleted (user_id)
    Profile->>PG: Удаляет профиль по user_id в DB (коммит)
    Profile->>MinIO: Удаляет файлы профиля по user_id (S3) — best-effort
    Note over Profile, MinIO: Если MinIO недоступен — логируется, не блокирует
```

**Поток обработки события:**

1.  **Auth Service** (инициатор): После удаления своей записи публикует событие в RabbitMQ.
2.  **RabbitMQ**: Обеспечивает надежную доставку события в очередь `account_deletion_queue`.
3.  **Profile Service** (обработчик события):
    - Получает событие `AccountDeleted` с `user_id`
    - **Шаг 1**: Удаляет запись профиля в PostgreSQL по `user_id` (коммитит транзакцию)
    - **Шаг 2**: Удаляет файлы аватара и фона из MinIO по `user_id` (best-effort, логирует ошибки, не прерывает процесс)
    
    Разделение на шаги гарантирует консистентность: даже если MinIO недоступен, профиль удален из БД.

---

## Структура проекта

```text
LoreLounge/
├── docs/                        # Общая документация
├── gateway/                     # API Gateway (KrakenD) и Reverse Proxy (Nginx)
│   ├── nginx.conf               # Конфигурация Nginx (reverse proxy :80 → :3000, :8080)
│   ├── krakend/                 # KrakenD API Gateway
│   │   ├── krakend.tmpl.json    # Основной конфиг с шаблонизацией
│   │   └── partials/            # Переиспользуемые шаблоны для каждого сервиса
│   │       ├── auth-public.tmpl      # POST register, login, logout, refresh
│   │       ├── auth-protected.tmpl  # GET /me, DELETE /me, role-requests (JWT required)
│   │       ├── profile-public.tmpl   # GET user/{name} (public profile lookup)
│   │       ├── profile-protected.tmpl # GET/PUT/PATCH /me, /me/upload, /me/ignored (JWT required)
│   │       ├── headers-standard.tmpl # Стандартные заголовки (Content-Type, Authorization)
│   │       ├── headers-post.tmpl     # POST/PUT заголовки + JSON body validation
│   │       └── jwt-validator.tmpl    # Конфиг JWT валидации (RS256)
│   └── README.md                # Документация KrakenD и маршрутизации
├── frontend/                    # Next.js приложение
├── infra/                       # Docker Compose, скрипты, конфиги БД
├── services/                    # Микросервисы
│   ├── auth/                    # [README](services/auth/README.md) — Auth & Roles (FastAPI)
│   ├── profile/                 # [README](services/profile/README.md) — User Profiles (FastAPI)
│   ├── notification/            # [README](services/notification/README.md) — Emails (FastStream)
│   ├── content/                 # [в разработке] Новеллы и главы
│   └── comment/                 # [в разработке] Комментарии
└── Makefile                     # Команды управления проектом
```

### KrakenD структура

**Flexible Configuration** с Go-шаблонизацией:
- `krakend.tmpl.json` — точка входа, подключает партиалы через `{{ template "file.tmpl" . }}`
- `partials/auth-public.tmpl`, `partials/auth-protected.tmpl` — эндпоинты авторизации
- `partials/profile-public.tmpl`, `partials/profile-protected.tmpl` — эндпоинты профиля
- `partials/*protected.tmpl` переиспользуют `headers-*.tmpl` и `jwt-validator.tmpl` через `{{ template }}`

Добавление нового микросервиса: создать `partials/{service}/{public,protected}.tmpl` + добавить import в `krakend.tmpl.json`.

---

## Микросервисы

Подробную информацию о функционале, API и настройках каждого сервиса можно найти в их внутренних документах:

1.  [**Auth Service**](services/auth/README.md) — Регистрация, вход, JWT (RS256), роли, сброс пароля.
2.  [**Profile Service**](services/profile/README.md) — Профили, загрузка аватаров (MinIO), черные списки.
3.  [**Notification Service**](services/notification/README.md) — Отправка email через RabbitMQ.

---

## Быстрый старт

### Требования

- Docker 24+
- Docker Compose 2.20+
- Make

### Шаги

```bash
# 1. Скопировать переменные окружения
cp .env.example .env
cp services/auth/.env.example services/auth/.env
cp services/profile/.env.example services/profile/.env

# 2. Сгенерировать RSA-ключи для JWT
make certs

# 3. Применить миграции БД
make migrate

# 4. Запустить все сервисы
make up
```

После запуска приложение доступно на `http://localhost`.

### Основные команды Make

| Команда | Описание |
|---------|---------|
| `make up` | Запустить все сервисы (сборка при необходимости) |
| `make down` | Остановить все сервисы |
| `make build` | Пересобрать образы без кэша |
| `make logs` | Стримить логи всех сервисов |
| `make ps` | Статус контейнеров |
| `make clean` | Остановить и удалить все volumes |
| `make certs` | Сгенерировать RSA-ключи для JWT |
| `make migrate` | Применить Alembic-миграции (auth) |
| `make migrate-gen MSG="..."` | Создать новую миграцию |

---

## Маршрутизация

### Nginx → сервисы

| Путь | Назначение |
|------|-----------|
| `/api/auth/docs`, `/api/auth/redoc`, `/api/auth/openapi.json` | Swagger auth (напрямую в auth:8000) |
| `/api/profile/docs`, `/api/profile/openapi.json` | Swagger profile (напрямую в profile:8000) |
| `/api/*` | KrakenD API Gateway (krakend:8080) |
| `/media/*` | Статика из MinIO (minio:9000) |
| `/nginx-health` | Health-check Nginx |
| `/*` | Next.js Frontend (frontend:3000) |

### Ограничения на уровне Nginx

- Rate limit применяется для `/api/auth/login`, `/api/auth/register`, `/api/auth/password-reset-request`, `/api/auth/password-reset-confirm`.
- Для `/api/*` и frontend-роутов включены CORS-заголовки.

### Маршруты KrakenD (текущее состояние)

| Группа | Маршруты |
|------|-----------|
| Auth Public | `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/logout`, `POST /api/auth/refresh`, `POST /api/auth/password-reset-request`, `POST /api/auth/password-reset-confirm`, `GET /api/auth/password-reset-check?token=...` |
| Auth Protected (JWT) | `GET /api/auth/me`, `DELETE /api/auth/me`, `POST /api/auth/role-request`, `GET /api/auth/role-requests/`, `POST /api/auth/role-requests/{request_id}/approve`, `POST /api/auth/role-requests/{request_id}/reject`, `POST /api/auth/password-change` |
| Profile Public | `GET /api/profile/user/{name}` |
| Profile Protected (JWT) | `GET /api/profile/me`, `PUT /api/profile/me`, `PATCH /api/profile/me`, `POST /api/profile/me/upload`, `GET /api/profile/me/ignored`, `POST /api/profile/me/ignored/{target_user_id}`, `DELETE /api/profile/me/ignored/{target_user_id}` |

Для protected-эндпоинтов KrakenD валидирует JWT и прокидывает служебные заголовки пользователя (`x-user-id`, `x-user-role`, `x-user-email`) в downstream-сервисы.

### Поток авторизованного запроса

```mermaid
sequenceDiagram
    participant B as Браузер
    participant N as Nginx :80
    participant K as KrakenD :8080
    participant S as Микросервис

    B->>N: GET /api/profile/me<br/>Cookie: access_token=JWT
    N->>K: проксирует запрос
    K->>K: Проверяет подпись JWT (RS256)
    alt Токен валиден
        K->>S: запрос + заголовки<br/>X-User-Id, X-User-Role, X-User-Email
        S-->>B: 200 OK
    else Токен невалиден
        K-->>B: 401 Unauthorized
    end
```

---

## Лицензия

MIT
