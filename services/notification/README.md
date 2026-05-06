# Notification Service

Микросервис отправки уведомлений LoreLounge.

## Назначение

- Отправка email-уведомлений (сброс пароля, приветствие и т.д.).
- Асинхронная обработка задач из очереди RabbitMQ.

## Технологический стек

- **Ядро**: FastStream (для работы с брокерами сообщений).
- **Брокер**: RabbitMQ.
- **Протокол**: SMTP для отправки почты.

## Структура папок

```text
notification/
├── src/
│   ├── core/            # config.py
│   ├── domain/          # Схемы сообщений
│   │   └── notification/ # schemas.py (PasswordResetNotification)
│   ├── infrastructure/  # Внешние реализации
│   │   ├── broker/      # rabbitmq.py
│   │   └── email/       # smtp.py
│   └── main.py          # Точка входа и обработчики (FastStream)
├── Dockerfile           # Инструкции для сборки
└── requirements.txt     # Зависимости Python
```

## Обработчики (Subscribers)

| Очередь | Модель сообщения | Описание |
|---------|------------------|----------|
| `password_reset_queue` | `PasswordResetNotification` | Отправка письма со ссылкой на сброс пароля |

## Конфигурация (.env)

| Переменная | Описание |
|------------|---------|
| `SMTP_HOST` | Хост SMTP сервера |
| `SMTP_PORT` | Порт SMTP сервера |
| `SMTP_USER` | Логин SMTP |
| `SMTP_PASSWORD` | Пароль SMTP |
| `SMTP_FROM` | Email отправителя |
| `RABBITMQ_URL` | Адрес RabbitMQ |

## Запуск (Docker)

```bash
# из корня проекта
make up
```
