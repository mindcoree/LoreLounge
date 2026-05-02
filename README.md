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
┌─────────────────────────────────────────────────────────────┐
│  Слой 1: Входная группа                                  │
│  Nginx (:80) → KrakenD (:8080) → Next.js (:3000)            │
├─────────────────────────────────────────────────────────────┤
│  Слой 2: Микросервисы                                    │
│  auth (:8000), notification (:8001)                       │
├─────────────────────────────────────────────────────────────┤
│  Слой 3: Event-Driven                                    │
│  RabbitMQ                                               │
├─────────────────────────────────────────────────────────────┤
│  Слой 4: Хранение                                        │
│  postgres_auth, redis_auth                              │
└─────────────────────────────────────────────────────────────┘
```

### Сетевая изоляция

- **lorelounge_net**: Nginx, KrakenD, Next.js, сервисы
- **auth_db_net**: auth ↔ postgres_auth, redis_auth
- **broker_net** (internal): auth ↔ notification ↔ RabbitMQ

## Структура проекта

```
loreLounge/
├── docs/                  # Документация
├── gateway/              # Nginx, KrakenD конфиг
│   ├── nginx.conf
│   ├── krakend.json
│   └── krakend/          # Flexible Configuration
│       ├── partials/     # Переиспользуемые блоки
│       ├── endpoints/    # Эндпоинты
│       └── templates/   # Шаблоны
├── frontend/            # Next.js приложение
├── services/
│   ├── auth/            # Auth Service (FastAPI)
│   └── notification/    # Notification Service (FastStream)
├── infra/               # Docker Compose, скрипты
└── Makefile
```

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

| Сервис | URL |
|--------|-----|
| Frontend | http://localhost |
| API Gateway | http://localhost/api |
| Auth OpenAPI | http://localhost/api/v1/docs |
| RabbitMQ UI | http://localhost:15672 |

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
├── krakend.json          # Корень с $import
├── partials/             # Переиспользуемые блоки
│   ├── jwt-validator.json
│   └── common-headers.json
├── endpoints/            # Эндпоинты
│   ├── auth-public.json
│   └── auth-protected.json
└── templates/           # Шаблоны
    └── backend.json
```

**Проверка конфига:**
```bash
krakend check -c gateway/krakend.json
krakend audit -c gateway/krakend.json
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