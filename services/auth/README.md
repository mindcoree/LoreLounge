# Auth Service

Микросервис аутентификации и авторизации LoreLounge. Реализован с использованием принципов **Clean Architecture**.

## Назначение

- Регистрация и аутентификация пользователей.
- Выдача `access`/`refresh` JWT токенов в http-only cookies.
- Обновление сессий (Refresh Token Rotate).
- Отзыв токенов при выходе (Logout) через Redis.
- Публикация JWKS для валидации токенов на шлюзе (KrakenD).
- Сброс пароля через email-уведомления (RabbitMQ) с таймером валидности.
- Безопасная смена пароля авторизованным пользователем.
- Управление ролями и заявками на изменение прав доступа.

## Технологический стек

- **Ядро**: FastAPI + Pydantic v2 (Settings, Validation).
- **Безопасность**: RS256 JWT, хеширование паролей (bcrypt/argon2).
- **База данных**: PostgreSQL (SQLAlchemy 2.0).
- **Кеширование**: Redis (blacklist токенов, revocation list).
- **Сообщения**: RabbitMQ (Publish/Subscribe для уведомлений).
- **Миграции**: Alembic.

## Структура проекта (Clean Architecture)

```text
auth/src/
├── api/                     # Уровень представления (Delivery)
│   ├── routers/             # Маршруты FastAPI (auth, roles, password)
│   ├── schemas/             # DTO (Pydantic модели для API)
│   ├── dependencies/         # DI (зависимости для эндпоинтов)
│   └── handlers/            # Обработчики доменных исключений -> HTTP
├── domain/                  # Ядро бизнеса (Pure Python)
│   ├── services/            # Бизнес-логика (AuthServices, RoleServices)
│   ├── exceptions/          # Доменные исключения (UserNotFoundError и др.)
│   ├── enums.py             # Перечисления (Roles)
│   └── interfaces.py        # Интерфейсы репозиториев и сервисов
├── infrastructure/           # Реализация внешних зависимостей
│   ├── db/                  # SQLAlchemy модели и репозитории
│   ├── cache/               # Логика работы с Redis
│   └── broker/              # Интеграция с RabbitMQ
├── config/                  # Глобальная конфигурация приложения
└── main.py                  # Точка входа и сборка приложения
```

## API Endpoints (префикс `/api/auth`)

| Метод | Путь | Доступ | Описание |
|-------|------|:------:|---------|
| POST  | `/register` | Public | Регистрация нового аккаунта |
| POST  | `/login` | Public | Вход (установка cookies) |
| POST  | `/logout` | Public | Выход (аннулирование сессии) |
| POST  | `/refresh` | Public | Продление access-токена |
| GET   | `/.well-known/jwks.json` | Public | Публичные ключи для KrakenD |
| GET   | `/me` | JWT | Данные профиля текущего пользователя |
| POST  | `/password-reset-request` | Public | Запрос ссылки на сброс пароля |
| GET   | `/password-reset-check` | Public | Проверка токена и времени жизни |
| POST  | `/password-reset-confirm` | Public | Установка нового пароля по токену |
| POST  | `/password-change` | JWT | Смена пароля (требует текущий) |
| POST  | `/role-request` | JWT | Заявка на получение новой роли |
| GET   | `/role-requests/` | JWT | Просмотр активных заявок |
| POST  | `/role-requests/{id}/approve` | Admin | Утверждение роли |

## Особенности реализации

### Безопасность
- **JWT RS256**: Токены подписываются приватным ключом. Публичный ключ доступен по стандарту JWKS, что позволяет API-шлюзу валидировать запросы без обращения к сервису auth.
- **Revocation List**: При логауте `jti` refresh-токена попадает в Redis (db=0) с TTL, равным сроку жизни токена.

### Сброс пароля
- Токены сброса имеют ограниченный срок жизни (30 минут).
- Фронтенд использует эндпоинт `/password-reset-check` для отображения таймера обратного отсчета до истечения ссылки.

### Redis
Сервис использует **логическую базу данных Redis (db=0)**. Единый Redis-сервер разделяет данные между сервисами через логические БД:
- `db=0` — Auth Service (revocation list токенов)
- `db=1` — Profile Service (кэш, сессии)
- и т.д.

Это обеспечивает изоляцию данных при минимальном потреблении ресурсов.

### Инфраструктура
- Сервис полностью контейнеризирован.
- Логирование настроено через стандартный `logging`.
- Переменные окружения строго типизированы через Pydantic.

## Разработка

1. **Миграции**:
   ```bash
   # Создать миграцию
   alembic revision --autogenerate -m "description"
   # Применить
   alembic upgrade head
   ```

2. **Запуск тестов**:
   ```bash
   pytest
   ```

3. **RSA Ключи**:
   Для работы JWT необходимы `private.pem` и `public.pem` в папке `certs/` (или настроены пути через ENV).

## Переменные окружения

| Переменная | Описание | По умолчанию |
|-----------|----------|--------------|
| `AUTH__REDIS__URL` | URL для подключения к Redis | `redis://:redis_secret@redis:6379/0` |
| `AUTH__DB__*` | Настройки PostgreSQL | см. `.env.example` |
| `AUTH__AUTH__ACCESS_EXPIRE_MIN` | Время жизни access-токена | `15` |
| `AUTH__AUTH__REFRESH_EXPIRE_DAYS` | Время жизни refresh-токена | `7` |