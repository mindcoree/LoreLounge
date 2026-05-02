# LoreLounge

LoreLounge (от слов Lore — история, знания вселенной, и Lounge — зона отдыха) — это современная платформа для чтения и каталогизации веб-новелл. Место, где удобный интерфейс встречается с умными технологиями: собирайте собственные библиотеки, обсуждайте сюжетные повороты и читайте эксклюзивные переводы, созданные с помощью нейросетей.

## Технологический стек

| Уровень | Технология |
|---------|-------------|
| Frontend | Next.js 15, React 19, Tailwind CSS 4 |
| API Gateway | KrakenD |
| Reverse Proxy | Nginx |
| Auth Service | FastAPI (Python 3.11+) |
| Notification | FastStream |
| Database | PostgreSQL 15, Redis 7 |
| Message Queue | RabbitMQ |
| Container | Docker, Docker Compose |

## Архитектура

Система построена на 4 независимых слоях:

```
┌─────────────────────────────────────────────────────────────┐
│  Слой 1: Входная группа                                  │
│  Nginx (:80) → KrakenD (:8080) → Next.js (:3000)            │
├─────────────────────────────────────────────────────────────┤
│  Слой 2: Микросервисы                                    │
│  auth (:8000), notification-service (:8001)                  │
├─────────────────────────────────────────────────────────────┤
│  Слой 3: Event-Driven                                    │
│  RabbitMQ (async messaging)                              │
├─────────────────────────────────────────────────────────────┤
│  Слой 4: Хранение                                        │
│  postgres_auth, redis_auth                               │
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
├── gateway/              # Nginx, KrakenD конфиги
├── frontend/            # Next.js приложение
├── services/
│   ├── auth/            # auth (FastAPI)
│   └── notification/    # notification-service (FastStream)
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

### Аутентификация

| Метод | Путь | Описание |
|-------|------|----------|
| POST | /api/auth/register | Регистрация |
| POST | /api/auth/login | Вход |
| POST | /api/auth/logout | Выход |
| GET | /api/auth/me | Текущий пользователь |
| POST | /api/auth/password-reset-request | Запрос сброса пароля |
| POST | /api/auth/password-reset-confirm | Подтверждение сброса |

### Роли

| Метод | Путь | Описание |
|-------|------|----------|
| POST | /api/auth/role-request | Запрос на роль |
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

| Переменная | Описание |
|------------|----------|
| CONFIG__DB__URL | PostgreSQL URL |
| JWT_SECRET_PATH | Путь к приватному ключу |
| SMTP_HOST | SMTP сервер |
| RABBITMQ_URL | RabbitMQ URL |

## Разработка

```bash
# Запуск только фронтенда в режиме разработки
cd frontend && npm run dev

# Запуск auth
cd services/auth && uvicorn src.main:app --reload
```

## Лицензия

MIT