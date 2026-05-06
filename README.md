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
flowchart TB
    Browser(["🌐 Браузер"])

    Browser -->|"HTTP :80"| Nginx

    subgraph gateway["🔀 Шлюзы"]
        Nginx["Nginx\n:80"]
        KrakenD["KrakenD\nAPI Gateway\n:8080"]
    end

    subgraph frontend_layer["🖥️ Фронтенд"]
        Frontend["Next.js\n:3000"]
    end

    subgraph services_layer["⚙️ Микросервисы"]
        Auth["auth\nFastAPI :8000"]
        Profile["profile\nFastAPI :8001"]
        Notification["notification\nFastStream"]
    end

    subgraph storage_layer["🗄️ Хранилища"]
        PGAuth["postgres_auth\n:5432"]
        RedisAuth["redis_auth\n:6379"]
        PGProfile["postgres_profile\n:5433"]
        MinIO["MinIO\n:9000"]
    end

    subgraph broker_layer["📨 Брокер"]
        RabbitMQ["RabbitMQ\n:5672"]
    end

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

    RabbitMQ -->|"subscribe"| Notification
    Notification -->|"read media"| MinIO
```

---

## Сетевая изоляция

Каждый сервис видит только те соседей, которые ему нужны.

```mermaid
flowchart LR
    subgraph lorelounge_net["lorelounge_net  (bridge)"]
        Nginx["nginx"]
        KrakenD["krakend"]
        Frontend["frontend"]
        Auth["auth"]
        Profile["profile"]
        Notification["notification"]
        MinIO["minio"]
    end

    subgraph auth_db_net["auth_db_net  (bridge)"]
        Auth2["auth"]
        PGAuth["postgres_auth"]
        RedisAuth["redis_auth"]
    end

    subgraph profile_db_net["profile_db_net  (bridge)"]
        Profile2["profile"]
        PGProfile["postgres_profile"]
    end

    subgraph broker_net["broker_net  (internal)"]
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

## Структура проекта

```text
LoreLounge/
├── docs/                        # Общая документация
├── gateway/                     # API Gateway (KrakenD) и Reverse Proxy (Nginx)
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
| `make clean` | Остановить и удалить все volumes ⚠️ |
| `make certs` | Сгенерировать RSA-ключи для JWT |
| `make migrate` | Применить Alembic-миграции (auth) |
| `make migrate-gen MSG="..."` | Создать новую миграцию |

---

## Маршрутизация

### Nginx → сервисы

| Путь | Назначение |
|------|-----------|
| `/api/auth/docs`, `/api/auth/redoc`, `/api/auth/openapi.json` | Swagger auth (напрямую) |
| `/api/*` | KrakenD API Gateway |
| `/*` | Next.js Frontend |

### Поток авторизованного запроса

```mermaid
sequenceDiagram
    participant B as Браузер
    participant N as Nginx :80
    participant K as KrakenD :8080
    participant S as Микросервис

    B->>N: GET /api/auth/me<br/>Cookie: access_token=JWT
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
