# LoreLounge

LoreLounge (от слов Lore — история, знания вселенной, и Lounge — зона отдыха) — платформа для чтения и каталогизации веб-новелл с умными технологиями.

## Технологический стек

| Уровень | Технология |
|---------|-------------|
| Frontend | Next.js 15, React 19, Tailwind CSS 4 |
| API Gateway | KrakenD (Flexible Configuration) |
| Reverse Proxy | Nginx |
| Auth Service | FastAPI (Python 3.11+) |
| Notification Service | FastStream |
| Database | PostgreSQL 15, Redis 7 |
| Message Queue | RabbitMQ |
| Container | Docker, Docker Compose |

## Архитектура

Система построена на 4 независимых слоя:

```
┌─────────────────────────────────────────────────────────────────┐
│  Слой 1: Внешний (The Front Door)                              │
│  Nginx (:80) → KrakenD (:8080) → Next.js (:3000)              │
├─────────────────────────────────────────────────────────────────┤
│  Слой 2: Микросервисы                                      │
│  auth (:8000), notification (FastStream, только подписка) │
├─────────────────────────────────────────────────────────────────┤
│  Слой 3: Event-Driven                                      │
│  RabbitMQ (:5672)                                           │
├─────────────────────────────────────────────────────────────────┤
│  Слой 4: Хранение                                         │
│  postgres_auth (:5432), redis_auth (:6379)                  │
└─────────────────────────────────────────────────────────────────┘
```

### Сетевая изоляция

- **lorelounge_net**: Nginx, KrakenD, Next.js, сервисы
- **auth_db_net**: auth ↔ postgres_auth, redis_auth
- **broker_net** (internal): auth ↔ notification ↔ RabbitMQ

### Ports Summary

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

## Структура проекта

```
loreLounge/
├── docs/                     # Документация
│   └── architecture.md
├── gateway/                  # Шлюзы
│   ├── nginx.conf            # Nginx — публичная точка входа (:80)
│   └── krakend/             # KrakenD API Gateway (:8080)
│       ├── krakend.tmpl.json # Главный конфиг
│       ├── endpoints/        # Эндпоинты
│       ├── partials/         # Переиспользуемые блоки
│       └── templates/       # Шаблоны
├── frontend/                # Next.js (:3000)
├── services/
│   ├── auth/                # Auth Service (FastAPI :8000)
│   └── notification/        # Notification Service (FastStream)
├── infra/                   # Docker инфраструктура
│   ├── docker-compose.yml
│   ├── postgres/auth/init.sql
│   └── scripts/
└── Makefile
```

### Назначение папок

| Папка | Назначение |
|-------|-------------|
| `docs/` | Документация архитектуры |
| `gateway/` | Конфиги шлюзов (Nginx, KrakenD) |
| `frontend/` | Next.js веб-приложение |
| `services/auth/` | Микросервис авторизации (FastAPI) |
| `services/notification/` | Микросервис уведомлений (FastStream) |
| `infra/` | Docker Compose и SQL скрипты |

## Быстрый старт

### Требования

- Docker 24+
- Docker Compose 2.20+
- Make

### Запуск

```bash
# Собрать и запустить все сервисы
make up

# Остановить
make down
```

### Доступные сервисы

| Сервис | URL | Port |
|--------|-----|------|
| Frontend | http://localhost | 3000 |
| API Gateway | http://localhost/api | 8080 |
| Auth OpenAPI | http://localhost/api/v1/docs | 8000 |
| RabbitMQ UI | http://localhost:15672 | 15672 |

## Gateway поток (Nginx)

```
/api/*       → KrakenD (:8080) → auth (:8000)
/api/v1/docs → auth:8000 (напрямую для Swagger UI)
/*          → Frontend (:3000)
```

- Nginx — единственная публичная точка входа (:80)
- `/api/*` → KrakenD
- `/api/v1/docs`, `/api/v1/redoc`, `/api/v1/openapi.json` → auth напрямую (для Swagger)
- `/*` → Frontend

## API Endpoints

### Auth Service (`/api/v1/`)

| Метод | Путь | Описание |
|-------|------|----------|
| POST | /api/v1/register | Регистрация пользователя |
| POST | /api/v1/login | Вход (устанавливает http-only cookies) |
| POST | /api/v1/logout | Выход (удаляет cookies) |
| GET | /api/v1/me | Текущий пользователь (из JWT payload) |
| POST | /api/v1/role-request | Запрос на смену роли |
| POST | /api/v1/password-reset-request | Запрос сброса пароля |
| POST | /api/v1/password-reset-confirm | Подтверждение сброса пароля |
| GET | /api/v1/.well-known/jwks.json | JWKS для KrakenD |

### Role Requests (`/api/v1/role-requests/`)

| Метод | Путь | Описание |
|-------|------|----------|
| GET | /api/v1/role-requests/ | Список заявок (admin) |
| POST | /api/v1/role-requests/{id}/approve | Одобрить заявку |
| POST | /api/v1/role-requests/{id}/reject | Отклонить заявку |

## Переменные окружения

### frontend

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| LORELOUNGE_API_BASE | URL API Gateway | http://krakend:8080/api |
| PORT | Порт Next.js | 3000 |

### auth

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| CONFIG__DB__URL | PostgreSQL URL | postgresql+asyncpg://... |
| CONFIG__DB__POOL_SIZE | Размер пула соединений | 20 |
| CONFIG__DB__MAX_OVERFLOW | Максимальное переполнение | 10 |
| JWT_SECRET_PATH | Путь к приватному ключу | /app/certs/private_key.pem |
| SMTP_HOST | SMTP сервер | - |
| RABBITMQ_URL | RabbitMQ URL | amqp://guest:guest@rabbitmq:5672/ |

## KrakenD Configuration

Конфиг использует [Flexible Configuration](https://www.krakend.io/docs/flexible-configuration/) для разделения на части:

```
gateway/krakend/
├── krakend.tmpl.json     # Корень с {{ include }}
├── partials/             # Переиспользуемые блоки
│   ├── jwt-validator.json   # JWT валидация
│   └── common-headers.json # Общие заголовки
├── endpoints/            # Эндпоинты
│   ├── auth-public.json    # Публичные
│   └── auth-protected.json # Защищённые
└── templates/           # Шаблоны
    └── backend.json
```

### Публичные эндпоинты (без JWT)
- `/api/auth/register` → auth
- `/api/auth/login` → auth
- `/api/auth/logout` → auth
- `/api/auth/password-reset-request` → auth
- `/api/auth/password-reset-confirm` → auth

### Защищённые эндпоинты (требуют JWT)
- `/api/auth/me` → auth
- `/api/auth/role-request` → auth
- `/api/v1/role-requests/` → auth
- `/api/v1/role-requests/{id}/approve` → auth
- `/api/v1/role-requests/{id}/reject` → auth

**Проверка конфига:**
```bash
docker run -it --rm -v $(pwd)/gateway/krakend:/etc/krakend devopsfaith/krakend:2.5 check -c /etc/krakend/krakend.tmpl.json
```

## Разработка

```bash
# Собрать и запустить все сервисы
make up

# Запуск только фронтенда
cd frontend && npm run dev

# Запуск auth
cd services/auth && uvicorn src.main:app --reload --port 8000

# Запуск notification
cd services/notification && python -m src.main
```

## Лицензия

MIT