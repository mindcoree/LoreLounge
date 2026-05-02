# LoreLounge — Архитектура (Mermaid диаграммы)

## Структура проекта

```
loreLounge/
├── docs/                     # Документация (этот файл)
├── gateway/                  # Шлюзы
│   ├── nginx.conf            # Nginx — публичная точка входа (:80)
│   └── krakend/               # KrakenD API Gateway (:8080)
│       ├── krakend.tmpl.json  # Главный конфиг
│       ├── endpoints/         # Эндпоинты
│       ├── partials/          # Переиспользуемые блоки
│       └── templates/         # Шаблоны
├── frontend/                 # Next.js (:3000)
├── services/
│   ├── auth/                  # Auth Service (FastAPI :8000)
│   └── notification/          # Notification Service (FastStream)
├── infra/                    # Docker инфраструктура
│   ├── docker-compose.yml
│   └── postgres/auth/init.sql
└── Makefile
```

## 4 слоя системы

```mermaid
flowchart TB
    subgraph Ext["Слой 1: Внешний (The Front Door)"]
        Browser["Браузер<br/>Клиент"]
        Nginx["Nginx<br/>:80"]
        KrakenD["KrakenD<br/>API Gateway<br/>:8080"]
        NextJS["Next.js<br/>Frontend<br/>:3000"]
    end

    subgraph Micro["Слой 2: Микросервисы"]
        Auth["auth<br/>FastAPI<br/>:8000"]
        Notif["notification<br/>FastStream<br/>(подписка)"]
    end

    subgraph Event["Слой 3: Event-Driven"]
        RMQ["RabbitMQ<br/>:5672"]
    end

    subgraph Storage["Слой 4: Хранение"]
        PG["postgres_auth<br/>PostgreSQL 15<br/>:5432"]
        Redis["redis_auth<br/>Redis 7<br/>:6379"]
    end

    Browser -->|"GET /"| Nginx
    Browser -->|"GET /api/*"| Nginx
    Nginx -->|"/*"| NextJS
    Nginx -->|"/api/*"| KrakenD
    KrakenD -->|jwt validation| Auth
    KrakenD -->|"x-user-id,<br/>x-user-role,<br/>x-user-email"| Auth

    Auth -->|"publish"| RMQ
    RMQ -->|"subscribe"| Notif

    Auth -->|"SELECT/INSERT"| PG
    Auth -->|"GET/SET"| Redis
```

## Ports Summary

| Сервис | Port | Назначение |
|--------|------|-------------|
| nginx | 80 | Публичный вход (единственный) |
| krakend | 8080 | API Gateway |
| frontend | 3000 | Next.js |
| auth | 8000 | Auth Service |
| rabbitmq | 5672 | AMQP |
| rabbitmq (mgmt) | 15672 | RabbitMQ UI |
| postgres_auth | 5432 | PostgreSQL |
| redis_auth | 6379 | Redis |

## Сетевая изоляция

```mermaid
flowchart TB
    subgraph Public["Публичная сеть (порт 80)"]
        NginxP["nginx"]
    end

    subgraph Lorelounge["lorelounge_net"]
        Nginx["nginx"]
        KrakenD["krakend<br/>:8080"]
        NextJS["frontend<br/>:3000"]
        Auth["auth<br/>:8000"]
        Notif["notification"]
    end

    subgraph AuthDB["auth_db_net"]
        PGA["postgres_auth<br/>:5432"]
        RDSA["redis_auth<br/>:6379"]
    end

    subgraph Broker["broker_net (internal)"]
        RMQ["rabbitmq<br/>:5672"]
    end

    Public --> Nginx
    Nginx -->|"/*"| NextJS
    Nginx -->|"/api/*"| KrakenD
    KrakenD --> Auth
    Auth -->|"publish"| RMQ
    Notif -->|"subscribe"| RMQ
    Auth --> PGA
    Auth --> RDSA
```

### Сетевая изоляция (сервисы)

| Network | Сервисы | Доступ |
|---------|---------|--------|
| `lorelounge_net` | nginx, krakend, frontend, auth, notification | Внутри Docker |
| `auth_db_net` | postgres_auth, redis_auth | Только auth |
| `broker_net` (internal) | rabbitmq | Только сервисы |

## Поток авторизованного запроса

```mermaid
sequenceDiagram
    participant B as Браузер
    participant N as Nginx :80
    participant K as KrakenD :8080
    participant A as auth :8000

    B->>N: GET /api/auth/me<br/>Cookie: access_token=JWT

    N->>K: GET /api/auth/me<br/>Cookie: access_token=JWT

    K->>K: Проверить подпись JWT<br/>RS256 + public_key.pem

    alt Токен валиден
        K->>K: Извлечь claims из payload:<br/>sub, role, email
        K->>A: GET /api/v1/me<br/>X-User-Id: xxx<br/>X-User-Role: user<br/>X-User-Email: email
        A-->>K: {id, email, role}<br/>(из JWT payload)
        K-->>N: {id, email, role}
        N-->>B: {id, email, role}
    else Токен невалиден
        K-->>N: 401 Unauthorized
        N-->>B: 401 Unauthorized
    end
```

**Примечание:** `/api/v1/me` НЕ обращается к БД — данные берутся напрямую из JWT payload.

## Поток регистрации + async email

```mermaid
sequenceDiagram
    participant B as Браузер
    participant N as Nginx :80
    participant K as KrakenD :8080
    participant A as auth :8000
    participant PG as postgres_auth :5432
    participant RMQ as RabbitMQ :5672
    participant Notif as notification

    B->>N: POST /api/auth/register<br/>{email, password}
    N->>K: POST /api/auth/register
    K->>A: POST /api/v1/register
    A->>PG: INSERT INTO users
    PG-->>A: OK
    A->>RMQ: publish: password_reset_queue<br/>{to_email, reset_link}
    RMQ-->>A: ACK
    A-->>K: {message: success}
    K-->>N: {message: success}
    N-->>B: {message: success}

    RMQ->>Notif: deliver message
    Notif->>Notif: Отправить email
```

**Примечание:** Nginx также проксирует `/api/v1/docs` → `auth:8000` напрямую для Swagger UI.

## Диаграмма Docker сетей

```mermaid
flowchart LR
    subgraph Docker["Docker Compose"]
        subgraph Networks["Сети"]
            Net1["lorelounge_net"]
            Net2["auth_db_net"]
            Net3["broker_net"]
        end

        subgraph Services["Сервисы"]
            Nginx["nginx<br/>:80"]
            KrakenD["krakend<br/>:8080"]
            NextJS["frontend<br/>:3000"]
            Auth["auth<br/>:8000"]
            Notif["notification"]
            PG["postgres_auth<br/>:5432"]
            Redis["redis_auth<br/>:6379"]
            RMQ["rabbitmq<br/>:5672"]
        end

        Nginx --> Net1
        KrakenD --> Net1
        NextJS --> Net1
        Auth --> Net1
        Notif --> Net1

        Auth --> Net2
        PG --> Net2
        Redis --> Net2

        Auth --> Net3
        Notif --> Net3
        RMQ --> Net3
    end
```

## Gateway поток (Nginx)

```
/api/*       → KrakenD (:8080)
/api/v1/docs → auth:8000 ( напрямую для Swagger )
/*          → Frontend (:3000)
```

## KrakenD Endpoints

### Публичные (без JWT)
- `/api/auth/register` → auth
- `/api/auth/login` → auth
- `/api/auth/logout` → auth
- `/api/auth/password-reset-request` → auth
- `/api/auth/password-reset-confirm` → auth

### Защищённые (требуют JWT)
- `/api/auth/me` → auth
- `/api/auth/role-request` → auth
- `/api/v1/role-requests/` → auth
- `/api/v1/role-requests/{id}/approve` → auth
- `/api/v1/role-requests/{id}/reject` → auth